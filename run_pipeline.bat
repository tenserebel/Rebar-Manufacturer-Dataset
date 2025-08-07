@echo off
setlocal enabledelayedexpansion

REM Rebar Manufacturer Dataset Pipeline - Batch Script
REM This script automates the entire workflow for Windows users

REM Initialize variables
set "SKIP_VENV="
set "SKIP_INSTALL="
set "SKIP_EXTRACTION="
set "SKIP_COMBINE="
set "SKIP_MAIN="

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="-SkipVenv" set "SKIP_VENV=1"
if /i "%~1"=="-SkipInstall" set "SKIP_INSTALL=1"
if /i "%~1"=="-SkipExtraction" set "SKIP_EXTRACTION=1"
if /i "%~1"=="-SkipCombine" set "SKIP_COMBINE=1"
if /i "%~1"=="-SkipMain" set "SKIP_MAIN=1"
if /i "%~1"=="-h" goto :show_help
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-?" goto :show_help
shift
goto :parse_args

:show_help
echo Rebar Manufacturer Dataset Pipeline
echo.
echo Usage: run_pipeline.bat [options]
echo.
echo Options:
echo   -SkipVenv       Skip virtual environment setup
echo   -SkipInstall    Skip dependency installation
echo   -SkipExtraction Skip data extraction scripts
echo   -SkipCombine    Skip CSV combination
echo   -SkipMain       Skip main processing
echo.
echo Examples:
echo   run_pipeline.bat                    # Run complete pipeline
echo   run_pipeline.bat -SkipVenv          # Skip venv setup
echo   run_pipeline.bat -SkipExtraction    # Skip data extraction
echo.
exit /b 0

:main
echo.
echo ============================================================
echo 🚀 Starting Rebar Manufacturer Dataset Pipeline
echo ============================================================
echo Project root: %CD%
echo Platform: Windows
echo.

REM Check prerequisites
call :write_step "Prerequisites Check" "Verifying required files and Python installation"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    exit /b 1
)
echo ✅ Python is installed

REM Check required files
set "MISSING_FILES="
if not exist "requirements.txt" set "MISSING_FILES=1"
if not exist "Data Extraction\Cares.py" set "MISSING_FILES=1"
if not exist "Data Extraction\Eurometal.py" set "MISSING_FILES=1"
if not exist "combine_csv.py" set "MISSING_FILES=1"
if not exist "main.py" set "MISSING_FILES=1"

if defined MISSING_FILES (
    echo ❌ Missing required files:
    if not exist "requirements.txt" echo    - requirements.txt
    if not exist "Data Extraction\Cares.py" echo    - Data Extraction\Cares.py
    if not exist "Data Extraction\Eurometal.py" echo    - Data Extraction\Eurometal.py
    if not exist "combine_csv.py" echo    - combine_csv.py
    if not exist "main.py" echo    - main.py
    exit /b 1
)

echo ✅ All required files found

REM Setup virtual environment
if not defined SKIP_VENV (
    call :write_step "Virtual Environment Setup" "Creating/checking virtual environment"
    
    if exist "venv" (
        echo ✅ Virtual environment already exists
    ) else (
        echo Creating virtual environment...
        call :run_command "python -m venv venv" "Creating virtual environment"
        if errorlevel 1 exit /b 1
    )
)

REM Install requirements
if not defined SKIP_INSTALL (
    call :write_step "Install Dependencies" "Installing Python packages from requirements.txt"
    
    call :run_command "venv\Scripts\pip.exe install -r requirements.txt" "Installing dependencies"
    if errorlevel 1 exit /b 1
)

REM Run data extraction
if not defined SKIP_EXTRACTION (
    call :write_step "Data Extraction" "Running Cares.py and Eurometal.py extraction scripts"
    
    echo --- Running Cares.py ---
    call :run_command "venv\Scripts\python.exe \"Data Extraction\Cares.py\"" "Running Cares.py"
    if errorlevel 1 exit /b 1
    
    echo --- Running Eurometal.py ---
    call :run_command "venv\Scripts\python.exe \"Data Extraction\Eurometal.py\"" "Running Eurometal.py"
    if errorlevel 1 exit /b 1
)

REM Combine CSV files
if not defined SKIP_COMBINE (
    call :write_step "Combine CSV Files" "Running combine_csv.py to merge all data"
    
    call :run_command "venv\Scripts\python.exe combine_csv.py" "Combining CSV files"
    if errorlevel 1 exit /b 1
)

REM Run main processing
if not defined SKIP_MAIN (
    call :write_step "Main Processing" "Running main.py for final data processing"
    
    if not exist "Combined_Company_Data.csv" (
        echo ❌ Combined CSV file not found
        echo Skipping main.py execution
    ) else (
        call :run_command "venv\Scripts\python.exe main.py Combined_Company_Data.csv" "Running main processing"
        if errorlevel 1 exit /b 1
    )
)

REM Success message
echo.
echo ============================================================
echo 🎉 PIPELINE COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo Generated files:
echo - Company Data/ (directory with individual CSV files)
echo - Combined_Company_Data.csv (merged dataset)
echo - Rebar Manufacturers.csv (final processed dataset)
echo.
exit /b 0

REM Function to print step headers
:write_step
echo.
echo ============================================================
echo STEP: %~1
if not "%~2"=="" echo DESCRIPTION: %~2
echo ============================================================
echo.
goto :eof

REM Function to run command with error handling
:run_command
echo Running: %~1
if not "%~2"=="" echo Description: %~2

%~1
if errorlevel 1 (
    echo ❌ Command failed: %~1
    exit /b 1
) else (
    echo ✅ Command completed successfully
)
goto :eof 