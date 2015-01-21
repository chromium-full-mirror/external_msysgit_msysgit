@echo off
setlocal
if DEFINED EDITOR goto rungit
set EDITOR=win32pad
set PATH=%~dp0@@GITDIR@@\win32pad;%PATH%

:rungit
set PATH=%~dp0@@GITDIR@@\cmd;%PATH%
"%~dp0@@GITDIR@@\cmd\git.cmd" %*
