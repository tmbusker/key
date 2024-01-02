import pytest
import os
from datetime import datetime
from busker.photo.file_info import FileType, FileInfo, read_all_files


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

    def test_create_captured_at(self):
        name = 'IMG_20190417_114435.jpg'
        path = os.path.dirname(os.path.abspath(__file__))

        file_info = FileInfo.create(name, path)
        assert file_info.id is None
        assert file_info.name == name
        assert file_info.path == path
        assert file_info.hash == '1578d32ce770118aa4193374c4837eff'
        assert file_info.created_at == datetime(2023, 12, 25, 9, 20, 30, 823322)
        assert file_info.modified_at == datetime(2023, 12, 25, 9, 20, 30, 824315)
        assert file_info.file_type == FileType.IMAGE
        assert file_info.captured_at == datetime(2019, 4, 17, 11, 44, 37)
        assert file_info.save_to == '2019\\04'

    def test_create_without_captured_at(self):
        name = 'screenshot20231009.png'
        path = os.path.dirname(os.path.abspath(__file__))

        file_info = FileInfo.create(name, path)
        assert file_info.id is None
        assert file_info.name == name
        assert file_info.path == path
        assert file_info.hash == '5952a66a8be9d8f8a2b991f01c2349fd'
        assert file_info.created_at == datetime(2023, 12, 25, 9, 20, 30, 825352)
        assert file_info.modified_at == datetime(2023, 12, 25, 9, 20, 30, 825352)
        assert file_info.file_type == FileType.IMAGE
        assert file_info.captured_at is None
        assert file_info.save_to == '2023\\12'

    def test_create_non_image(self):
        name = 'test_photo.py'
        path = os.path.dirname(os.path.abspath(__file__))

        file_info = FileInfo.create(name, path)
        assert file_info.id is None
        assert file_info.name == name
        assert file_info.path == path
        assert file_info.file_type == FileType.UNKNOWN
        assert file_info.captured_at is None

    def test_create_except(self):
        with pytest.raises(TypeError):
            FileInfo.create('screenshot20231009.png', None)

        with pytest.raises(TypeError):
            FileInfo.create(None, os.path.dirname(os.path.abspath(__file__)))

        with pytest.raises(FileNotFoundError):
            FileInfo.create('screenshot20231009.png', '.')

    def test_full_name(self):
        name = 'screenshot20231009.png'
        path = os.path.dirname(__file__)
        file_info = FileInfo.create(name, path)
        assert file_info.full_name == os.path.join(os.path.dirname(path), 'photo', name)

    def test_relative(self):
        name = 'screenshot20231009.png'
        path = os.path.dirname(__file__)
        file_info = FileInfo.create(name, path)

        assert file_info.get_relative_path(os.path.dirname(os.path.dirname(__file__))) == 'photo'


def test_read_all_files():
    source_path = os.path.dirname(__file__)
    file_count = 4

    batch_size = 5
    for file_infos in read_all_files(source_path, batch_size=batch_size):
        assert len(file_infos) == file_count

    batch_size = 3
    for file_infos in read_all_files(source_path, batch_size=batch_size):
        if len(file_infos) >= batch_size:
            assert len(file_infos) == batch_size
        else:
            assert len(file_infos) == file_count % batch_size
