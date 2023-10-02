import os
import hashlib
from PIL import Image
from datetime import datetime
import logging
from typing import List, Optional


logger = logging.getLogger("busker.file.sql")
logger.setLevel(logging.INFO)
logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)


class FileType:
    IMAGE = 'image'
    VIDEO = 'video'
    UNKNOWN = 'unknown'

    @classmethod
    def create(cls, file_name) -> str:
        file_extension = os.path.splitext(file_name)[1]
        if file_extension.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'):
            return cls.IMAGE
        elif file_extension.lower() in ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'):
            return cls.VIDEO
        else:
            return cls.UNKNOWN


class FileInfo:
    block_size = 8192

    def __init__(self,
                 id: Optional[int],
                 name: str,
                 path: str,
                 size: int,
                 hash: str,
                 created_at: datetime,
                 modified_at: datetime,
                 file_type: str,
                 captured_at: Optional[datetime],
                 save_to: str) -> None:
        if name is None or path is None:
            raise TypeError("Both 'name' and 'path' parameters are required.")
        self.id = id
        self.name = name
        self.path = path
        self.size = size
        self.hash = hash
        self.created_at = created_at
        self.modified_at = modified_at
        self.file_type = file_type
        self.captured_at = captured_at
        self.save_to = save_to

    @property
    def full_name(self) -> str:
        return os.path.join(self.path, self.name)

    def get_relative_path(self, relative_root: str) -> str:
        if relative_root[-1] != os.path.sep:
            relative_root += os.path.sep
        return self.path.replace(relative_root, '')

    @classmethod
    def create(cls, name: str, path: str) -> 'FileInfo':
        """ファイルからFileInfoを生成する"""
        full_name = os.path.join(path, name)
        size = os.path.getsize(full_name)

        hash = None
        with open(full_name, "rb") as f:
            md5_hash = hashlib.md5()
            for byte_block in iter(lambda: f.read(cls.block_size), b""):
                md5_hash.update(byte_block)
            hash = md5_hash.hexdigest()

        created_at = datetime.fromtimestamp(os.path.getctime(full_name))
        modified_at = datetime.fromtimestamp(os.path.getmtime(full_name))
        file_type = FileType.create(name)

        captured_at = modified_at
        if file_type == FileType.IMAGE:
            try:
                with Image.open(full_name) as img:
                    exif = img.getexif()
                    if exif:
                        datetime_str = exif.get(0x9003)
                        captured_at = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")    # type: ignore
            except Exception:
                pass
        
        save_to = datetime.strftime(captured_at, "%Y" + os.path.sep + "%m")
        return FileInfo(None,
                        name,
                        path,
                        size,
                        hash,
                        created_at,
                        modified_at,
                        file_type,
                        captured_at,
                        save_to)


def read_all_files(directory: str, batch_size: int) -> List[List[FileInfo]]:
    file_infos: List[FileInfo] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_infos.append(FileInfo.create(file, root))
            if len(file_infos) >= batch_size:
                yield file_infos
                file_infos = []

    # Check if there are remaining files in the last batch
    if file_infos:
        yield file_infos
