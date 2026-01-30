from fastapi import FastAPI

app = FastAPI(title="Digital Library API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Digital Library API"}
