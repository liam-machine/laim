# SharePoint Skill Troubleshooting

Common issues and solutions when working with SharePoint pages.

## Authentication Issues

### "No token available" error

**Cause:** First-time use or expired token cache.

**Solution:**
```bash
# Authenticate interactively
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/_lib/auth.py johnholland --auth
```

### "401 Unauthorized" error

**Cause:** Token expired or insufficient permissions.

**Solutions:**
1. Clear cache and re-authenticate:
   ```bash
   rm ~/.credentials/sp_johnholland_token.json
   # Run any command to trigger re-auth
   ```

2. Ensure you have at least "Edit" permissions on the site

### Device code not working

**Cause:** Browser popup blocked or wrong tenant.

**Solution:**
1. Open the URL manually in your browser
2. Ensure you're logging into the correct Microsoft 365 account
3. Check that the tenant name is correct (e.g., "johnholland" for johnholland.sharepoint.com)

## Page Reading Issues

### "Page not found" error

**Causes:**
- Wrong page name
- Page in a different library
- Missing .aspx extension

**Solutions:**
```bash
# List all pages first
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sharepoint/scripts/sp_pages.py list "https://johnholland.sharepoint.com/sites/MySite"

# Use the exact filename from the list
```

### Empty sections returned

**Cause:** Page may use classic layout or have no canvas content.

**Solution:**
- Classic pages (wiki pages) don't have CanvasContent1
- Check if the page is a modern page in the browser

### "403 Forbidden" error

**Cause:** Site-level permissions or tenant policy blocking API access.

**Solutions:**
1. Verify you can access the site in browser
2. Check with IT if API access is restricted
3. Try using a different site to isolate the issue

## PnP PowerShell Issues

### Module not found

**Solution:**
```powershell
# Install
Install-Module PnP.PowerShell -Scope CurrentUser -Force

# Verify
Get-Module PnP.PowerShell -ListAvailable
```

### Connection fails

**Solutions:**
```powershell
# Clear any existing connections
Disconnect-PnPOnline

# Reconnect with fresh auth
Connect-PnPOnline -Url "https://johnholland.sharepoint.com/sites/MySite" -Interactive -ForceAuthentication
```

### "Set-PnPPageTextPart" fails

**Causes:**
- Wrong InstanceId
- Page checked out by someone else
- Text part doesn't exist

**Solutions:**
1. Get fresh InstanceId:
   ```powershell
   $page = Get-PnPPage -Identity "Home.aspx"
   $page.Controls | ForEach-Object { $_.InstanceId }
   ```

2. Check page status:
   ```powershell
   Get-PnPPage -Identity "Home.aspx" | Select-Object CheckedOutBy
   ```

### Changes not appearing

**Solutions:**
1. Ensure page is published:
   ```powershell
   Set-PnPPage -Identity "Home.aspx" -Publish
   ```

2. Clear browser cache or use Ctrl+F5

3. Check if page is checked out

## REST API Issues

### "500 Internal Server Error"

**Cause:** Invalid request format or server-side issue.

**Solutions:**
1. Check the site URL format
2. Ensure page name includes .aspx
3. Try again later (transient server issues)

### Slow responses

**Cause:** Large pages or network latency.

**Solutions:**
1. Use `--output table` for minimal output
2. Query specific pages instead of listing all

## JHG-Specific Issues

### Site not accessible

Common JHG sites that should work:
- `https://johnholland.sharepoint.com/sites/JHG-VermillionTirana`
- `https://johnholland.sharepoint.com/sites/JHG-TEKGeotechnical`

If a site isn't accessible:
1. Check you have membership in the site's SharePoint group
2. Request access through the site owner
3. Some project sites require specific project team membership

### PnP blocked by tenant policy

If PnP PowerShell connections fail with policy errors:
1. Use the Python REST API for read operations
2. Contact IT about PnP.PowerShell access
3. Use SharePoint web UI for edits as fallback

## Getting Help

1. Check SharePoint site permissions in browser first
2. Run commands with verbose output to see full error messages
3. Test with a personal/test site before production sites
4. For JHG-specific issues, contact IT Service Desk
