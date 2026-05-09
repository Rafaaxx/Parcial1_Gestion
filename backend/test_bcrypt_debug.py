from passlib.hash import bcrypt

# Test short password
try:
    h = bcrypt.hash("pwd")
    print("Short password OK:", h[:20])
except Exception as e:
    print("Short password ERROR:", str(e)[:100])

# Test email
try:
    h2 = bcrypt.hash("a1@t.co")
    print("Email hash OK")
except Exception as e:
    print("Email hash ERROR:", str(e))

# Test if the issue is in the fixture setup
try:
    h3 = bcrypt.hash("abc" * 30)  # 90 bytes
    print("Long password OK")
except Exception as e:
    print("Long password ERROR:", str(e)[:80])
