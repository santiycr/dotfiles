#!/usr/bin/env python

import sys
import os
import shutil

DOTFILES_PATH = os.path.dirname(os.path.realpath(__file__))
HOME_PATH = os.environ['HOME']

def safe_ln(source, dest):
    source = "%s/%s" % (DOTFILES_PATH, source)
    dest = "%s/%s" % (HOME_PATH, dest)
    if os.path.islink(dest):
        print "Existing link in %s to %s found. Unlinking." % (dest, os.path.realpath(dest))
        os.unlink(dest)
    elif os.path.isfile(dest) or os.path.isdir(dest):
        print "Already existing config found. Moving up to %s.orig" % dest
        shutil.move(dest, dest+".orig")
    os.symlink(source, dest)

for install in sys.argv[1:]:
    print "installing %s" % install
    if install == 'vim':
        safe_ln('vim/vimrc', '.vimrc')
        safe_ln('vim/vimrc', '.gvimrc')
        safe_ln('vim', '.vim')
