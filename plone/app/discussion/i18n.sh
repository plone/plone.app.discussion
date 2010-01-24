#!/bin/sh

DOMAIN='plone.app.discussion'

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --create ${DOMAIN} .

i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${DOMAIN}.mo $lang/LC_MESSAGES/${DOMAIN}.po
    fi
done