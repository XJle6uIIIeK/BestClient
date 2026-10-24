@echo off
setlocal EnableExtensions

set BUILD_DIR=build-ui-redesign
set DIST_DIR=dist-ui-redesign

echo [1/4] Updating submodules...
git submodule update --init --recursive
if errorlevel 1 goto :fail

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

echo [2/4] Configuring x64 Release...
cmake -S . -B "%BUILD_DIR%" -A x64 -DCMAKE_BUILD_TYPE=Release -DDISCORD=OFF -DTOOLS=OFF -DAUTOUPDATE=OFF -DVULKAN=ON -DDOWNLOAD_GTEST=OFF -DCMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE=.
if errorlevel 1 goto :fail

echo [3/4] Building BestClient...
cmake --build "%BUILD_DIR%" --config Release --target everything --parallel 2
if errorlevel 1 goto :fail

echo [4/4] Packaging EXE + data...
cmake --build "%BUILD_DIR%" --config Release --target package_default
if errorlevel 1 goto :fail

for /R "%BUILD_DIR%" %%F in (*.zip) do copy /Y "%%F" "%DIST_DIR%\" >nul

echo.
echo Done. Packaged build is in %DIST_DIR%\
echo If no ZIP was produced, use %BUILD_DIR%\Release output together with the repository data folder.
exit /b 0

:fail
echo.
echo Build failed. See the error above.
exit /b 1
