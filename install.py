#!/usr/bin/env python

import sys
import os
import shutil
import subprocess

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
    installs = ['dotfiles', 'vim', 'tmux', 'zsh', 'git', 'pep8', 'bin']

for install in installs:
    print "installing %s" % install
    if install == 'vim':
        safe_ln('vim/vimrc', '.vimrc')
        safe_ln('vim/vimrc', '.gvimrc')
        safe_ln('vim', '.vim')
        safe_mkdir(".vim/tmp")
        safe_mkdir(".vim/tmp/swap")
        safe_mkdir(".vim/tmp/undo")
        safe_mkdir(".vim/tmp/backup")
    elif install == 'tmux':
        safe_ln('tmux/tmux.conf', '.tmux.conf')
        safe_ln('tmux/tmux.osx.conf', '.tmux.osx.conf')
    elif install == 'zsh':
        safe_ln('zsh/zshrc', '.zshrc')
        os.system("chsh -s /bin/zsh")
    elif install == 'git':
        safe_ln('git/gitconfig', '.gitconfig')
    elif install == 'bin':
        safe_mkdir("bin")
        for script in os.listdir(DOTFILES_PATH + '/bin'):
            safe_ln('bin/' + script, 'bin/' + os.path.basename(script))
    elif install == 'dotfiles':
        os.system("cd %s; git submodule init; git submodule update" % DOTFILES_PATH)
    elif install == 'pep8':
        with open(os.devnull, "w") as devnull:
            for lint in ['pep8', 'flake8']:
                if not subprocess.call(['which', '-s', lint],
                                       stdout=devnull, stderr=devnull):
                    break
            else:
                print "WARNING: No pep8 lint-like found"

        safe_ln('pep8/pep8', '.pep8')
    else:
        print "Invalid install requested: %s" % install
