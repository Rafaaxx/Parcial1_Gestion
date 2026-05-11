#!/usr/bin/env python
"""Run backend with correct Python path"""

import sys
from pathlib import Path

# Add backend to path so imports work
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load .env
from dotenv import load_dotenv
env_file = backend_path / ".env"
load_dotenv(env_file)

# Now run uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
