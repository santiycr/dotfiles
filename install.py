#!/usr/bin/env python

import sys
import os
import shutil
import subprocess
import platform


class Installation(object):
    """ Specific installations subclass this class and define:
        - other installations they depend on
        - a set of steps the installation is compossed of """

    NAME = "REDEFINE"
    DEPENDENCIES = []

    def __init__(self):
        self.DOTFILES_PATH = os.path.dirname(os.path.realpath(__file__))
        self.HOME_PATH = os.environ['HOME']

    def safe_ln(self, source, dest):
        source = "%s/%s" % (self.DOTFILES_PATH, source)
        dest = "%s/%s" % (self.HOME_PATH, dest)
        if os.path.islink(dest):
            print("Existing link in %s to %s found. Unlinking."
                  % (dest, os.path.realpath(dest)))
            os.unlink(dest)
        elif os.path.isfile(dest) or os.path.isdir(dest):
            print "Already existing config found. Moving up to %s.orig" % dest
            shutil.move(dest, dest + ".orig")
        os.symlink(source, dest)

    def safe_mkdir(self, dest):
        dest = "%s/%s" % (self.HOME_PATH, dest)
        if not os.path.isdir(dest):
            os.mkdir(dest)

    def install(self, package, extras=''):
        if platform.system() == 'Darwin':
            installer = 'brew install'
        elif platform.system() == 'Linux':
            installer = 'sudo apt-get install'
        else:
            raise Exception('SAYWHAA')
        os.system("%s %s %s" % (installer, extras, package))

    def run(self, already_installed):
        print 'Installing %s' % self.NAME
        for dependency in self.DEPENDENCIES:
            if dependency in already_installed:
                continue
            for installation in find_installations(dependency):
                installation().run(already_installed)
        self.steps()
        already_installed.append(self.NAME)

    def steps(self):
        """ installation subclasses need to define their own steps method """
        print "steps method hasn't been defined! Broken installation"


class DotfilesInstallation(Installation):
    NAME = "dotfiles"

    def steps(self):
        os.system('cd %s;'
                  'git submodule init;'
                  'git submodule update;'
                  'cd -;'
                  % self.DOTFILES_PATH)
        os.system('cd %s/zsh/prezto;'
                  'git submodule init;'
                  'git submodule update;'
                  'cd -;'
                  % self.DOTFILES_PATH)


class VimInstallation(Installation):
    NAME = "vim"
    DEPENDENCIES = ['dotfiles', 'lint', 'git']

    def steps(self):
        if platform.system() == 'Darwin':
            self.install('macvim', '--override-system-vim')
        self.safe_ln('vim/vimrc', '.vimrc')
        self.safe_ln('vim', '.vim')
        self.safe_mkdir('.vim/tmp')
        self.safe_mkdir('.vim/tmp/swap')
        self.safe_mkdir('.vim/tmp/undo')
        self.safe_mkdir('.vim/tmp/backup')
        self.safe_mkdir('.vim/bundle')
        os.system('git clone git://github.com/Shougo/neobundle.vim'
                  ' ~/.vim/bundle/neobundle.vim')
        os.system('vim +NeoBundleInstall +qall')


class VirtualenvInstallation(Installation):
    NAME = "virtualenv"
    DEPENDENCIES = ['zsh']

    def steps(self):
        os.system('which mkvirtualenv || curl -s https://raw.github.com/brainsik/'
                  'virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL')


class TmuxInstallation(Installation):
    NAME = "tmux"
    DEPENDENCIES = ['git']

    def steps(self):
        self.install('tmux')
        self.safe_ln('tmux/tmux.conf', '.tmux.conf')
        self.safe_mkdir('.tmux/plugins')
        os.system('git clone https://github.com/tmux-plugins/tpm'
                  ' ~/.tmux/plugins/tpm')
        os.system('which gem && sudo gem install tmuxinator')
        self.safe_ln('tmux/tmuxinator', '.tmuxinator')


class ZshInstallation(Installation):
    NAME = "zsh"
    DEPENDENCIES = ['dotfiles']

    def steps(self):
        self.safe_ln('zsh/prezto', '.zprezto')
        self.safe_ln('zsh/prezto/runcoms/zshrc', '.zshrc')
        self.safe_ln('zsh/prezto/runcoms/zshenv', '.zshenv')
        self.safe_ln('zsh/prezto/runcoms/zlogin', '.zlogin')
        self.safe_ln('zsh/prezto/runcoms/zlogout', '.zlogout')
        self.safe_ln('zsh/prezto/runcoms/zprofile', '.zprofile')
        self.safe_ln('zsh/zpreztorc', '.zpreztorc')
        os.system('chsh -s /bin/zsh')


class GitInstallation(Installation):
    NAME = 'git'

    def steps(self):
        self.install('hub')
        self.safe_ln('git/gitconfig', '.gitconfig')
        self.safe_ln('git/gitignore', '.gitignore')


class BinInstallation(Installation):
    NAME = 'bin'

    def steps(self):
        self.safe_mkdir("bin")
        for script in os.listdir(self.DOTFILES_PATH + '/bin'):
            self.safe_ln('bin/' + script, 'bin/' + os.path.basename(script))


class LintInstallation(Installation):
    NAME = 'lint'

    def steps(self):
        with open(os.devnull, "w") as devnull:

            for lint in ['pep8', 'flake8']:
                if not subprocess.call(['which', '-s', lint],
                                       stdout=devnull, stderr=devnull):
                    break
            else:
                print "WARNING: No pep8 lint-like found in path"

            for lint in ['jshint']:
                if subprocess.call(['which', '-s', lint],
                                   stdout=devnull, stderr=devnull):
                    print "WARNING: No %s binary found in path" % lint

        self.safe_ln('lint/pep8', '.pep8')
        self.safe_ln('lint/jshintrc', '.jshintrc')


def find_installations(name):
    installations = []
    for installation in [c for n, c in globals().items()
                         if 'steps' in dir(c) and
                         Installation in c.mro() and
                         c != Installation]:
        if name == 'all' or installation.NAME == name:
            installations.append(installation)
    if installations:
        return installations
    print "Invalid installtion requested: %s" % name
    sys.exit(1)


if __name__ == "__main__":
    installs = sys.argv[1:]

    already_installed = []
    for install in installs:
        for installation in find_installations(install):
            if installation.NAME not in already_installed:
                installation().run(already_installed)
