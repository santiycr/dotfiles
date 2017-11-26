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

    def __init__(self, skip_verify):
        self.DOTFILES_PATH = os.path.dirname(os.path.realpath(__file__))
        self.HOME_PATH = os.environ['HOME']
        self.skip_verify = skip_verify

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

    def pip_install(self, package, upgrade=True):
        for pip_binary in ['pip3', 'pip', 'pip2']:
            if shutil.which(pip_install):
                break
        else:
            raise Exception("No pip available")

        os.system("{} install --user {} {}".format(
            pip_binary, "--upgrade" if upgrade else "", package))

    def npm_install(self, package):
        os.system('npm install -g {}'.format(package))

    def run(self, already_installed):
        print 'Installing %s' % self.NAME
        for dependency in self.DEPENDENCIES:
            if dependency in already_installed:
                continue
            for installation in find_installations(dependency):
                installation(self.skip_verify).run(already_installed)
        if self.skip_verify or self.verify():
            self.steps()
        already_installed.append(self.NAME)

    def verify(self):
        question = "> Proceed installing installation %s [Yn]: " % self.NAME
        return raw_input(question).lower() in ['', 'y']

    def steps(self):
        """ installation subclasses need to define their own steps method """
        print "steps method hasn't been defined! Broken installation"

class MacInstallation(Installation):
    NAME = "mac"

    def steps(self):
        # Show all extrensions
        os.system('defaults write -g AppleShowAllExtensions -bool true')
        # unhide Library
        os.system('chflags nohidden ~/Library')
        # Set Current Folder as Default Search Scope
        os.system('defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"')
        # Set Default Finder Location to Home Folder
        os.system('defaults write com.apple.finder NewWindowTarget -string "PfLo" &&'
                  'defaults write com.apple.finder NewWindowTargetPath -string "file://${HOME}"')
        # Disable Creation of Metadata Files on Network Volumes
        os.system('defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true')
        # Disable Creation of Metadata Files on USB Volumes
        os.system('defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true')
        # Enable FileVault
        os.system('sudo fdesetup enable')
        # https://github.com/sindresorhus/quick-look-plugins
        self.cask_install('qlcolorcode')
        self.cask_install('qlstephen')
        self.cask_install('qlmarkdown')
        self.cask_install('quicklook-json')
        self.cask_install('qlprettypatch')
        self.cask_install('quicklook-csv')
        self.cask_install('betterzipql')
        self.cask_install('qlimagesize')
        self.cask_install('webpquicklook')
        self.cask_install('suspicious-package')
        self.cask_install('quicklookase')
        self.cask_install('qlvideo')



class CaskInstallation(Installation):
    NAME = "cask"

    def steps(self):
        self.tap('caskroom/cask')


class NeoVimInstallation(Installation):
    NAME = "neovim"
    DEPENDENCIES = ['lint', 'git', 'cask', 'autoformat']

    def steps(self):
        if platform.system() == 'Darwin':
            self.tap('neovim/neovim')
            self.tap('caskroom/fonts')
            self.cask_install('font-inconsolata-nerd-font')
        self.install('neovim')
        self.install('grip') # used by markdown-preview
        self.pip_install('neovim')
        self.safe_mkdir('.config')
        self.safe_ln('vim', '.config/nvim')
        self.safe_ln('vim/vimrc', '.config/nvim/init.vim')
        self.safe_mkdir('.config/nvim/tmp/swap')
        self.safe_mkdir('.config/nvim/tmp/undo')
        self.safe_mkdir('.config/nvim/tmp/backup')
        os.system('curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs '
                  'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim')
        os.system('nvim +PlugInstall +qall')


class autoformatInstallation(Installation):
    NAME = "autoformat"

    def steps(self):
        self.install('tiny-html5')
        self.pip_install('autopep8')
        self.pip_install('js-beautify')
        self.pip_install('remark-cli')


class VimrInstallation(Installation):
    NAME = "vimr"
    DEPENDENCIES = ['neovim']

    def steps(self):
        if platform.system() == 'Darwin':
            self.cask_install('vimr')


class HammerspoonInstallation(Installation):
    NAME = "hammerspoon"

    def steps(self):
        if platform.system() != 'Darwin':
            raise Exception('SAYWHAA')
        self.cask_install('hammerspoon')
        self.safe_ln('hammerspoon', '.hammerspoon')


class TmuxInstallation(Installation):
    NAME = "tmux"
    DEPENDENCIES = ['git']

    def steps(self):
        self.install('tmux')
        self.install('fpp')
        self.install('urlview')
        if platform.system() == 'Darwin':
            self.install('reattach-to-user-namespace')
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

    def steps(self):
        self.safe_ln('zsh/zshrc', '.zshrc')

        # os.system('git clone https://github.com/tarjoilija/zgen.git'
        #           ' ~/.zgen')
        # TODO Use a custom fork of zgen that drops prezto modules on top:
        os.system('git clone git@github.com:brandon-fryslie/zgen.git'
                  ' ~/.zgen')
        os.system('zsh -i -c exit')
        if platform.system() == 'Darwin':
            self.install('zsh')
            os.system('sudo dscl . -create /Users/$USER UserShell /usr/local/bin/zsh')
        else:
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
            self.npm_install('diff-so-fancy')
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
        os.pip_install('flake8')
        self.npm_install('jshint')
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
    skip_verify = '-y' in installs
    if skip_verify:
        installs.remove('-y')

    already_installed = []
    for install in installs:
        for installation in find_installations(install):
            if installation.NAME not in already_installed:
                installation(skip_verify).run(already_installed)
