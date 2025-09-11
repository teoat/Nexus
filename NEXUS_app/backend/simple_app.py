#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
"""

from fastapi import FastAPI
import uvicorn


@app.get("/")
async def root():
    return {"message": "🚀 Nexus Platform is running!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nexus-platform"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
