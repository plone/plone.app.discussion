# Monkey patch plone.app.vocabularies.types.BAD_TYPES and remove
# 'Discussion Item' from this tuple, so that Comments can be found
# in the search. This will become needless once plone.app.discussion
# will become a part of Plone 4.

import plone.app.vocabularies.types

new_bad_types = list(plone.app.vocabularies.types.BAD_TYPES)
if 'Discussion Item' in new_bad_types:
    new_bad_types.remove('Discussion Item')
plone.app.vocabularies.types.BAD_TYPES = new_bad_types