# Row-Level Security (RLS) Patterns in Power BI

Row-Level Security restricts data access at the row level based on user identity. This document covers RLS implementation patterns using TMDL, from simple static filters to complex dynamic security hierarchies.

---

## Table of Contents

1. [RLS Overview](#1-rls-overview)
2. [TMDL Syntax for Roles](#2-tmdl-syntax-for-roles)
3. [Static RLS Patterns](#3-static-rls-patterns)
4. [Dynamic RLS Patterns](#4-dynamic-rls-patterns)
5. [Hierarchical Security](#5-hierarchical-security)
6. [Testing RLS](#6-testing-rls)
7. [Performance Considerations](#7-performance-considerations)
8. [Common Mistakes](#8-common-mistakes)

---

## 1. RLS Overview

### What is Row-Level Security?

RLS filters data at the row level based on the identity of the user viewing the report. When enabled:

- Users only see data they're authorized to access
- Filters are applied automatically to every query
- Security is enforced in both Power BI Service and embedded scenarios

### Core Components

| Component | Description |
|-----------|-------------|
| **Role** | Named security configuration with filter rules |
| **Table Permission** | DAX filter expression applied to a table |
| **Member** | User or group assigned to a role |

### Static vs Dynamic RLS

| Type | Description | Use When |
|------|-------------|----------|
| **Static RLS** | Hard-coded filter values in DAX | Fixed user groups, regions, departments |
| **Dynamic RLS** | Filter based on logged-in user identity | Per-user data access, self-service security |

### Who RLS Applies To

RLS only restricts data access for users with **Viewer** permissions:

| Permission Level | RLS Applied? |
|-----------------|--------------|
| Viewer | Yes |
| Contributor | No |
| Member | No |
| Admin | No |

---

## 2. TMDL Syntax for Roles

### Basic Role Structure

```tmdl
role 'Sales Region Managers'
    modelPermission: read

    tablePermission Sales = [Region] = "West"
```

### Complete Role Example

```tmdl
role 'Regional Sales'
    modelPermission: read
    description: "Restricts sales data by region"

    tablePermission Sales = 'Sales'[Region] = "West"

    member 'user1@company.com'
    member 'user2@company.com'
    member 'sales-west-group@company.com' = group
```

### Role Properties

| Property | Required | Description |
|----------|----------|-------------|
| `modelPermission` | Yes | Must be `read` for RLS |
| `description` | No | Human-readable description |
| `tablePermission` | Yes | DAX filter per table |
| `member` | No | Users/groups assigned (Service only) |

### Table Permission Syntax

```tmdl
tablePermission <TableName> = <DAX Boolean Expression>
```

The DAX expression must return TRUE for rows the user can see.

### Member Assignment Types

```tmdl
role 'Example Role'
    modelPermission: read

    // Individual user (Azure AD/Entra ID)
    member 'user@company.com'

    // Security group
    member 'security-group@company.com' = group

    // Auto-detect type
    member 'entity@company.com' = auto

    // Windows Active Directory
    member company\username = activeDirectory
    member company\groupname = activeDirectory
```

### Object-Level Security (OLS)

Hide columns or tables from specific roles:

```tmdl
role 'Hide Salary'
    modelPermission: read

    tablePermission Employee
        metadataPermission: read
        columnPermission Salary = none
        columnPermission SSN = none

role 'Hide HR Table'
    modelPermission: read

    tablePermission HR_Confidential
        metadataPermission: none
```

---

## 3. Static RLS Patterns

### Simple Value Filter

Restrict to a single value:

```tmdl
role 'West Region'
    modelPermission: read

    tablePermission Sales = [Region] = "West"
```

### Multiple Values (OR)

Allow multiple values:

```tmdl
role 'West and Central Regions'
    modelPermission: read

    tablePermission Sales =
        [Region] = "West" || [Region] = "Central"
```

Or using IN:

```tmdl
role 'Multiple Regions'
    modelPermission: read

    tablePermission Sales = [Region] IN {"West", "Central", "East"}
```

### Multiple Conditions (AND)

Combine conditions:

```tmdl
role 'West Premium Sales'
    modelPermission: read

    tablePermission Sales =
        [Region] = "West" && [CustomerTier] = "Premium"
```

### Multiple Tables

Apply filters to multiple related tables:

```tmdl
role 'West Region Complete'
    modelPermission: read

    /// Filter the fact table
    tablePermission Sales = [Region] = "West"

    /// Also filter the customer dimension
    tablePermission Customers = [Region] = "West"

    /// And the employee table
    tablePermission Employees = [Region] = "West"
```

### Excluding Values

Show all except specific values:

```tmdl
role 'Non-Confidential'
    modelPermission: read

    tablePermission Products =
        NOT([Category] IN {"Internal", "Prototype", "Restricted"})
```

### Date-Based Static Filter

Restrict to specific date ranges:

```tmdl
role 'Current Year Only'
    modelPermission: read

    tablePermission Sales =
        YEAR([OrderDate]) = YEAR(TODAY())

role 'Last 12 Months'
    modelPermission: read

    tablePermission Sales =
        [OrderDate] >= DATE(YEAR(TODAY()) - 1, MONTH(TODAY()), DAY(TODAY()))
```

---

## 4. Dynamic RLS Patterns

### User Identity Functions

| Function | Returns | Example |
|----------|---------|---------|
| `USERPRINCIPALNAME()` | UPN (email) | user@company.com |
| `USERNAME()` | Domain\User or UPN | DOMAIN\user or user@company.com |
| `CUSTOMDATA()` | Custom string passed via embed | Any custom value |

**Best Practice:** Use `USERPRINCIPALNAME()` for Azure AD/Microsoft 365 environments.

### Direct User Match

Filter where data matches logged-in user:

```tmdl
role 'Sales Rep Own Data'
    modelPermission: read

    tablePermission Sales =
        [SalesPersonEmail] = USERPRINCIPALNAME()
```

### Lookup Table Pattern

Use a security mapping table for flexible user-to-data assignments:

**Security Table Structure:**
```
UserSecurity
├── UserEmail (string)
├── Region (string)
├── CanSeeAllData (boolean)
└── AccessLevel (string)
```

**TMDL Role:**

```tmdl
role 'Dynamic Region Access'
    modelPermission: read

    tablePermission Sales =
        VAR UserRegions =
            CALCULATETABLE(
                VALUES('UserSecurity'[Region]),
                'UserSecurity'[UserEmail] = USERPRINCIPALNAME()
            )
        RETURN
            [Region] IN UserRegions
```

### Multiple Access Patterns

Combine user-specific access with admin override:

```tmdl
role 'Sales with Admin Override'
    modelPermission: read

    tablePermission Sales =
        /// User's own sales
        [SalesPersonEmail] = USERPRINCIPALNAME()
        /// OR user has "See All" permission
        || LOOKUPVALUE(
            'UserSecurity'[CanSeeAll],
            'UserSecurity'[UserEmail], USERPRINCIPALNAME()
        ) = TRUE()
```

### Multi-Value User Permissions

When users can have access to multiple regions:

```tmdl
role 'Multi-Region Access'
    modelPermission: read

    tablePermission Sales =
        CONTAINS(
            FILTER(
                'UserSecurity',
                'UserSecurity'[UserEmail] = USERPRINCIPALNAME()
            ),
            'UserSecurity'[Region], [Region]
        )
```

**Better Performance Alternative (using relationships):**

```tmdl
role 'Multi-Region via Relationship'
    modelPermission: read

    /// Filter the security bridge table
    tablePermission UserRegionBridge =
        [UserEmail] = USERPRINCIPALNAME()
```

The filter propagates through relationships to Sales automatically.

### Department-Based Security

```tmdl
role 'Department Data Only'
    modelPermission: read

    tablePermission Employees =
        [Department] = LOOKUPVALUE(
            'UserSecurity'[Department],
            'UserSecurity'[UserEmail], USERPRINCIPALNAME()
        )

    tablePermission Budget =
        [Department] = LOOKUPVALUE(
            'UserSecurity'[Department],
            'UserSecurity'[UserEmail], USERPRINCIPALNAME()
        )
```

---

## 5. Hierarchical Security

### Manager Sees Team Data Pattern

Use the PATH function for organizational hierarchies.

**Employee Table with Hierarchy:**
```
Employees
├── EmployeeID
├── EmployeeEmail
├── ManagerID (self-referencing)
└── HierarchyPath (calculated column)
```

**Calculate Hierarchy Path:**

```dax
HierarchyPath = PATH(Employees[EmployeeID], Employees[ManagerID])
```

This creates paths like: `1|5|12|45` (CEO -> VP -> Director -> Employee)

**TMDL Role for Hierarchical Access:**

```tmdl
role 'Manager Hierarchy Access'
    modelPermission: read

    tablePermission Employees =
        VAR CurrentUserID =
            LOOKUPVALUE(
                'Employees'[EmployeeID],
                'Employees'[EmployeeEmail], USERPRINCIPALNAME()
            )
        RETURN
            PATHCONTAINS([HierarchyPath], CurrentUserID)

    tablePermission Sales =
        VAR CurrentUserID =
            LOOKUPVALUE(
                'Employees'[EmployeeID],
                'Employees'[EmployeeEmail], USERPRINCIPALNAME()
            )
        VAR AllowedEmployees =
            FILTER(
                ALL('Employees'),
                PATHCONTAINS('Employees'[HierarchyPath], CurrentUserID)
            )
        RETURN
            [EmployeeID] IN SELECTCOLUMNS(AllowedEmployees, "ID", [EmployeeID])
```

### Simplified Hierarchy with Security Table

Create a pre-computed security mapping:

**UserAccessibleEmployees Table:**
```
UserAccessibleEmployees
├── ManagerEmail
└── CanAccessEmployeeID
```

**TMDL Role:**

```tmdl
role 'Precomputed Hierarchy'
    modelPermission: read

    tablePermission UserAccessibleEmployees =
        [ManagerEmail] = USERPRINCIPALNAME()
```

Filter propagates through relationships to employee data.

### Tiered Access Levels

```tmdl
role 'Tiered Access'
    modelPermission: read

    tablePermission Sales =
        VAR UserLevel =
            LOOKUPVALUE(
                'UserSecurity'[AccessLevel],
                'UserSecurity'[UserEmail], USERPRINCIPALNAME()
            )
        RETURN
            SWITCH(
                TRUE(),
                UserLevel = "Global", TRUE(),
                UserLevel = "Region", [Region] = LOOKUPVALUE(
                    'UserSecurity'[Region],
                    'UserSecurity'[UserEmail], USERPRINCIPALNAME()
                ),
                UserLevel = "Country", [Country] = LOOKUPVALUE(
                    'UserSecurity'[Country],
                    'UserSecurity'[UserEmail], USERPRINCIPALNAME()
                ),
                FALSE()
            )
```

---

## 6. Testing RLS

### View as Role in Power BI Desktop

1. Go to **Modeling** tab
2. Click **View as**
3. Select role(s) to test
4. Optionally enter a user email to test dynamic RLS
5. Report shows data as that role would see it

### Testing Dynamic RLS

To test `USERPRINCIPALNAME()` functions:

1. In **View as** dialog, check "Other user"
2. Enter the email address to simulate
3. Check the role being tested
4. View the report as that user would see it

### DAX Query Testing

Test RLS filters using DAX queries in DAX Studio or Power BI Desktop:

```dax
// Test what a specific user would see
DEFINE
    VAR TestUser = "john.smith@company.com"

EVALUATE
CALCULATETABLE(
    SUMMARIZE(
        Sales,
        Sales[Region],
        "Row Count", COUNTROWS(Sales)
    ),
    // Simulate the RLS filter
    'Sales'[SalesPersonEmail] = TestUser
)
```

### Debug Measure

Add a measure to verify RLS is working:

```dax
Who Am I = USERPRINCIPALNAME()
```

Add this to a card visual. When testing:
- Shows actual logged-in user in Service
- Shows test user email when using "View as"

### Testing Checklist

| Test | Verification |
|------|--------------|
| Correct user gets correct data | Check row counts match expectations |
| User cannot see other users' data | Filter should exclude others |
| Admin/override users see all | Test users with elevated access |
| Blank user returns no data | Ensure no data leakage for unknown users |
| Filter propagates through relationships | Check related tables are filtered |
| Performance is acceptable | Test with realistic data volumes |

### Common Test Scenarios

```dax
// 1. Verify row count by user
EVALUATE
ROW(
    "User", USERPRINCIPALNAME(),
    "Visible Rows", COUNTROWS(Sales),
    "Expected Rows", 1234  // Fill in expected
)

// 2. List accessible regions
EVALUATE
VALUES(Sales[Region])

// 3. Check if specific sensitive row is hidden
EVALUATE
FILTER(
    Sales,
    Sales[CustomerID] = "CONFIDENTIAL-001"  // Should return empty
)
```

---

## 7. Performance Considerations

### Use Relationships Instead of LOOKUPVALUE

**Slower (row-by-row lookup):**

```tmdl
role 'Slow Pattern'
    modelPermission: read

    tablePermission Sales =
        LOOKUPVALUE(
            'UserSecurity'[Region],
            'UserSecurity'[UserEmail], USERPRINCIPALNAME()
        ) = [Region]
```

**Faster (relationship-based):**

```tmdl
role 'Fast Pattern'
    modelPermission: read

    /// Filter security table, let relationship propagate
    tablePermission UserSecurity =
        [UserEmail] = USERPRINCIPALNAME()
```

### Filter Dimension Tables, Not Fact Tables

Apply RLS to dimension tables and let filters propagate:

**Less efficient:**

```tmdl
role 'Filter Fact'
    modelPermission: read

    tablePermission Sales = [Region] = "West"  // Filters millions of rows
```

**More efficient:**

```tmdl
role 'Filter Dimension'
    modelPermission: read

    tablePermission Geography = [Region] = "West"  // Filters few rows, propagates
```

### Avoid CONTAINS with Large Tables

**Slow:**

```dax
CONTAINS(
    'LargeSecurityTable',
    'LargeSecurityTable'[UserEmail], USERPRINCIPALNAME(),
    'LargeSecurityTable'[Region], [Region]
)
```

**Faster:**

```dax
// Pre-filter the security table first
VAR CurrentUserSecurity =
    FILTER(
        'UserSecurity',
        'UserSecurity'[UserEmail] = USERPRINCIPALNAME()
    )
RETURN
    [Region] IN SELECTCOLUMNS(CurrentUserSecurity, "R", [Region])
```

### Bidirectional Filtering Implications

Enabling "Apply security filter in both directions" can:
- Cause performance degradation
- Create ambiguous filter paths
- Lead to unexpected results with complex models

**When to use bidirectional security filtering:**
- Required for many-to-many security scenarios
- User needs to see filtered dimension values only

**Risks:**
- Only one bidirectional relationship per table allowed
- Can expose data if not carefully configured
- May significantly slow queries

### Pre-Compute Security Mappings

For complex hierarchies, materialize security in ETL:

1. Create `UserDataAccess` table during refresh
2. Columns: UserEmail, AccessibleEntityID, AccessLevel
3. Simple RLS filter on this table
4. Relationship propagates to data tables

---

## 8. Common Mistakes

### Forgetting Related Tables

**Problem:** User can't see data in one table but security wasn't applied to related tables.

```tmdl
role 'Incomplete Security'
    modelPermission: read

    tablePermission Sales = [Region] = "West"
    // Missing: tablePermission Customers, tablePermission Products
```

**Solution:** Ensure all tables that could expose sensitive data have appropriate filters, or rely on relationship propagation from a single filtered table.

### Using Wrong User Function

| Environment | Recommended Function |
|-------------|---------------------|
| Power BI Service | `USERPRINCIPALNAME()` |
| Power BI Embedded (Azure AD) | `USERPRINCIPALNAME()` |
| Power BI Embedded (Custom) | `CUSTOMDATA()` |
| On-premises (SSAS) | `USERNAME()` |

### Not Handling Admin/Manager Users

**Problem:** Admins see no data because they don't match the RLS filter.

**Solution:** Add admin override logic:

```tmdl
role 'With Admin Override'
    modelPermission: read

    tablePermission Sales =
        [SalesPersonEmail] = USERPRINCIPALNAME()
        || LOOKUPVALUE(
            'AdminUsers'[IsAdmin],
            'AdminUsers'[Email], USERPRINCIPALNAME()
        ) = TRUE()
```

### Case Sensitivity Issues

DAX string comparisons are case-insensitive by default, but email addresses in security tables might have inconsistent casing.

**Problem:**
- Security table: "John.Smith@company.com"
- USERPRINCIPALNAME() returns: "john.smith@company.com"

**Solution:** Use LOWER() or UPPER() consistently:

```tmdl
role 'Case Insensitive'
    modelPermission: read

    tablePermission UserSecurity =
        LOWER([UserEmail]) = LOWER(USERPRINCIPALNAME())
```

### Blank Values Returning All Data

**Problem:** If LOOKUPVALUE returns BLANK for unknown user, comparison might pass.

```dax
// Dangerous: BLANK() = BLANK() returns TRUE
[Region] = LOOKUPVALUE(...)  // If no match, compares [Region] = BLANK()
```

**Solution:** Handle BLANK explicitly:

```tmdl
role 'Handle Blank'
    modelPermission: read

    tablePermission Sales =
        VAR UserRegion =
            LOOKUPVALUE(
                'UserSecurity'[Region],
                'UserSecurity'[UserEmail], USERPRINCIPALNAME()
            )
        RETURN
            NOT(ISBLANK(UserRegion)) && [Region] = UserRegion
```

### Testing Only in Desktop

**Problem:** RLS works in Desktop "View as" but fails in Service.

**Causes:**
- Different UPN format in Service vs testing
- Group membership not synced
- Conditional access policies interfering

**Solution:** Always test in Power BI Service with actual user accounts.

### Circular Relationships with RLS

**Problem:** Bidirectional relationships can create circular filter paths.

**Solution:**
- Minimize bidirectional relationships
- Use CROSSFILTER in measures instead of model bidirectional
- Carefully plan star schema to avoid ambiguity

### Summary: RLS Checklist

| Item | Check |
|------|-------|
| All sensitive tables have filters | Apply to dimension tables, let propagate |
| Admin override exists | Ensure admins/managers can see data |
| Unknown users get no data | ISBLANK check on user lookup |
| Case handling is consistent | Use LOWER() or UPPER() |
| Tested in Power BI Service | Not just Desktop "View as" |
| Performance is acceptable | Use relationships over LOOKUPVALUE |
| Bidirectional filters are intentional | Understand implications |
| Documentation exists | Document who has access to what |

---

## References

- [Row-level security (RLS) with Power BI - Microsoft Learn](https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security)
- [RLS Guidance - Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/guidance/rls-guidance)
- [Dynamic Row Level Security - RADACAD](https://radacad.com/dynamic-row-level-security-with-power-bi-made-simple/)
- [Hierarchical RLS in Power BI - Power BI Docs](https://powerbidocs.com/2025/02/25/dynamic-row-level-security-rls-in-power-bi-with-organizational-hierarchy-explained/)
- [TMDL View in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-tmdl-view)
