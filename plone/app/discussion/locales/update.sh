domain=plone.app.discussion
i18ndude rebuild-pot --pot $domain.pot --create $domain --merge $domain-manual.pot ../
i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po

i18ndude rebuild-pot --pot ../i18n/plone.pot --create plone --merge ../i18n/plone-manual.pot ../profiles
i18ndude sync --pot ../i18n/plone.pot ../i18n/plone-*.po
