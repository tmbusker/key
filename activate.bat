echo off

pushd %~dp0
call venv_kee\Scripts\Activate.bat
set "path=%path%;%~dp0batch"
popd
