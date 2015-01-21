@echo off
setlocal
set PATH=%~dp0@@GITDIR@@\cmd;%PATH%
"%~dp0@@GITDIR@@\cmd\ssh-keygen.cmd" %*
