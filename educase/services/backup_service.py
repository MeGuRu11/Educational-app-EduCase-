# services/backup_service.py
import os
import shutil
import datetime
import zipfile
from typing import Tuple


class BackupService:
    def __init__(self, db_path: str = "educase.db", backup_dir: str = "backups", media_dir: str = "assets/media"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.media_dir = media_dir
        
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_full_backup(self) -> Tuple[bool, str]:
        """Создает ZIP архив с базой данных и папкой media."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"educase_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Добавляем БД
                if os.path.exists(self.db_path):
                    zipf.write(self.db_path, os.path.basename(self.db_path))
                
                # Добавляем медиа файлы
                if os.path.exists(self.media_dir):
                    for root, dirs, files in os.walk(self.media_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(self.media_dir))
                            zipf.write(file_path, arcname)
                            
            return True, backup_path
        except Exception as e:
            return False, str(e)
