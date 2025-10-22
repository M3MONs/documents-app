from fastapi import FastAPI

app = FastAPI()

@app.get("/status")
def get_status() -> dict[str, str]:
    return {"status": "ok"}