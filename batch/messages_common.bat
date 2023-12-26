echo off

REM Check for command-line arguments
if "%1"=="" (
    echo Usage : %~0 app_path [locale]
    echo         app_path relative to project base directory
    echo Usage Sample1 : %~0 busker\photo ja_JP
    echo Usage Sample2 : %~0 busker\photo
    exit /b 1
)

if "%2"=="" (
    set locale=ja_JP
) else (
    set locale=%2
)

pushd %~dp0
cd ..
set "app_path=!cd!\%1"
popd

set "locale_base=%app_path%\locales"
set "locale_path=%locale_base%\%locale%\LC_MESSAGES"

set "pot_file=%locale_base%\messages.pot"
set "po_file=%locale_path%\messages.po"
set "mo_file=%locale_path%\messages.mo"

echo pot_file=%pot_file%
echo po_file=%po_file%
echo mo_file=%mo_file%