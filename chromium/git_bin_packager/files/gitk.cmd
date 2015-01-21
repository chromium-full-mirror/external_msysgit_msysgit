@rem Do not use "echo off" to not affect any child calls.
@setlocal

@rem Get the abolute path to the parent directory, which is assumed to be the
@rem Git installation root.
@for /F "delims=" %%I in ("%~dp0..") do @set git_install_root=%%~fI
@set PATH=%git_install_root%\bin;%git_install_root%\mingw\bin;%PATH%

:: Set the HOME variable to depot_tools (the parent of this directory's parent).
@if not exist "%HOME%" @for /F "delims=" %%I in ("%~dp0..\..") do @set HOME=%%~fI

@start "gitk" wish.exe "%git_install_root%\bin\gitk" -- %*
