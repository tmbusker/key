import gettext
import logging
import locale


def init_i18n(domain: str, localedir: str) -> None:     # pragma: no cover
    """多言語対応の初期化、localedirはlocaleフォルダーの絶対パス"""
    lang, _ = locale.getdefaultlocale()
    print(locale.getdefaultlocale())

    # Bind the text domain to the specified directory
    gettext.bindtextdomain(domain, localedir)

    # Set the text domain
    gettext.textdomain(domain)
    
    # Create and install the translation
    _translation = gettext.translation(domain, localedir=localedir, languages=[lang], fallback=True)  # type: ignore
    _translation.install()
    
    print('Installed domain:', gettext._current_domain)     # type: ignore
    print('Installed languages:', gettext.find(domain, localedir=localedir))
    print('Installed languages:', gettext.find(domain, localedir=localedir, languages=[lang]))      # type: ignore
    print('close', gettext.gettext('Close'))


def init_logging(file_name: str, level, encoding: str) -> None:        # pragma: no cover
    """log出力の初期化"""
    logging.basicConfig(level=level)
    file_handler = logging.FileHandler(file_name, encoding=encoding)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Remove any existing handlers to ensure logs are not duplicated
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(file_handler)
