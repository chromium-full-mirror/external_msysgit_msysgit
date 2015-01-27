#!/bin/bash

set -e

if [ "$VERBOSE" ]; then
  set -x
fi

cd "$(dirname "$0")"
SCRIPTDIR="$(pwd -P)"
. "$SCRIPTDIR/shell_utils.sh"

verify_msys

cd "$(git rev-parse --show-toplevel)"
TOPDIR="$(pwd -P)"

# Make sure depot_tools is available for running python and gsutil later.
PYTHON="cmd //c python.bat"
$PYTHON --version 2>/dev/null \
  && which gsutil.py >/dev/null \
  || die "Please add depot_tools to your PATH for python and gsutil."
GSUTIL="$(which gsutil.py)"

cd "$TOPDIR"
echo "Verifying checkouts are clean..."
verify_clean_git git
verify_clean_git

echo "Building git..."
start_and_wait "$TOPDIR/bin/bash.exe" --login -i -c \
  "cd /git && make clean && make && make install" \
  || die "Failed to build a new version of git!"


GITVER=$(cat "$TOPDIR/git/version")
echo "Creating 'portable' msysgit package..."
"$TOPDIR/share/WinGit/portable-release.sh" $GITVER

echo "Creating msysgit depot_tools package..."
PACKAGERDIR=$SCRIPTDIR/git_bin_packager
$PYTHON $PACKAGERDIR/git_bin_packager.py -f "$HOME/PortableGit-$GITVER.7z" \
  -r $GITVER

echo "Pushing package to cloud storage..."
PACKAGE=git-${GITVER}_bin.zip
BUCKET=chrome-infra
$PYTHON "$GSUTIL" cp -n "$PACKAGERDIR/$PACKAGE" "gs://$BUCKET/$PACKAGE"
$PYTHON "$GSUTIL" chacl -g AllUsers:R "gs://$BUCKET/$PACKAGE"
echo
echo "Package is available at:"
echo "https://commondatastorage.googleapis.com/$BUCKET/$PACKAGE"
echo
