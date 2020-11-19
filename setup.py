#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# python setup.py sdist --format=zip,gztar

from setuptools import setup
import setuptools.command.sdist
import os
import sys
import platform
import imp
import argparse

with open('README.rst', "r", encoding="utf-8") as f:
    long_description = f.read()

with open('contrib/requirements/requirements.txt') as f:
    requirements = f.read().splitlines()

with open('contrib/requirements/requirements-hw.txt') as f:
    requirements_hw = f.read().splitlines()

# # We use this convoluted way of importing version.py and constants.py
# # because the setup.py scripts tends to be called with python option
# # -O, which is not allowed for electroncash (see comment in module
# # electroncash/bitcoin.py). A regular import would trigger this issue.
# dirname = os.path.dirname(os.path.abspath(__file__))
# ec_package_dirname = os.path.join(dirname, "electroncash")
# sys.path.insert(0, ec_package_dirname)
#
#
# def get_version():
#     import version
#     return version.PACKAGE_VERSION
#
#
# def get_constants():
#     import constants as c
#     return c.PROJECT_NAME, c.REPOSITORY_URL, c.SCRIPT_NAME
PROJECT_NAME: str = "Electrum BCHA"
SCRIPT_NAME: str = "electrum-bcha"
REPOSITORY_URL: str = "https://github.com/PiRK/ElectrumBCHA"
def get_version():
    return  '4.3.0a0'

if sys.version_info[:3] < (3, 6):
    sys.exit(f"Error: {PROJECT} requires Python version >= 3.6...")

data_files = []

if platform.system() in ['Linux', 'FreeBSD', 'DragonFly']:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--user', dest='is_user', action='store_true', default=False)
    parser.add_argument('--system', dest='is_user', action='store_false', default=False)
    parser.add_argument('--root=', dest='root_path', metavar='dir', default='/')
    parser.add_argument('--prefix=', dest='prefix_path', metavar='prefix', nargs='?', const='/', default=sys.prefix)
    opts, _ = parser.parse_known_args(sys.argv[1:])

    # Use per-user */share directory if the global one is not writable or if a per-user installation
    # is attempted
    user_share   = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    system_share = os.path.join(opts.prefix_path, "share")
    if not opts.is_user:
        # Not neccarily a per-user installation try system directories
        if os.access(opts.root_path + system_share, os.W_OK):
            # Global /usr/share is writable for us so just use that
            share_dir = system_share
        elif not os.path.exists(opts.root_path + system_share) and os.access(opts.root_path, os.W_OK):
            # Global /usr/share does not exist, but / is writable keep using the global directory
            # (happens during packaging)
            share_dir = system_share
        else:
            # Neither /usr/share (nor / if /usr/share doesn't exist) is writable, use the
            # per-user */share directory
            share_dir = user_share
    else:
        # Per-user installation
        share_dir = user_share
    data_files += [
        # Menu icon
        (os.path.join(share_dir, 'icons/hicolor/128x128/apps/'), ['icons/electron-cash.png']),
        (os.path.join(share_dir, 'pixmaps/'),                    ['icons/electron-cash.png']),
        # Menu entry
        (os.path.join(share_dir, 'applications/'), ['electron-cash.desktop']),
        # App stream (store) metadata
        (os.path.join(share_dir, 'metainfo/'), ['org.electroncash.ElectronCash.appdata.xml']),
    ]

