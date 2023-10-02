import pytest
import os
import tempfile
from datetime import date, datetime
from busker.file import utils


# Pytest function to test the get_file_type method
def test_get_file_type():
    # Test image file types
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    for ext in image_extensions:
        file_name = f"image_file{ext}"
        assert utils.FileType.get_file_type(file_name) == utils.FileType.IMAGE

    # Test video file types
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    for ext in video_extensions:
        file_name = f"video_file{ext}"
        assert utils.FileType.get_file_type(file_name) == utils.FileType.VIDEO

    # Test unknown file type
    assert utils.FileType.get_file_type('unknown_file.txt') == utils.FileType.UNKNOWN


def test_get_image_capture_datetime():
    assert utils.FileType.get_file_type('screenshot20231009.png') == utils.FileType.IMAGE
    # file not exists
    assert utils.get_image_capture_datetime('screenshot20231009.png') is None

    file = os.path.join(os.path.dirname(__file__), 'screenshot20231009.png')
    assert utils.FileType.get_file_type(file) == utils.FileType.IMAGE
    # the file has no original datetime
    assert utils.get_image_capture_datetime(file) is None

    file = os.path.join(os.path.dirname(__file__), 'IMG_20190417_114435.jpg')
    assert utils.FileType.get_file_type(file) == utils.FileType.IMAGE
    shooting_datetime = utils.get_image_capture_datetime(file)
    assert shooting_datetime == '2019:04:17 11:44:37'


def test_parameterize_query():
    # Test case with a date parameter
    query1 = "SELECT * FROM table WHERE date_column = ?"
    parameters1 = [date(2023, 1, 15)]
    result1 = utils.parameterize_query(query1, parameters1)
    expected_result1 = "SELECT * FROM table WHERE date_column = '2023/01/15'"
    assert result1 == expected_result1

    # Test case with a datetime parameter
    query2 = "INSERT INTO table (datetime_column) VALUES (?)"
    parameters2 = [datetime(2023, 1, 15, 12, 30, 0)]
    result2 = utils.parameterize_query(query2, parameters2)
    expected_result2 = "INSERT INTO table (datetime_column) VALUES ('2023/01/15 12:30:00')"
    assert result2 == expected_result2

    # Test case with multiple parameters
    query3 = "UPDATE table SET column1 = ?, column2 = ? WHERE id = ?"
    parameters3 = [42, 'value', date(2023, 1, 15)]
    result3 = utils.parameterize_query(query3, parameters3)
    expected_result3 = "UPDATE table SET column1 = 42, column2 = 'value' WHERE id = '2023/01/15'"
    assert result3 == expected_result3

    # Test case with null parameters
    query4 = "UPDATE table SET column1 = ?, column2 = ? WHERE id = ?"
    parameters4 = [42, None, date(2023, 1, 15)]
    result4 = utils.parameterize_query(query4, parameters4)
    expected_result4 = "UPDATE table SET column1 = 42, column2 = NULL WHERE id = '2023/01/15'"
    assert result4 == expected_result4


def test_read_all_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        batch_size = 2
        # Create some test files
        with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
            f.write('file1')
        with open(os.path.join(temp_dir, 'file2.txt'), 'w') as f:
            f.write('file2')
        with open(os.path.join(temp_dir, 'file3.txt'), 'w') as f:
            f.write('file3')
        expected_output = [
            [(temp_dir, 'file1.txt'), (temp_dir, 'file2.txt')],
            [(temp_dir, 'file3.txt')]
        ]
        output = list(utils.read_all_files(temp_dir, batch_size))
        assert output == expected_output


def test_read_all_files_with_nonexistent_directory():
    with tempfile.TemporaryDirectory() as temp_dir:     # noqa
        assert list(utils.read_all_files('nonexistent_directory', 2)) == []


def test_read_all_files_with_file_as_directory():
    with tempfile.NamedTemporaryFile() as temp_file:
        assert list(utils.read_all_files(temp_file.name, 2)) == []


def test_read_all_files_with_subdirectories():
    with tempfile.TemporaryDirectory() as temp_dir:
        batch_size = 2
        
        # Create some test files and subdirectories
        with open(os.path.join(temp_dir, 'file1.txt'), 'w') as f:
            f.write('file1')
        with open(os.path.join(temp_dir, 'file2.txt'), 'w') as f:
            f.write('file2')
        os.mkdir(os.path.join(temp_dir, 'subdir'))
        with open(os.path.join(temp_dir, 'subdir', 'file3.txt'), 'w') as f:
            f.write('file3')
        
        subdir = os.path.join(temp_dir, 'subdir')
        expected_output = [
            [(temp_dir, 'file1.txt'), (temp_dir, 'file2.txt')],
            [(subdir, 'file3.txt')]
        ]
        
        output = list(utils.read_all_files(temp_dir, batch_size))
        
        assert output == expected_output
