import gettext
import os


def init_i18n(app, locale):
    lang = gettext.translation(app, localedir='locale', languages=[locale])
    lang.install()


def _(message):
    return message