class MakeAllBeforeSdist(setuptools.command.sdist.sdist):
    """Does some custom stuff before calling super().run()."""

    user_options = setuptools.command.sdist.sdist.user_options + [
        ("disable-secp", None, "Disable libsecp256k1 complilation (default)."),
        ("enable-secp", None, "Enable libsecp256k1 complilation."),
        ("disable-zbar", None, "Disable libzbar complilation (default)."),
        ("enable-zbar", None, "Enable libzbar complilation."),
        ("disable-tor", None, "Disable tor complilation (default)."),
        ("enable-tor", None, "Enable tor complilation.")
    ]

    def initialize_options(self):
        self.disable_secp = None
        self.enable_secp = None
        self.disable_zbar = None
        self.enable_zbar = None
        self.disable_tor = None
        self.enable_tor = None
        super().initialize_options()

    def finalize_options(self):
        if self.enable_secp is None:
            self.enable_secp = False
        self.enable_secp = not self.disable_secp and self.enable_secp
        if self.enable_zbar is None:
            self.enable_zbar = False
        self.enable_zbar = not self.disable_zbar and self.enable_zbar
        if self.enable_tor is None:
            self.enable_tor = False
        self.enable_tor = not self.disable_tor and self.enable_tor
        super().finalize_options()

    def run(self):
        """Run command."""
        #self.announce("Running make_locale...")
        #0==os.system("contrib/make_locale") or sys.exit("Could not make locale, aborting")
        #self.announce("Running make_packages...")
        #0==os.system("contrib/make_packages") or sys.exit("Could not make locale, aborting")
        if self.enable_secp:
            self.announce("Running make_secp...")
            0==os.system("contrib/make_secp") or sys.exit("Could not build libsecp256k1")
        if self.enable_zbar:
            self.announce("Running make_zbar...")
            0==os.system("contrib/make_zbar") or sys.exit("Could not build libzbar")
        if self.enable_tor:
            self.announce("Running make_openssl...")
            0==os.system("contrib/make_openssl") or sys.exit("Could not build openssl")
            self.announce("Running make_libevent...")
            0==os.system("contrib/make_libevent") or sys.exit("Could not build libevent")
            self.announce("Running make_zlib...")
            0==os.system("contrib/make_zlib") or sys.exit("Could not build zlib")
            self.announce("Running make_tor...")
            0==os.system("contrib/make_tor") or sys.exit("Could not build tor")
        super().run()


platform_package_data = {}

if sys.platform in ('linux'):
    platform_package_data = {
        'electroncash_gui.qt': [
            'data/ecsupplemental_lnx.ttf',
            'data/fonts.xml'
        ],
    }

if sys.platform in ('win32', 'cygwin'):
    platform_package_data = {
        'electroncash_gui.qt': [
            'data/ecsupplemental_win.ttf'
        ],
    }

setup(
    cmdclass={
        'sdist': MakeAllBeforeSdist,
    },
    name=os.environ.get('EC_PACKAGE_NAME') or PROJECT_NAME.replace(" ", ""),
    version=os.environ.get('EC_PACKAGE_VERSION') or get_version(),
    install_requires=requirements,
    extras_require={
        'hardware': requirements_hw,
        'gui': ['pyqt5'],
        'all': requirements_hw + ['pyqt5']
    },
    packages=[
        'electroncash',
        'electroncash.qrreaders',
        'electroncash.rpa',
        'electroncash.slp',
        'electroncash.tor',
        'electroncash.utils',
        'electroncash_gui',
        'electroncash_gui.qt',
        'electroncash_gui.qt.qrreader',
        'electroncash_gui.qt.utils',
        'electroncash_gui.qt.utils.darkdetect',
        'electroncash_plugins',
        'electroncash_plugins.audio_modem',
        'electroncash_plugins.cosigner_pool',
        'electroncash_plugins.email_requests',
        'electroncash_plugins.hw_wallet',
        'electroncash_plugins.keepkey',
        'electroncash_plugins.labels',
        'electroncash_plugins.ledger',
        'electroncash_plugins.trezor',
        'electroncash_plugins.digitalbitbox',
        'electroncash_plugins.virtualkeyboard',
        'electroncash_plugins.shuffle_deprecated',
        'electroncash_plugins.satochip',
        'electroncash_plugins.fusion',
    ],
    package_data={
        'electroncash': [
            'servers.json',
            'servers_testnet.json',
            'servers_testnet4.json',
            'servers_scalenet.json',
            'currencies.json',
            'www/index.html',
            'wordlist/*.txt',
            'libsecp256k1*',
            'libzbar*',
            'locale/*/LC_MESSAGES/electron-cash.mo',
            'tor/bin/*'
        ],
        'electroncash_plugins.shuffle_deprecated': [
            'servers.json'
        ],
        'electroncash_plugins.fusion': [
            '*.svg', '*.png'
        ],
        # On Linux and Windows this means adding electroncash_gui/qt/data/*.ttf
        # On Darwin we don't use that font, so we don't add it to save space.
        **platform_package_data
    },
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Security :: Cryptography',
        'Topic :: Office/Business :: Financial'
    ],
    scripts=[SCRIPT_NAME],
    data_files=data_files,
    description="Lightweight BCHA Wallet",
    author=f"The {PROJECT_NAME} Developers",
    # author_email=
    license="MIT Licence",
    url=REPOSITORY_URL,
    long_description=long_description
)
