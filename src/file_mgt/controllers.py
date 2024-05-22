import io
import os
from typing import List
import zipfile
import sys
import uuid
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from sqlalchemy import select

from .schema import FileRecord, UploadInstance


sys.path.append("/src")
from db_setup import SessionLocal

UPLOAD_DIR = "uploads"

# os.makedirs(UPLOAD_DIR, exist_ok=True)
router = APIRouter()


@router.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    instance_uuid = str(uuid.uuid4())
    instance_dir = os.path.join(UPLOAD_DIR, instance_uuid)
    os.makedirs(instance_dir, exist_ok=True)  # Create a directory for this instance

    db_instance = UploadInstance(instance_id=instance_uuid)
    with SessionLocal() as session:
        session.add(db_instance)
        session.commit()

        for file in files:
            file_path = os.path.join(instance_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())

            db_file = FileRecord(
                filename=file.filename,
                file_path=file_path,
                upload_instance_id=db_instance.id,
            )
            session.add(db_file)

        session.commit()

    return {
        "instance_id": instance_uuid,
        "filenames": [file.filename for file in files],
    }


@router.get("/download/{instance_id}")
async def download_files(instance_id: str):
    with SessionLocal() as session:
        stmt = select(UploadInstance).where(UploadInstance.instance_id == instance_id)
        result = session.execute(stmt)
        upload_instance = result.scalars().first()

        if not upload_instance:
            raise HTTPException(status_code=404, detail="Instance not found")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_record in upload_instance.files:
                zip_file.write(file_record.file_path, file_record.filename)

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename={instance_id}.zip"},
        )
