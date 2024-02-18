echo off

pushd %~dp0
cd ..\busker\file\photo
echo %cd%

pyinstaller --onefile --noconsole --add-data "locale/Japanese_Japan/LC_MESSAGES/*.mo;locale/Japanese_Japan/LC_MESSAGES" organizer.py

popd