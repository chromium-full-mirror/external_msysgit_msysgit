#!/bin/bash

# This is a 'copy and run' wrapper for the actual implementation script.
#
# Running a copy of the script avoids issues from git deleting or checking out
# different versions of the script when switching branches.

set -ex

cd "$(dirname "$0")"
BASENAME="$(basename "$0")"
IMPL="$(basename "$0").impl"
cp "$IMPL" "tmp.$BASENAME"
exec "tmp.$BASENAME"
