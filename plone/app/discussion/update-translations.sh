#!/bin/sh
#
# Shell script to manage .po files.

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
i18ndude rebuild-pot --pot locales/$PRODUCTNAME.pot --create $PRODUCTNAME --merge locales/$PRODUCTNAME-manual.pot .
i18ndude rebuild-pot --pot i18n/plone.pot --create "plone" --merge i18n/plone-manual.pot profiles

for lang in $LANGUAGES; do
    touch -a i18n/plone-$lang.po
    i18ndude sync --pot i18n/plone.pot i18n/plone-$lang.po
done

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
