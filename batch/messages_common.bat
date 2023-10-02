echo off

set locale=ja
set app=photo_collector

set locale_base=locale
set locale_path=%locale_base%\%locale%\LC_MESSAGES
if not exist %locale_path% mkdir %locale_path%

set pot_file=%locale_base%\%app%.pot
set po_file=%locale_path%\%app%.po
set mo_file=%locale_path%\%app%.mo
