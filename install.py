#!/usr/bin/env python

import sys
import os
import shutil
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

    def tap(self, src, extras=''):
        if platform.system() == 'Darwin':
            installer = 'brew tap'
        else:
            raise Exception('SAYWHAA')
        os.system("%s %s %s" % (installer, extras, src))

    def install(self, package, extras=''):
        if platform.system() == 'Darwin':
            installer = 'brew install'
        elif platform.system() == 'Linux':
            installer = 'sudo apt-get install'
        else:
            raise Exception('SAYWHAA')
        os.system("%s %s %s" % (installer, extras, package))

    def cask_install(self, package, extras=''):
        if platform.system() != 'Darwin':
            raise Exception('SAYWHAA')
        installer = 'brew cask install'
        os.system("%s %s %s" % (installer, extras, package))

    def run(self, already_installed):
        print 'Installing %s' % self.NAME
        for dependency in self.DEPENDENCIES:
            if dependency in already_installed:
                continue
            for installation in find_installations(dependency):
                installation().run(already_installed)
        if self.verify():
            self.steps()
        already_installed.append(self.NAME)

    def verify(self):
        question = "> Proceed installing installation %s [Yn]: " % self.NAME
        return raw_input(question).lower() in ['', 'y']

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


class CaskInstallation(Installation):
    NAME = "cask"

    def steps(self):
        self.tap('caskroom/cask')


class VimInstallation(Installation):
    NAME = "vim"
    DEPENDENCIES = ['dotfiles', 'lint', 'git', 'cask']

    def steps(self):
        if platform.system() == 'Darwin':
            self.cask_install('macvim')
            self.cask_install('font-inconsolata-for-powerline')
        self.safe_ln('vim/vimrc', '.vimrc')
        self.safe_ln('vim', '.vim')
        self.safe_mkdir('.vim/tmp')
        self.safe_mkdir('.vim/tmp/swap')
        self.safe_mkdir('.vim/tmp/undo')
        self.safe_mkdir('.vim/tmp/backup')
        os.system('curl -fLo ~/.vim/autoload/plug.vim --create-dirs'
                  'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim')
        os.system('vim +PlugInstall +qall')


class NeoVimInstallation(Installation):
    NAME = "neovim"
    DEPENDENCIES = ['vim']

    def steps(self):
        if platform.system() == 'Darwin':
            self.tap('neovim/neovim')
            self.install('neovim')
        self.safe_mkdir('.config')
        self.safe_ln('vim', '.config/nvim')
        self.safe_ln('vim/vimrc', '.config/nvim/init.vim')
        self.safe_mkdir('.config/nvim/tmp/swap')
        self.safe_mkdir('.config/nvim/tmp/undo')
        self.safe_mkdir('.config/nvim/tmp/backup')
        os.system('curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs'
                  'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim')
        os.system('vim +PlugInstall +qall')


class VimrInstallation(Installation):
    NAME = "vimr"
    DEPENDENCIES = ['neovim']

    def steps(self):
        if platform.system() == 'Darwin':
            self.cask_install('vimr')


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
        self.safe_mkdir('.tmux')
        self.safe_mkdir('.tmux/plugins')
        os.system('git clone https://github.com/tmux-plugins/tpm'
                  ' ~/.tmux/plugins/tpm')
        os.system('tmux start-server; tmux new-session -d;'
                  '%s/.tmux/plugins/tpm/scripts/install_plugins.sh'
                  % self.HOME_PATH)
        os.system('which gem && sudo gem install tmuxinator')
        self.safe_ln('tmux/tmuxinator', '.tmuxinator')


class ZInstallation(Installation):
    NAME = "z"

    def steps(self):
        self.install('z')


class OndirInstallation(Installation):
    NAME = "ondir"
    DEPENDENCIES = ['zsh']

    def steps(self):
        self.install('ondir')
        self.safe_ln('ondirrc', '.ondirrc')


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


class NodeInstallation(Installation):
    NAME = 'node'

    def steps(self):
        self.install('node')


class GitInstallation(Installation):
    NAME = 'git'
    DEPENDENCIES = ['node']

    def steps(self):
        self.install('hub')
        if platform.system() == 'Darwin':
            self.install('diff-so-fancy')
        else:
            os.system('npm install -g diff-so-fancy')
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
    DEPENDENCIES = ['node']

    def steps(self):
        os.system('pip install --user flake8')
        os.system('npm install -g jshint')
        self.safe_ln('lint/pep8', '.pep8')
        self.safe_mkdir('.config')
        self.safe_ln('lint/flake8', '.config/flake8')
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
