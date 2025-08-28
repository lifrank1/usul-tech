#!/usr/bin/env python3
"""
Simple script to run the SOF Week Speaker Recommendation Engine backend server.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
