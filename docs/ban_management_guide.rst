Ban Management Web Interface
============================

The ban management system provides a comprehensive web interface for administrators
to manage problematic users without resorting to permanent account restrictions.

## Accessing Ban Management

### Prerequisites
- User must have "Review comments" permission
- Ban system must be enabled in Discussion Control Panel

### Main Ban Management View

Access: `@@ban-management`

**Features:**
- Quick ban form for immediate user restrictions
- Active bans overview with detailed information
- Bulk actions for maintenance

**Quick Ban Form:**
- User ID field (required)
- Ban type selector:
  * Cooldown Ban: Temporary comment restriction
  * Shadow Ban: Hidden comments (user unaware)
  * Permanent Ban: Complete comment restriction
- Duration field (for non-permanent bans)
- Reason field for documentation

**Active Bans Table:**
- User information
- Ban type and status
- Creation and expiration dates
- Remaining time calculation
- Moderator who created the ban
- Reason for the ban
- Quick unban action

### Individual User Ban Form

Access: `@@ban-user-form?user_id=username`

**Features:**
- User information verification
- Detailed ban type descriptions
- Duration configuration
- Mandatory reason field

**Ban Type Descriptions:**

*Cooldown Ban:*
- Temporarily prevents user from commenting
- Automatic expiration
- Clear notification to user with remaining time
- Useful for "cooling off" heated discussions

*Shadow Ban:*
- Comments appear published to the author
- Hidden from all other users
- Can be time-limited or indefinite
- Effective for managing trolls without confrontation

*Permanent Ban:*
- Complete restriction from commenting
- Requires explicit administrative action to lift
- Clear notification of permanent status
- Reserved for severe violations

## User Experience

### For Banned Users

**Cooldown Ban:**
```
"You are temporarily banned from commenting for 2 hours and 15 minutes. 
Reason: Excessive off-topic comments."
```

**Shadow Ban (if notifications enabled):**
```
"Your comments are currently under review. 
Reason: Suspected automated posting."
```

**Permanent Ban:**
```
"You have been permanently banned from commenting. 
Reason: Violation of community guidelines."
```

### For Other Users

**Shadow Banned Comments:**
- Comments from shadow banned users are invisible
- No indication that comments were hidden
- Maintains normal conversation flow

## Administrative Workflow

### Typical Moderation Workflow

1. **Identify Problematic User**
   - Review reported comments
   - Observe patterns of behavior
   - Consider escalation path

2. **Choose Appropriate Ban Type**
   - **First offense:** Cooldown (1-24 hours)
   - **Repeated issues:** Shadow ban (24-72 hours)
   - **Severe violations:** Permanent ban

3. **Apply Ban**
   - Document clear reason
   - Set appropriate duration
   - Monitor for circumvention

4. **Follow Up**
   - Review ban effectiveness
   - Adjust duration if needed
   - Consider lifting for good behavior

### Bulk Operations

**Cleanup Expired Bans:**
- Removes inactive bans from storage
- Improves system performance
- Provides count of cleaned items

## Integration Points

### Comment Moderation View

Ban management links are integrated into:
- Comment moderation interface
- User profile pages (if available)
- Content management workflow

### Status Checking

**User Ban Status API:**
Access: `@@user-ban-status`

Returns JSON with current user's ban information:
```json
{
  "banned": true,
  "ban_type": "cooldown",
  "can_comment": false,
  "reason": "Spam posting",
  "expires_date": "2024-01-15T10:30:00"
}
```

## Configuration Options

### Discussion Control Panel Settings

**Enable User Ban System:**
- Master switch for ban functionality
- Default: Disabled

**Notify Users of Shadow Bans:**
- Controls shadow ban visibility to users
- Default: Disabled (true shadow bans)

**Default Cooldown Duration:**
- Hours for cooldown bans when not specified
- Default: 24 hours

## Security Considerations

### Permission Model
- Uses existing "Review comments" permission
- No additional permissions required
- Follows Plone security model

### Data Protection
- Ban data stored in portal annotations
- Automatic cleanup of expired bans
- No personal data beyond user ID

### Audit Trail
- All bans include moderator ID
- Creation timestamps recorded
- Reason field for documentation

## Troubleshooting

### Common Issues

**Ban Not Taking Effect:**
- Check ban system is enabled
- Verify user has permission
- Clear caches if needed

**User Can Still Comment After Ban:**
- Check ban type (shadow bans allow commenting)
- Verify ban hasn't expired
- Check for permission overrides

**Missing Ban Management Views:**
- Verify "Review comments" permission
- Check ZCML configuration
- Restart instance if needed

### Performance Considerations

- Expired bans are cleaned automatically
- Large numbers of bans may impact performance
- Regular cleanup recommended for high-volume sites

## Monitoring and Reporting

### Ban Statistics

Monitor ban usage through:
- Active bans count
- Ban type distribution
- Average ban duration
- Moderator activity

### Effectiveness Metrics

Track ban effectiveness by:
- Repeat offender rates
- Comment quality improvements
- User behavior changes
- Community feedback

## Best Practices

### Ban Duration Guidelines

**Cooldown Bans:**
- Minor issues: 1-6 hours
- Moderate issues: 12-24 hours  
- Serious issues: 2-7 days

**Shadow Bans:**
- Testing period: 24-48 hours
- Suspected automation: 3-7 days
- Behavioral modification: 1-2 weeks

**Permanent Bans:**
- Reserved for severe violations
- Document thoroughly
- Provide appeal process

### Communication

**Documentation:**
- Always provide clear reason
- Use consistent language
- Reference community guidelines

**User Communication:**
- Explain ban duration and reason
- Provide improvement guidelines
- Offer appeal process if applicable

### Regular Maintenance

**Weekly Tasks:**
- Review active bans
- Clean up expired bans
- Monitor ban effectiveness

**Monthly Tasks:**
- Analyze ban patterns
- Update guidelines if needed
- Train new moderators
