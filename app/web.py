from fastapi import FastAPI

app = FastAPI(title="Control SuperPanel")


@app.get("/")
def root():
    return {
        "name": "control",
        "ui": "ok",
        "next": ["/health"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
