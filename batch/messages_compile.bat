echo off
setlocal EnableExtensions enabledelayedexpansion 

call "%~dp0messages_common.bat" %1 %2
if errorlevel 1 goto :eof

echo msgfmt -o %mo_file% %po_file%
msgfmt -o %mo_file% %po_file%

endlocal