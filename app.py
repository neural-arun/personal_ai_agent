from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from api import router

app = FastAPI(
    title="Personal Career Agent",
    version="1.0.0"
)

# include routes
app.include_router(router)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    # Render provides the port in the PORT env var; default to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)