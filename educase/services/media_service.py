# services/media_service.py
import os
import shutil
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4

from models.media import Media
from repositories.media_repo import MediaRepository


class MediaService:
    def __init__(self, session: Session, upload_dir: str = "assets/media"):
        self.session = session
        self.media_repo = MediaRepository(session)
        self.upload_dir = upload_dir
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, source_path: str, uploader_id: int, case_id: Optional[int] = None, task_id: Optional[int] = None) -> Media:
        """
        Копирует файл из source_path во внутреннюю директорию и создает запись в БД.
        В реальном приложении здесь стоит добавить валидацию (разрешенные расширения, размер) 
        и сжатие изображений через Pillow.
        """
        filename = os.path.basename(source_path)
        ext = os.path.splitext(filename)[1]
        
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid4().hex}{ext}"
        destination_path = os.path.join(self.upload_dir, unique_filename)
        
        # Копируем файл
        shutil.copy2(source_path, destination_path)
        
        size_bytes = os.path.getsize(destination_path)
        
        new_media = Media(
            filename=filename,
            file_path=destination_path,
            content_type="application/octet-stream", # В идеале определять MIME-тип
            size_bytes=size_bytes,
            uploaded_by_id=uploader_id,
            case_id=case_id,
            task_id=task_id
        )
        return self.media_repo.add(new_media)
