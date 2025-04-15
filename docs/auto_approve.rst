Automatic Comment Approval
==========================

Introduction
-----------

This feature enhances the Plone discussion system by automatically approving comments from users
who have the "Review comments" permission, even when comment moderation is enabled site-wide.

How It Works
-----------

When a user with the "Review comments" permission creates a comment, the system will:

1. Check if comment moderation is enabled
2. Verify if the user has the "Review comments" permission
3. Automatically publish the comment if both conditions are met

This functionality is particularly useful for:

- Trusted community members
- Moderators who should bypass the moderation queue
- Site editors or staff members

Configuration
------------

No additional configuration is needed. Simply assign the "Review comments" permission to 
the roles or users you want to bypass moderation.

Examples:

- Assign "Review comments" permission to the Editor role
- Create a "Trusted Commenter" role with the "Review comments" permission
- Give specific users the permission on specific content

Permission Management
-------------------

The "Review comments" permission can be managed:

- Site-wide through the Security control panel
- On specific folders or content items through the Sharing tab
- Programmatically using the Plone security APIs
