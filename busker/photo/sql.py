import logging
from datetime import datetime, date
from numbers import Number
from typing import Any, Iterable, List, Optional
from busker.photo.file_info import FileInfo


logger = logging.getLogger("busker.file.sql")
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


def parameterize_query(query: str, parameters: Optional[Iterable[Any]] = None) -> str:
    """パラメータを代入したSQL文を返す"""

    if parameters is None:
        return query

    for parameter in parameters:
        index = query.find('?')
        if index != -1:
            if isinstance(parameter, datetime):
                parameter = "'" + parameter.strftime('%Y/%m/%d %H:%M:%S') + "'"
            elif isinstance(parameter, date):
                parameter = "'" + parameter.strftime('%Y/%m/%d') + "'"
            elif isinstance(parameter, Number):
                parameter = str(parameter)
            elif parameter:
                parameter = "'" + parameter + "'"
            else:
                parameter = 'NULL'

            prefix = query[:index]
            suffix = query[index + 1:]
            query = prefix + parameter + suffix
    return query


def exec_query(conn, query: str, parameters: Optional[Iterable[Any]] = None):
    """Execute the SQL"""

    logger.debug(parameterize_query(query, parameters))
    cursor = conn.cursor()
    if parameters:
        cursor.execute(query, parameters)
    else:
        cursor.execute(query)
    return cursor


def create_table_file_info(conn) -> None:
    """Create tables(sqlite3)"""

    query = '''
            CREATE TABLE IF NOT EXISTS file_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT not null,
                path TEXT not null,
                size INTEGER,
                hash TEXT,
                created_at DATETIME,
                modified_at DATETIME,
                file_type TEXT,
                captured_at DATETIME,
                save_to TEXT,
                UNIQUE (save_to, name),
                UNIQUE (size, hash, captured_at)
            )
        '''
    exec_query(conn, query)


def get_count(conn):
    """file_infoテーブルの件数を取得する"""

    query = 'SELECT count(1) FROM file_info'
    cursor = exec_query(conn, query)
    return cursor.fetchone()[0]


def get_file_by_save_to__name(conn, save_to: str, name: str) -> List['FileInfo']:
    """相対パスと名称を条件に、登録済みファイル情報を検索する"""

    query = 'SELECT * FROM file_info WHERE save_to = ? AND name = ?'
    parameters = (save_to, name)
    cursor = exec_query(conn, query, parameters)
    results = cursor.fetchall()

    if results:
        columns = [desc[0] for desc in cursor.description]
        return [FileInfo(**dict(zip(columns, row))) for row in results]

    return []


def get_same_file(conn, file_info: FileInfo) -> Optional[FileInfo]:
    """ファイル情報（サイズ、hash、撮影日時）を条件に、登録済みファイル情報を検索する"""

    query = 'SELECT * FROM file_info WHERE size = ? AND hash = ? AND captured_at = ?'
    parameters = (file_info.size, file_info.hash, file_info.captured_at)
    cursor = exec_query(conn, query, parameters)
    result = cursor.fetchone()

    if result:
        return FileInfo(*result)
    else:
        return None


def register_file_info(conn, file_info: FileInfo) -> None:
    """Insert a new record to the table file_info"""
    
    query = 'insert into file_info (name, path, size, hash, created_at, modified_at, file_type, captured_at, \
             save_to) values (?, ?, ?, ?, ?, ?, ?, ?, ?)'

    parameters = (file_info.name,
                  file_info.path,
                  file_info.size,
                  file_info.hash,
                  file_info.created_at,
                  file_info.modified_at,
                  file_info.file_type,
                  file_info.captured_at,
                  file_info.save_to)
    exec_query(conn, query, parameters)
