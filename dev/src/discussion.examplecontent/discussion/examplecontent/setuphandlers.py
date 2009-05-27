from zope.component import createObject

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

from Products.CMFPlone.utils import _createObjectByType

from plone.app.discussion.interfaces import IConversation, IReplies

def addUser(portal, id, fullname, password, email, roles):
    status=""
    props = {"username": id,
             "fullname": fullname,
             "password": password,
             "email": email}
    # add a new member to the Portal
    try:
        portal.portal_registration.addMember(id, password, roles,domains="",
                                              properties=props)
        status+="The user "+fullname+" was successfully added.\n"
    except:
        status+="The user "+fullname+" was not added.\n"
    portal.plone_log(status)

def addComments(portal):

    # Create document
    _createObjectByType('Document', portal, id='doc1', title='Document 1')
    portal.plone_log("Document 1 created")

    doc1 = portal.get('doc1', None)

    # Create a conversation. In this case we doesn't assign it to an
    # object, as we just want to check the Conversation object API.
    conversation = IConversation(doc1)

    # Pretend that we have traversed to the comment by aq wrapping it.
    conversation = conversation.__of__(doc1)

    replies = IReplies(conversation)

    # Create a nested comment structure:
    #
    # Conversation
    # +- Comment 1
    #    +- Comment 1_1
    #    |  +- Comment 1_1_1
    #    +- Comment 1_2
    # +- Comment 2
    #    +- Comment 2_1
    # +- Comment 3
    # +- Comment 4

    # Create all comments
    comment1 = createObject('plone.Comment')
    comment1.title = 'Comment 1'
    comment1.text = 'Comment text'
    comment1.Creator = 'Jim'

    comment1_1 = createObject('plone.Comment')
    comment1_1.title = 'Re: Comment 1'
    comment1_1.text = 'Comment text'
    comment1_1.Creator = 'Emma'

    comment1_1_1 = createObject('plone.Comment')
    comment1_1_1.title = 'Re: Re: Comment 1'
    comment1_1_1.text = 'Comment text'
    comment1_1_1.Creator = 'Lukas'

    comment1_2 = createObject('plone.Comment')
    comment1_2.title = 'Re: Comment 1 (2)'
    comment1_2.text = 'Comment text'
    comment1_2.Creator = 'Jim'

    comment2 = createObject('plone.Comment')
    comment2.title = 'Comment 2'
    comment2.text = 'Comment text'
    comment2.Creator = 'Lukas'

    comment2_1 = createObject('plone.Comment')
    comment2_1.title = 'Re: Comment 2'
    comment2_1.text = 'Comment text'
    comment2_1.Creator = 'Emma'

    comment3 = createObject('plone.Comment')
    comment3.title = 'Comment 3'
    comment3.text = 'Comment text'
    comment3.Creator = 'Lukas'

    comment4 = createObject('plone.Comment')
    comment4.title = 'Comment 4'
    comment4.text = 'Comment text'
    comment4.Creator = 'Emma'

    # Create the nested comment structure
    new_id_1 = conversation.addComment(comment1)
    new_id_2 = conversation.addComment(comment2)
    new_id_3 = conversation.addComment(comment3)
    new_id_4 = conversation.addComment(comment4)

    comment1_1.in_reply_to = new_id_1
    new_id_1_1 = conversation.addComment(comment1_1)

    comment1_1_1.in_reply_to = new_id_1_1
    new_id_1_1_1 = conversation.addComment(comment1_1_1)

    comment1_2.in_reply_to = new_id_1
    new_id_1_2 = conversation.addComment(comment1_2)

    comment2_1.in_reply_to = new_id_2
    new_id_2_1 = conversation.addComment(comment2_1)

    # Add a comment. Note: in real life, we always create comments via the factory
    # to allow different factories to be swapped in

    portal.plone_log("")

def importVarious(context):
    """Miscellanous steps import handle
    """

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('discussion.examplecontent_various.txt') is None:
        return

    portal = context.getSite()

    addUser(portal, id="jim", fullname="Jim Knopf", password="lummerland",
            email="jim@lummerland.com", roles = ("Member",))
    addUser(portal, id="lukas", fullname="Lukas", password="lummerland",
            email="lukas@lummerland.com", roles = ("Member",))
    addUser(portal, id="emma", fullname="Emma", password="lummerland",
            email="emma@lummerland.com", roles = ("Member",))
    addComments(portal)