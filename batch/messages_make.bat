echo off
setlocal EnableExtensions enabledelayedexpansion 

call "%~dp0messages_common.bat" %1 %2
if errorlevel 1 goto :eof

if not exist "%locale_path%" mkdir "%locale_path%"

cd %app_path%
@REM xgettext --language=Python --output=locale/photo_collector.pot photo_collector.py
for /r %%i in (*.py) do (
    echo Processing file: %%i
    xgettext --language=Python --from-code=UTF-8 --output=%pot_file% %%i
    @REM xgettext --language=Python --from-code=cp932 --output=%pot_file% %%i
)

if not exist %po_file% (
    echo msginit --locale=%locale% --input=%pot_file% --output=%po_file%
    msginit --locale=%locale% --input=%pot_file% --output=%po_file%
) else (
    echo msgmerge -U %po_file% %pot_file%
    msgmerge -U %po_file% %pot_file%
)

:END
@REM del /q %pot_file%

endlocal
