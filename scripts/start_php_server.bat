@echo off
cd /d "%~dp0.."

if exist "C:\xampp\php\php.exe" (
  echo Starting Gemma4 demo with XAMPP PHP...
  echo Open http://127.0.0.1:8080 in your browser.
  "C:\xampp\php\php.exe" -S 127.0.0.1:8080 router.php
) else (
  echo XAMPP PHP was not found at C:\xampp\php\php.exe
  echo Please install XAMPP or add PHP to PATH, then run:
  echo php -S 127.0.0.1:8080 router.php
  pause
)
