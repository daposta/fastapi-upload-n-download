from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from sqlalchemy.orm import relationship
import sys
import uuid

sys.path.append("src")
from db_setup import Base, engine


class UploadInstance(Base):
    __tablename__ = "upload_instances"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    instance_id = Column(
        String, unique=True, default=lambda: str(uuid.uuid4()), index=True
    )
    files = relationship("FileRecord", back_populates="upload_instance")


class FileRecord(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String, index=True)
    file_path = Column(String)  # Store the path to the file
    upload_instance_id = Column(String, ForeignKey("upload_instances.id"))
    upload_instance = relationship("UploadInstance", back_populates="files")


Base.metadata.create_all(bind=engine)
