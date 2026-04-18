@echo off
title Story Game Studio
cls

echo Checking for Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit
)

echo Installing dependencies...
python -m pip install pygame customtkinter pillow --quiet

echo Launching Studio...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Studio crashed. Check your main.py for errors.
    pause
)