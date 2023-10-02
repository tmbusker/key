echo off

pushd %~dp0
call messages_common.bat

cd ..
msgfmt -o %mo_file% %po_file%
popd
