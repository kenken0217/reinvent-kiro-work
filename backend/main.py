from fastapi import FastAPI

app = FastAPI(title="Backend API")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
