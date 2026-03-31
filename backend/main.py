import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from db import close_pool, init_pool
from routers.demotable_router import router as demotable_router
from routers.ml_router import router as ml_router
from routers.translator_router import router as translator_router
from routers.auth_router import router as auth_router

load_dotenv()

app = FastAPI(title="CPSC304 Python Backend")
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_pool()


@app.on_event("shutdown")
def on_shutdown() -> None:
    close_pool()


app.include_router(demotable_router)
app.include_router(ml_router)
app.include_router(translator_router)
app.include_router(auth_router)

@app.get("/", include_in_schema=False)
def serve_frontend_root():
    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Run './scripts/build-frontend.sh' first.",
    )


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    if full_path in {"favicon.ico"}:
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.exists():
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="File not found")

    requested_path = FRONTEND_DIST_DIR / full_path
    if requested_path.exists() and requested_path.is_file():
        return FileResponse(requested_path)

    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Run './scripts/build-frontend.sh' first.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
