import logging
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def process_upload(request, file, confidence, service, extensions):
    """Stage uploads with generated names; publish only finished artifacts."""
    settings = request.app.state.settings
    name = (file.filename or "upload").replace("\\", "/").split("/")[-1]
    suffix = Path(name).suffix.lower()
    job_id = uuid4().hex
    destination = settings.output_dir / job_id
    source = destination / ("upload" + suffix)
    succeeded = False
    try:
        if suffix not in extensions:
            raise HTTPException(415, "Unsupported file extension.")
        destination.mkdir(parents=True)
        size = 0
        with source.open("wb") as stream:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_bytes:
                    raise HTTPException(413, "Upload exceeds the 100 MiB limit.")
                stream.write(chunk)
        if not size:
            raise HTTPException(400, "The uploaded file is empty.")
        annotated, report = service(source, destination, request.app.state.detector, confidence, name)
        (destination / ".ready").touch()
        succeeded = True
        return {
            "job_id": job_id,
            "report": report,
            "files": {key: str(request.url_for("download_artifact", job_id=job_id, filename=filename))
                      for key, filename in {"annotated": annotated, "json_report": "report.json", "csv_report": "report.csv"}.items()},
        }
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Detection failed for job %s", job_id)
        raise HTTPException(500, "Detection failed; see server logs.") from exc
    finally:
        file.file.close()
        if succeeded:
            source.unlink(missing_ok=True)
        elif destination.exists():
            shutil.rmtree(destination)
