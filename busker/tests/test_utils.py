import os
import gettext
import logging
from busker.utils import init_i18n, init_logging


def test_init_i18n():
    localedir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'photo', 'locales')
    init_i18n('messages', localedir)
    assert gettext.gettext('Close') == '閉じる'


def test_logging():
    init_logging('test_utils.log', logging.INFO, 'utf-8')

    logger = logging.getLogger("busker.test_utils")
    logger.setLevel(logging.INFO)
    logger.info('test logging')
    assert logger.name == 'busker.test_utils'
