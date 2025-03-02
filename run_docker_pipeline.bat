@echo off
echo Starting ETL pipeline in Docker...

REM Check if .env file exists, if not create from example
if not exist .env (
    if exist .env.example (
        echo Creating .env file from .env.example...
        copy .env.example .env
        echo Please update the .env file with your MongoDB connection string.
        echo Press Enter to continue or Ctrl+C to exit and update .env first.
        pause
    ) else (
        echo ERROR: .env.example file not found.
        exit /b 1
    )
)

REM Build and run with docker-compose
docker-compose up --build

REM Check exit status
if %ERRORLEVEL% EQU 0 (
    echo Pipeline completed. View results in the ./data directory.
) else (
    echo Pipeline failed. Check logs for errors.
)
