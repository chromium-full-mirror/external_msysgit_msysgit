@rem Do not use "echo off" to not affect any child calls.
@setlocal

@rem Get the abolute path to the parent directory, which is assumed to be the
@rem Git installation root.
@for /F "delims=" %%I in ("%~dp0..") do @set git_install_root=%%~fI
@set PATH=%git_install_root%\bin;%git_install_root%\mingw\bin;%PATH%

:: Set the HOME variable to depot_tools (the parent of this directory's parent).
@if not exist "%HOME%" @for /F "delims=" %%I in ("%~dp0..\..") do @set HOME=%%~fI

:: Set up default SSH directory for this user in their home directory.
@if not exist "%HOME%\.ssh" @mkdir "%HOME%\.ssh"
@if not exist "%HOME%\.ssh\config" (
  echo Installing default ssh_config ...
  @copy "%~dp0..\ssh_config" "%HOME%\.ssh\config" >nul
)

:default
@ssh.exe -F "%HOME%\.ssh\config" %*
@set ErrorLevel=%ErrorLevel%
@goto quit

:quit
@"%COMSPEC%" /c exit /b %ErrorLevel%
