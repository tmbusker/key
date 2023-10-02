import gettext
import logging


def init_i18n(app: str, localedir: str, language: str) -> None:     # pragma: no cover
    """多言語対応の初期化、localedirはlocaleフォルダーの絶対パス"""
    lang = gettext.translation('messages', localedir=localedir, languages=[language])
    lang.install()


def init_logging(file_name: str, level, encoding: str) -> None:        # pragma: no cover
    """log出力の初期化"""
    logging.basicConfig(level=level)
    file_handler = logging.FileHandler(file_name, encoding=encoding)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Remove any existing handlers to ensure logs are not duplicated
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(file_handler)
