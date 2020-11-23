Building Mac OS binaries
========================

✗ _This script does not produce reproducible output (yet!)._

This guide explains how to build binaries for macOS systems.
We build our binaries on El Capitan (10.11.6) as building it on High Sierra
makes the binaries incompatible with older versions.

This assumes that the Xcode + Xcode Command Line tools (and thus git) are already installed. You can install older (and newer!) versions of Xcode from Apple provided you have a devloper account [from the Apple developer downloads site](https://developer.apple.com/download/more/).


## 1. Make sure to freshen git submodules

    git submodule update --init

The above ensures that you pull in the zbar, secp256k1, and other submodules.

## 2. Use the provided script to begin building.

    ./make_osx

Or, if you wish to sign the app when building, provide an Apple developer identity installed on the system for signing:

    ./make_osx "Developer ID Application: MY NAME (123456789)"

To find the identity string, use the following command:

    security find-identity -v -p codesigning

## 2. Done

You should see ElectrumABC.app and ElectrumABC-x.y.z.dmg in ../dist/. If you provided an identity for signing, these files can even be distributed to other Macs and they will run there without warnings from GateKeeper.
