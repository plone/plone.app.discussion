#!/bin/sh
#
# Shell script to manage .po files.
#
# Run this file in the folder main __init__.py of product
#
# E.g. if your product is yourproduct.name
# you run this file in yourproduct.name/yourproduct/name
#
#
# Copyright 2009 Twinapex Research http://www.twinapex.com
#

# Assume the product name is the current folder name
CURRENT_PATH=`pwd`
PRODUCTNAME="plone.app.discussion"

# List of languages
LANGUAGES="de it"

# Create locales folder structure for languages
install -d locales
for lang in $LANGUAGES; do
    install -d locales/$lang/LC_MESSAGES
done

# Rebuild .pot
i18ndude rebuild-pot --pot locales/$PRODUCTNAME.pot --create $PRODUCTNAME .

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then

        PO=$lang/LC_MESSAGES/${PRODUCTNAME}.po

        # Create po file if not exists
        touch $PO

        # Sync po file
        echo "Syncing $PO"
        i18ndude sync --pot locales/$PRODUCTNAME.pot $PO

        # Compile .po to .mo
        MO=$lang/LC_MESSAGES/${PRODUCTNAME}.mo
        echo "Compiling $MO"
        msgfmt -o $MO $lang/LC_MESSAGES/${PRODUCTNAME}.po
    fi
done

