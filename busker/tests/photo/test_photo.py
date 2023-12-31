import pytest
import os
from datetime import datetime
from busker.photo.file_info import FileType, FileInfo


class TestFileType:
    def test_image(self):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        for ext in image_extensions:
            file_name = f"image_file{ext}"
            assert FileType.create(file_name) == FileType.IMAGE

    def test_video(self):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        for ext in video_extensions:
            file_name = f"video_file{ext}"
            assert FileType.create(file_name) == FileType.VIDEO

    def test_unknown(self):
        assert FileType.create('unknown_file.txt') == FileType.UNKNOWN

    def test_no_extension(self):
        assert FileType.create('unknown_file') == FileType.UNKNOWN
        assert FileType.create('unknown_file.') == FileType.UNKNOWN


class TestFileInfo:
    def test_init(self):
        now = datetime.now()
        file_info = FileInfo(0, 'name', 'c:\\temp', 100, '3324a', now, now, 'image', None, 'c:\\temp')
        assert file_info.name == 'name'
        assert file_info.path == 'c:\\temp'
        assert file_info.hash == '3324a'
        assert file_info.created_at == now
        assert file_info.modified_at == now
        assert file_info.file_type == FileType.IMAGE
        assert file_info.captured_at is None
        assert file_info.save_to == 'c:\\temp'

    def test_init_except(self):
        now = datetime.now()
        with pytest.raises(TypeError, match="Both 'name' and 'path' parameters are required."):
            FileInfo(0, None, 'c:\\temp', 100, '3324a', now, now, 'image', None, 'c:\\temp')

        with pytest.raises(TypeError, match="Both 'name' and 'path' parameters are required."):
            FileInfo(0, '', 'c:\\temp', 100, '3324a', now, now, 'image', None, 'c:\\temp')
            
        with pytest.raises(TypeError, match="Both 'name' and 'path' parameters are required."):
            FileInfo(0, 'name', None, 100, '3324a', now, now, 'image', None, 'c:\\temp')

        with pytest.raises(TypeError, match="Both 'name' and 'path' parameters are required."):
            FileInfo(0, 'name', '', 100, '3324a', now, now, 'image', None, 'c:\\temp')

    def test_create_except(self):
        name = 'screenshot20231009.png'
        path = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.datetime(2023, 12, 25, 9, 20, 30, 825352)

        file_info = FileInfo.create(name, path)
        assert file_info.name == name
        assert file_info.path == path
        assert file_info.hash == '5952a66a8be9d8f8a2b991f01c2349fd'
        assert file_info.created_at == timestamp
        assert file_info.modified_at == timestamp
        assert file_info.file_type == FileType.IMAGE
        assert file_info.captured_at == timestamp
        assert file_info.save_to == '2023\\12'

