echo off
@REM setlocal EnableExtensions EnableDelayedExpansion

@REM showing coverage without report
@REM pytest --cov=busker --cov-config=.coveragerc

@REM generating report
pytest --cov=busker --cov-report=html:htmlcov --cov-config=.coveragerc
