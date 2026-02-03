# PnP PowerShell Commands Reference

Complete reference for SharePoint page editing with PnP PowerShell.

## Installation

```powershell
# Install PnP.PowerShell module
Install-Module PnP.PowerShell -Scope CurrentUser

# Or update if already installed
Update-Module PnP.PowerShell
```

## Connection

```powershell
# Interactive login (browser popup)
Connect-PnPOnline -Url "https://tenant.sharepoint.com/sites/SiteName" -Interactive

# Check connection
Get-PnPConnection
```

## Page Operations

### Get Page Information

```powershell
# List all pages
Get-PnPPage

# Get specific page
Get-PnPPage -Identity "Home.aspx"

# Get page with component details
$page = Get-PnPPage -Identity "Home.aspx"
$page.Sections
$page.Controls
```

### Create a New Page

```powershell
# Create blank page
Add-PnPPage -Name "NewPage" -Title "My New Page"

# Create from template
Add-PnPPage -Name "NewPage" -Title "My New Page" -LayoutType Article

# Layout types: Article, Home, SingleWebPartAppPage, RepostPage, HeaderlessSearchResults
```

### Delete a Page

```powershell
Remove-PnPPage -Identity "PageToDelete.aspx" -Force
```

## Section Operations

### Add Sections

```powershell
# Add a one-column section
Add-PnPPageSection -Page "Home.aspx" -SectionTemplate OneColumn -Order 1

# Add a two-column section
Add-PnPPageSection -Page "Home.aspx" -SectionTemplate TwoColumn -Order 2

# Section templates:
# - OneColumn
# - OneColumnFullWidth
# - TwoColumn
# - TwoColumnLeft (1/3 + 2/3)
# - TwoColumnRight (2/3 + 1/3)
# - ThreeColumn
# - ThreeColumnFullWidth
```

### Add Section with Background

```powershell
Add-PnPPageSection -Page "Home.aspx" -SectionTemplate OneColumn -Order 1 -ZoneEmphasis 1

# ZoneEmphasis values:
# 0 = None (default)
# 1 = Neutral
# 2 = Soft
# 3 = Strong
```

## Text Web Part Operations

### Add Text Web Part

```powershell
# Add text to specific section/column
Add-PnPPageTextPart -Page "Home.aspx" -Text "<h2>Title</h2><p>Content here</p>" -Section 1 -Column 1

# Add text with order (position within column)
Add-PnPPageTextPart -Page "Home.aspx" -Text "<p>More content</p>" -Section 1 -Column 1 -Order 2
```

### Edit Existing Text Web Part

```powershell
# You need the InstanceId from Get-PnPPage or the REST API
Set-PnPPageTextPart -Page "Home.aspx" -InstanceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -Text "<p>Updated content</p>"
```

### HTML Formatting in Text Parts

```html
<!-- Supported HTML elements -->
<h1>, <h2>, <h3>     - Headings
<p>                   - Paragraphs
<strong>, <b>         - Bold
<em>, <i>             - Italic
<u>                   - Underline
<a href="">           - Links
<ul>, <ol>, <li>      - Lists
<blockquote>          - Quotes
<code>                - Inline code
```

## Web Part Operations

### Add Built-in Web Parts

```powershell
# Add Image web part
Add-PnPPageWebPart -Page "Home.aspx" -DefaultWebPartType Image -Section 1 -Column 1

# Add Quick Links
Add-PnPPageWebPart -Page "Home.aspx" -DefaultWebPartType QuickLinks -Section 1 -Column 1

# Common web part types:
# - Image
# - ImageGallery
# - QuickLinks
# - News
# - Events
# - Hero
# - Button
# - Divider
# - Spacer
# - YouTube
# - Bing Maps
# - Weather
# - Code Snippet
```

### Remove Web Part

```powershell
# Remove by instance ID
Remove-PnPPageComponent -Page "Home.aspx" -InstanceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -Force
```

## Page Header Operations

### Set Page Header

```powershell
# Set header image
Set-PnPPage -Identity "Home.aspx" -HeaderType Custom -HeaderImage "/sites/SiteName/SiteAssets/header.jpg"

# Header types:
# - Default
# - Custom
# - None
# - ColorBlock
```

### Set Header Layout

```powershell
Set-PnPPage -Identity "Home.aspx" -LayoutType Article -HeaderLayoutType FullWidthImage
```

## Publishing

### Publish a Page

```powershell
# Save and publish
Set-PnPPage -Identity "Home.aspx" -Publish

# Just save (keep as draft)
Set-PnPPage -Identity "Home.aspx"
```

### Check Out/In

```powershell
# Check out for editing
Set-PnPPage -Identity "Home.aspx" -CheckOut

# Check in
Set-PnPPage -Identity "Home.aspx" -CheckIn
```

## Complete Workflow Example

```powershell
# 1. Connect
Connect-PnPOnline -Url "https://johnholland.sharepoint.com/sites/JHG-VermillionTirana" -Interactive

# 2. Create new page
Add-PnPPage -Name "ProjectUpdate" -Title "Project Update - February 2024"

# 3. Add sections
Add-PnPPageSection -Page "ProjectUpdate.aspx" -SectionTemplate OneColumn -Order 1
Add-PnPPageSection -Page "ProjectUpdate.aspx" -SectionTemplate TwoColumn -Order 2

# 4. Add content
Add-PnPPageTextPart -Page "ProjectUpdate.aspx" -Section 1 -Column 1 -Text @"
<h2>February Update</h2>
<p>This month we achieved the following milestones:</p>
<ul>
<li>Milestone 1 completed</li>
<li>Milestone 2 in progress</li>
</ul>
"@

# 5. Add image (left column of section 2)
Add-PnPPageWebPart -Page "ProjectUpdate.aspx" -DefaultWebPartType Image -Section 2 -Column 1

# 6. Publish
Set-PnPPage -Identity "ProjectUpdate.aspx" -Publish

Write-Host "Page created and published!"
```

## Troubleshooting

### "Access denied" errors
- Ensure you have Edit permissions on the site
- Try disconnecting and reconnecting: `Disconnect-PnPOnline` then `Connect-PnPOnline`

### "Page not found" errors
- Include .aspx extension in page name
- Check spelling and case sensitivity

### Changes not appearing
- Page may be checked out by another user
- Try forcing publish: `Set-PnPPage -Identity "Page.aspx" -Publish -Force`

### Module not found
- Ensure PnP.PowerShell is installed: `Get-Module PnP.PowerShell -ListAvailable`
- Import module: `Import-Module PnP.PowerShell`
