import gettext
import logging
import locale


def init_i18n(domain: str, localedir: str) -> None:
    """多言語対応の初期化、localedirはlocaleフォルダーの絶対パス"""
    lang, _ = locale.getlocale()
    print(locale.getlocale())

    # Bind the text domain to the specified directory
    gettext.bindtextdomain(domain, localedir)

    # Set the text domain
    gettext.textdomain(domain)
    
    # Create and install the translation
    _translation = gettext.translation(domain, localedir=localedir, languages=[lang], fallback=True)  # type: ignore
    _translation.install()


def init_logging(file_name: str, level, encoding: str) -> None:
    """log出力の初期化"""
    logging.basicConfig(level=level)
    file_handler = logging.FileHandler(file_name, encoding=encoding)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Remove any existing handlers to ensure logs are not duplicated
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(file_handler)
