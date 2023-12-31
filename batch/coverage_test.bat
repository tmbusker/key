echo off
@REM setlocal EnableExtensions EnableDelayedExpansion

@REM showing coverage without report
pytest --cov=cmm --cov-config=.coveragerc

@REM generating report
pytest --cov=cmm --cov-report=html:htmlcov --cov-config=.coveragerc
