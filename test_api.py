from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "API is running", "message": "Simple test API"}

@app.get("/test")
async def test_endpoint():
    return {"test": "working", "port": 8001}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
