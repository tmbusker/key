echo off
setlocal enabledelayedexpansion

pushd %~dp0
call messages_common.bat

cd ..
@REM xgettext --language=Python --output=locale/photo_collector.pot photo_collector.py
for /r %%i in (*.py) do (
    echo Processing file: %%i
    xgettext --language=Python --output=%pot_file% %%i
)

msginit --locale=%locale% --input=%pot_file% --output=%po_file%
del /q %pot_file%

:END
popd
endlocal
