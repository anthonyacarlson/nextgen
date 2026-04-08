---
name: django-security
description: "Use this skill when analyzing Django applications for framework-specific security issues and best practices."
license: MIT
metadata:
  author: absoluteappsec
  version: "1.0"
---

# Django Security Analysis Skill

## Overview
This skill provides expertise on Django's security features and common Django-specific vulnerabilities.

## Instructions

When analyzing Django applications, pay special attention to:

### Authentication & Authorization

Check for proper use of decorators:
- `@login_required` - ensures user is authenticated
- `@permission_required` - checks specific permissions
- `@user_passes_test` - custom authorization logic

Look for missing authorization on views that modify data. Verify `request.user` ownership is validated before operations.

### ORM & Database Security

**SAFE** - Django ORM methods automatically escape:
- `Model.objects.filter()`
- `Model.objects.get()`
- `Model.objects.exclude()`

**UNSAFE** - These can have SQL injection:
- `.raw()` with string formatting
- `.extra()` with user input
- `cursor.execute()` with concatenation

Example vulnerable pattern:
```python
# BAD: SQL Injection
User.objects.raw("SELECT * FROM users WHERE name = '%s'" % name)

# GOOD: Parameterized
User.objects.raw("SELECT * FROM users WHERE name = %s", [name])
```

### Template Security

- Check for `|safe` filter misuse on user input
- Look for `mark_safe()` on untrusted data
- Verify `{% autoescape off %}` blocks don't include user content

### CSRF Protection

- Ensure `{% csrf_token %}` in all POST forms
- Check for `@csrf_exempt` decorators (should be rare and justified)
- Verify AJAX requests include CSRF token in headers

### Settings Security

Check settings.py for:
- `DEBUG = False` in production
- `SECRET_KEY` not hardcoded (use environment variables)
- `ALLOWED_HOSTS` properly configured
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_SSL_REDIRECT = True`

### Common Vulnerable Patterns

```python
# BAD: IDOR - No ownership check
def delete_item(request, item_id):
    Item.objects.filter(id=item_id).delete()

# GOOD: Ownership verified
def delete_item(request, item_id):
    Item.objects.filter(id=item_id, owner=request.user).delete()

# BAD: XSS via mark_safe
return mark_safe(user_input)

# BAD: Open redirect
return redirect(request.GET.get('next'))

# GOOD: Validate redirect URL
from django.utils.http import url_has_allowed_host_and_scheme
next_url = request.GET.get('next')
if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
    return redirect(next_url)
```

### File Upload Security

- Validate file types (don't trust Content-Type header)
- Check file size limits
- Sanitize filenames
- Store uploads outside web root or use proper MEDIA_ROOT configuration

## Output Format

For each Django-specific finding, note:
- Whether Django provides a built-in protection that was bypassed
- The secure Django pattern that should be used instead
