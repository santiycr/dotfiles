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
        print ("Existing link in %s to %s found. Unlinking."
                % (dest, os.path.realpath(dest)))
        os.unlink(dest)
    elif os.path.isfile(dest) or os.path.isdir(dest):
        print "Already existing config found. Moving up to %s.orig" % dest
        shutil.move(dest, dest + ".orig")
    os.symlink(source, dest)


def safe_mkdir(dest):
    dest = "%s/%s" % (HOME_PATH, dest)
    if not os.path.isdir(dest):
        os.mkdir(dest)


installs = sys.argv[1:]
if installs == ['all']:
    installs = ['vim', 'tmux', 'zsh', 'git', 'bin']

for install in installs:
    print "installing %s" % install
    if install == 'vim':
        safe_ln('vim/vimrc', '.vimrc')
        safe_ln('vim/vimrc', '.gvimrc')
        safe_ln('vim', '.vim')
        safe_mkdir("vim/tmp")
        safe_mkdir("vim/tmp/swap")
        safe_mkdir("vim/tmp/undo")
        safe_mkdir("vim/tmp/backup")
    elif install == 'tmux':
        safe_ln('tmux/tmux.conf', '.tmux.conf')
    elif install == 'zsh':
        safe_ln('zsh/zshrc', '.zshrc')
    elif install == 'git':
        safe_ln('git/gitconfig', '.gitconfig')
    elif install == 'bin':
        safe_mkdir("bin")
        for script in os.listdir(DOTFILES_PATH + '/bin'):
            safe_ln('bin/' + script, 'bin/' + os.path.basename(script))
    else:
        print "Invalid install requested: %s" % install
