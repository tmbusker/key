echo off

pushd %~dp0
cd ..\busker\file\photo
echo %cd%

pyinstaller --onefile --noconsole --add-data "locale/ja_JP/LC_MESSAGES/*.mo;locale/ja_JP/LC_MESSAGES" organizer.py

popd