import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response

from app.api.image_routes import router as image_router
from app.api.video_routes import router as video_router
from app.core.config import Settings
from app.core.model_loader import load_detector


def create_app(settings=None, detector_factory=load_detector):
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        app.state.settings = settings
        # Lifespan runs once per worker, never once per request.
        app.state.detector = detector_factory(settings.model_path)
        yield
        del app.state.detector

    app = FastAPI(title="PPEGuard API", version="1.0.0", lifespan=lifespan)
    app.include_router(image_router)
    app.include_router(video_router)

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="docs")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    @app.get("/files/{job_id}/{filename}", name="download_artifact", tags=["Downloads"])
    def download_artifact(job_id: str, filename: str):
        if not re.fullmatch(r"[0-9a-f]{32}", job_id) or filename not in {
            "annotated.jpg", "annotated.mp4", "report.json", "report.csv"
        }:
            raise HTTPException(404, "Artifact not found.")
        path = settings.output_dir / job_id / filename
        if not path.is_file() or not (path.parent / ".ready").is_file():
            raise HTTPException(404, "Artifact not found.")
        return FileResponse(path, filename=filename)

    return app


app = create_app()
