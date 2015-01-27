#!/bin/bash

# Collection of common utility functions for msysgit bash scripts.

die() {
  RET=$?
  if [ $RET -eq 0 ]; then
    RET=1
  fi
  echo "$*" >&2
  exit $RET
}

verify_msys() {
  if [ ! -f /THIS_IS_MSYSGIT ]; then
    die "
    Please run this script in an msysgit development environment.
    See https://github.com/msysgit/msysgit/wiki/InstallMSysGit"
  fi
}

start_and_wait() {
  # Run a command, wait for it to finish, and check that it was successful.
  # Note that in DOS, "if errorlevel #" actually means "if errorlevel >= #", so
  # when #=1, it captures all failure return values (i.e. anything but 0).
  start //wait "$@" \&\& if errorlevel 1 \(exit %%errorlevel%%\)
}

verify_clean_git() {
  RET=0
  CHECKDIR=${1:-$PWD}
  cd "$CHECKDIR" >/dev/null
  git diff --no-patch --exit-code HEAD || RET=$?
  if [ $RET -ne 0 ]; then
    echo "You have unsaved changes in '$PWD'."
    die "Please commit (and ideally push upstream) any unsaved changes."
  fi
  cd - >/dev/null
}
