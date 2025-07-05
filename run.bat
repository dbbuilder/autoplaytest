@echo off
REM Working batch file to run AutoPlayTest with proper paths

cd /d D:\Dev2\autoplaytest

REM Set PYTHONPATH to include src directory
set PYTHONPATH=D:\Dev2\autoplaytest\src

REM Run as a module from the project root
D:\Dev2\autoplaytest\venv\Scripts\python.exe -m simple_runner %*
