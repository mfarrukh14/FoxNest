@echo off
REM Installation verification script for FoxNest

echo ========================================
echo FoxNest Installation Verification
echo ========================================
echo.

echo Testing fox command...
fox --version
if errorlevel 1 (
    echo ✗ fox command not found
    echo Please check that FoxNest is properly installed and in your PATH
    goto :error
) else (
    echo ✓ fox command works
)

echo.
echo Testing fox-server command...
where fox-server >nul 2>&1
if errorlevel 1 (
    echo ✗ fox-server command not found
    goto :error
) else (
    echo ✓ fox-server command found
)

echo.
echo Testing basic fox functionality...
fox help >nul 2>&1
if errorlevel 1 (
    echo ✗ fox help failed
    goto :error
) else (
    echo ✓ fox help works
)

echo.
echo ========================================
echo ✓ FoxNest installation verified!
echo ========================================
echo.
echo You can now use:
echo   fox init --username yourname --repo-name myproject
echo   fox add filename.txt
echo   fox commit -m "Initial commit"
echo   fox-server (to start the server)
echo.
echo For more help: fox help
goto :end

:error
echo.
echo ========================================
echo ✗ Installation verification failed
echo ========================================
echo.
echo Troubleshooting steps:
echo 1. Make sure you ran the installer as administrator
echo 2. Restart your command prompt or computer
echo 3. Check if the installation directory is in your PATH
echo 4. Try reinstalling FoxNest
echo.

:end
pause
