from zope.component import queryUtility

from Acquisition import aq_inner, aq_parent

from zope.annotation.interfaces import IAnnotations

from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable

from plone.app.discussion.conversation import ANNOTATION_KEY
from plone.app.discussion.interfaces import ICommentingTool


def patchedClearFindAndRebuild(self):
    """Empties catalog, then finds all contentish objects (i.e. objects
       with an indexObject method), and reindexes them.
       This may take a long time.
    """

    def indexObject(obj, path):

        if (base_hasattr(obj, 'indexObject') and
            safe_callable(obj.indexObject)):

            try:
                obj.indexObject()

                annotions = IAnnotations(obj)
                ctool = queryUtility(ICommentingTool)
                if ANNOTATION_KEY in annotions:
                    conversation = annotions[ANNOTATION_KEY]
                    conversation = conversation.__of__(obj)
                    for comment in conversation.getComments():
                        try:
                            if ctool:
                                ctool.indexObject(comment)
                        except StopIteration:  # pragma: no cover
                            pass

            except TypeError:
                # Catalogs have 'indexObject' as well, but they
                # take different args, and will fail
                pass

    self.manage_catalogClear()
    portal = aq_parent(aq_inner(self))
    portal.ZopeFindAndApply(portal, search_sub=True, apply_func=indexObject)
