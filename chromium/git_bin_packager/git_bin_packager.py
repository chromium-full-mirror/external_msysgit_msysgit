#!/usr/bin/python
# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


import io
import optparse
import os
import platform
import re
import shutil
import signal
import stat
import sys
import tempfile
import urllib
import urlparse


# The Git scripts call these exes directly, so we keep them in our distribution.
LIBEXEC_EXEMPT_LIST = [
  'git-clone.exe',
  'git-fetch.exe',
  'git-merge-base.exe',
  'git-merge-file.exe',
  'git-merge-index.exe',
  'git-merge-ours.exe',
  'git-merge-recursive.exe',
  'git-merge-subtree.exe',
  'git-merge-tree.exe',
  'git-merge.exe',
  'git-rev-parse.exe',
  'git-unpack-file.exe',
]
SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
WIN32PAD_FILE = 'win32pad.zip'
WIN32PAD_URL = 'http://www.gena01.com/win32pad/win32pad_1_5_10_4.zip'
BOOTSTRAP_FILES = [
  # (source file, destination path in archive dir)
  ('%s/files/MANIFEST.chromium' % SCRIPTDIR, '.'),
  ('%s/files/git.bat' % SCRIPTDIR, '.'),
  ('%s/files/gitk.bat' % SCRIPTDIR, '.'),
  ('%s/files/ssh_config' % SCRIPTDIR, '.'),
  ('%s/files/ssh.bat' % SCRIPTDIR, '.'),
  ('%s/files/ssh-keygen.bat' % SCRIPTDIR, '.'),
  ('%s/files/git.cmd' % SCRIPTDIR, 'cmd'),
  ('%s/files/gitk.cmd' % SCRIPTDIR, 'cmd'),
  ('%s/files/ssh.cmd' % SCRIPTDIR, 'cmd'),
  ('%s/files/ssh-keygen.cmd' % SCRIPTDIR, 'cmd'),
  ('%s/files/README.win32pad' % SCRIPTDIR, 'win32pad'),
  (os.path.join(SCRIPTDIR, os.pardir, os.pardir, 'bin',
    'README.msys-1.0.dll.chromium'), '.') ]


class FlushFile(io.TextIOWrapper):
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()
sys.stdout = FlushFile(sys.stdout)


def GetFileSize(filename):
  return os.stat(filename)[stat.ST_SIZE]


def main(argv):
  parser = optparse.OptionParser(usage='%prog [options]')
  parser.add_option('-u', '--url', default=None,
                    help='The URL of the portable git archive file.')
  parser.add_option('-f', '--file', default=None, dest='fname',
                    help='The local path of the portable git archive file.')
  parser.add_option('-r', '--release', default=None,
                    help='The git release version number (e.g. 1.8.5.2).')
  (opts, args) = parser.parse_args()

  if not ((opts.url or opts.fname) and opts.release):
    parser.error('Both --url|--file and --release are required.')
    return 1

  if opts.url and opts.fname:
    parser.error('Please specify either --url or --file, not both.')
    return 1

  PORTABLE_GIT_URL = opts.url
  PORTABLE_GIT_FILE = opts.fname or os.path.basename(PORTABLE_GIT_URL)
  DEPOT_GIT_DIR = 'git-%s_bin' % opts.release
  DEPOT_GIT_FILE = '%s.zip' % DEPOT_GIT_DIR

  tempdir = tempfile.mkdtemp(dir=os.environ.get('TEMP'))

  def RemoveTempdir(tempdir):
    if not re.match(r'^%s.*' % os.path.join(os.environ.get('TEMP'), 'tmp'),
                    tempdir):
      return
    os.system('rm -rf %s' % tempdir)

  def handler(signum, frame):
    RemoveTempdir(tempdir)
  signal.signal(signal.SIGINT, handler)

  if os.path.exists('%s/%s' % (SCRIPTDIR, DEPOT_GIT_FILE)):
    print 'ERROR: %s/%s already exists, remove to continue' % (
        SCRIPTDIR, DEPOT_GIT_FILE)
    return 1

  os.chdir(tempdir)
  os.mkdir(DEPOT_GIT_DIR)
  os.chdir(DEPOT_GIT_DIR)

  if PORTABLE_GIT_URL:
    if os.path.exists(PORTABLE_GIT_FILE):
      print 'ERROR: %s already exists, remove to continue' % PORTABLE_GIT_FILE
      return 1
    print 'Downloading Git from %s... ' % PORTABLE_GIT_URL,
    urllib.urlretrieve(PORTABLE_GIT_URL, PORTABLE_GIT_FILE)
    print 'done'

  # Exact the original portable git archive.
  print 'Extracting archive...'
  P7ZIP=None
  if platform.system() == 'Linux':
    P7ZIP = '7za'  # from p7zip-full package on Trusty
  else:
    # Assumed running in chromium msysgit environment.
    P7ZIP = os.path.join(SCRIPTDIR, os.pardir, os.pardir, 'share', '7-Zip', '7za.exe')
  os.system('%s x %s' % (P7ZIP, PORTABLE_GIT_FILE))

  # Remove unused executables.
  os.chdir('libexec/git-core/')
  gitexe_size = GetFileSize('git.exe')
  gitfiles = os.listdir('./')
  for gitfile in gitfiles:
    # Skip processing for files that begin with something other than git- or
    # end with something other than .exe.
    if not (gitfile.startswith('git-') and gitfile.endswith('.exe')):
      continue
    # Skip any git files in the LIBEXEC_EXEMPT_LIST.  The Git scripts call into
    # these exes directly.
    if gitfile in LIBEXEC_EXEMPT_LIST:
      continue
    if GetFileSize(gitfile) == gitexe_size:
      os.system('rm %s' % gitfile)

  # Move back to <tmp>/git-*_bin/.
  os.chdir('../../')

  # Set up win32pad.
  os.mkdir('win32pad')
  os.chdir('win32pad')
  print 'Downloading Win32pad from %s... ' % WIN32PAD_URL,
  urllib.urlretrieve(WIN32PAD_URL, WIN32PAD_FILE)
  print 'done'
  os.system('unzip %s' % WIN32PAD_FILE)
  os.system('rm %s' % WIN32PAD_FILE)
  os.chdir('..')

  def ProcessBootstrap(fn, outdir):
    f_in = open(fn, 'r')
    f_out = open(os.path.join(outdir, os.path.basename(fn)), 'w')
    for line in f_in:
      f_out.write(line.replace('@@GITDIR@@', DEPOT_GIT_DIR))
    f_in.close()
    f_out.close()

  # Place extra files into the archive directory.
  for fn, dest in BOOTSTRAP_FILES:
    ProcessBootstrap(fn, dest)

  # Create git_bin.zip archive.
  os.chdir('..')
  os.system('%s a -tzip %s %s' % (P7ZIP, DEPOT_GIT_FILE, DEPOT_GIT_DIR))

  # Set the archive aside.
  os.chdir(SCRIPTDIR)
  os.system('mv %s/%s ./' % (tempdir, DEPOT_GIT_FILE))
  RemoveTempdir(tempdir)

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv))
