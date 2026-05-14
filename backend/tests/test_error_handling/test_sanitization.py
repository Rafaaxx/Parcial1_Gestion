"""Tests for input sanitization functions"""

import pytest
from pydantic import BaseModel

from app.sanitization import (
    escape_html,
    sanitize_string,
    sanitize_dict,
    sanitize_pydantic_model_fields,
    DEFAULT_SANITIZE_FIELDS,
)


class TestEscapeHtml:
    """Tests for HTML escaping function"""
    
    def test_escapes_script_tag(self):
        """Should escape <script> tags"""
        result = escape_html("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_escapes_img_tag_with_onerror(self):
        """Should escape img tags - < and > are escaped, breaking the tag"""
        result = escape_html('<img src=x onerror=alert(1)>')
        # The < and > are escaped, which breaks the HTML tag
        # This makes it safe as the browser won't interpret it as a tag
        assert "&lt;img" in result
        assert "&gt;" in result
    
    def test_escapes_double_quotes(self):
        """Should escape double quotes"""
        result = escape_html('test "quoted" text')
        assert "&quot;quoted&quot;" in result
    
    def test_escapes_single_quotes(self):
        """Should escape single quotes"""
        result = escape_html("test 'quoted' text")
        assert "&#x27;quoted&#x27;" in result
    
    def test_escapes_ampersand(self):
        """Should escape ampersands"""
        result = escape_html("test & more")
        assert "&amp;" in result
    
    def test_escapes_less_than(self):
        """Should escape < character"""
        result = escape_html("a < b")
        assert "&lt;" in result
    
    def test_escapes_greater_than(self):
        """Should escape > character"""
        result = escape_html("a > b")
        assert "&gt;" in result
    
    def test_preserves_plain_text(self):
        """Should not modify plain text"""
        result = escape_html("plain text without special chars")
        assert result == "plain text without special chars"
    
    def test_handles_empty_string(self):
        """Should handle empty string"""
        result = escape_html("")
        assert result == ""


class TestSanitizeString:
    """Tests for sanitize_string function"""
    
    def test_returns_none_for_none(self):
        """Should return None for None input"""
        result = sanitize_string(None)
        assert result is None
    
    def test_sanitizes_string(self):
        """Should sanitize string"""
        result = sanitize_string("<script>alert(1)</script>")
        assert "<script>" not in result
    
    def test_converts_to_string(self):
        """Should convert non-string to string then sanitize"""
        result = sanitize_string(123)
        assert result == "123"
    
    def test_handles_empty_string(self):
        """Should handle empty string"""
        result = sanitize_string("")
        assert result == ""


class TestSanitizeDict:
    """Tests for sanitize_dict function"""
    
    def test_sanitizes_all_string_values(self):
        """Should sanitize all string values by default"""
        data = {
            "name": "<script>alert(1)</script>",
            "description": "Normal text",
        }
        
        result = sanitize_dict(data)
        
        assert "<script>" not in result["name"]
        assert result["description"] == "Normal text"
    
    def test_preserves_non_string_values(self):
        """Should preserve non-string values"""
        data = {
            "name": "test",
            "count": 42,
            "active": True,
            "price": 19.99,
        }
        
        result = sanitize_dict(data)
        
        assert result["count"] == 42
        assert result["active"] is True
        assert result["price"] == 19.99
    
    def test_sanitizes_specific_keys(self):
        """Should only sanitize specified keys"""
        data = {
            "name": "<script>alert(1)</script>",
            "email": "<img onerror=alert(1) src=x>",
        }
        
        result = sanitize_dict(data, keys_to_sanitize=["name"])
        
        # name should be sanitized
        assert "<script>" not in result["name"]
        # email should NOT be sanitized (not in keys_to_sanitize)
        assert "<img" in result["email"]
    
    def test_handles_nested_dict(self):
        """Should sanitize nested dictionaries"""
        data = {
            "user": {
                "name": "<b>John</b>",
                "bio": "Normal bio",
            }
        }
        
        result = sanitize_dict(data)
        
        assert "&lt;b&gt;" in result["user"]["name"]
        assert result["user"]["bio"] == "Normal bio"
    
    def test_handles_list_values(self):
        """Should sanitize strings in lists"""
        data = {
            "tags": ["<script>", "normal", "<img>"],
        }
        
        result = sanitize_dict(data)
        
        assert "&lt;script&gt;" in result["tags"][0]
        assert result["tags"][1] == "normal"
        assert "&lt;img&gt;" in result["tags"][2]
    
    def test_returns_empty_dict_for_empty_input(self):
        """Should handle empty dict"""
        result = sanitize_dict({})
        assert result == {}


class TestSanitizePydanticModel:
    """Tests for Pydantic model sanitization"""
    
    def test_sanitizes_specified_fields(self):
        """Should sanitize specified fields in model"""
        
        class UserCreate(BaseModel):
            name: str
            email: str
            age: int
        
        user = UserCreate(name="<script>alert(1)</script>", email="test@example.com", age=25)
        sanitize_pydantic_model_fields(user, fields=["name"])
        
        assert "<script>" not in user.name
        # email should not be sanitized (not in fields list)
        assert "@" in user.email
        assert user.age == 25
    
    def test_uses_default_fields(self):
        """Should use DEFAULT_SANITIZE_FIELDS when no fields specified"""
        
        class UserForm(BaseModel):
            name: str
            email: str
        
        user = UserForm(name="<b>John</b>", email="test@example.com")
        sanitize_pydantic_model_fields(user)
        
        assert user.name == "&lt;b&gt;John&lt;/b&gt;"
        # email is in DEFAULT_SANITIZE_FIELDS so should be sanitized
        assert "@" in user.email  # email still valid after sanitization


class TestDefaultSanitizeFields:
    """Tests for default sanitize fields list"""
    
    def test_contains_common_user_fields(self):
        """Should contain common user input fields"""
        expected_fields = [
            "name",
            "description",
            "address",
            "calle",
            "ciudad",
            "barrio",
            "observaciones",
            "titulo",
            "contenido",
            "email",
        ]
        
        for field in expected_fields:
            assert field in DEFAULT_SANITIZE_FIELDS