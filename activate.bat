echo off

pushd %~dp0
call venv\Scripts\Activate.bat
set "path=%path%;%~dp0batch"
popd
