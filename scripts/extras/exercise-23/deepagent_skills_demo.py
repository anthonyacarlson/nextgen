"""
DeepAgent Skills Demo - Exercise 23

This exercise demonstrates how to use DeepAgent Skills to create
reusable, composable security analysis capabilities.

Skills are pre-packaged behaviors that can be attached to agents,
making it easy to share and reuse analysis patterns across projects.
"""

from deepagents import create_deep_agent
from deepagents.skills import Skill
from deepagents.backends import FilesystemBackend
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os
import git

load_dotenv()

# ------------------------------------------------------------------------------
# Git Repo Setup
# ------------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_url = "https://github.com/redpointsec/vtm.git"
repo_path = os.path.join(SCRIPT_DIR, "repo")

if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
    print("Directory already contains a git repository.")
else:
    try:
        repo = git.Repo.clone_from(repo_url, repo_path)
        print(f"Repository cloned into: {repo_path}")
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")

print(f"Repo path: {repo_path}")


# ------------------------------------------------------------------------------
# Define Custom Skills
# ------------------------------------------------------------------------------
class OWASPTop10Skill(Skill):
    """
    Skill for analyzing code against OWASP Top 10 vulnerabilities.

    This skill provides structured guidance for identifying common
    web application security risks.
    """

    name = "owasp_top10_analysis"
    description = "Analyze code for OWASP Top 10 vulnerabilities"

    # The skill's instructions are injected into the agent's context
    instructions = """
## OWASP Top 10 Analysis Skill

When performing OWASP Top 10 analysis, check for these vulnerability categories:

1. **A01:2021 - Broken Access Control**
   - Missing authorization checks on sensitive operations
   - IDOR (Insecure Direct Object References)
   - Path traversal vulnerabilities

2. **A02:2021 - Cryptographic Failures**
   - Weak encryption algorithms
   - Hardcoded secrets or API keys
   - Sensitive data transmitted in cleartext

3. **A03:2021 - Injection**
   - SQL Injection (raw queries, string concatenation)
   - Command Injection (os.system, subprocess with shell=True)
   - Template Injection

4. **A04:2021 - Insecure Design**
   - Missing rate limiting
   - Lack of input validation
   - Trust boundary violations

5. **A05:2021 - Security Misconfiguration**
   - DEBUG=True in production
   - Default credentials
   - Verbose error messages

6. **A06:2021 - Vulnerable Components**
   - Outdated dependencies
   - Known vulnerable libraries

7. **A07:2021 - Authentication Failures**
   - Weak password policies
   - Missing brute-force protection
   - Session fixation

8. **A08:2021 - Data Integrity Failures**
   - Insecure deserialization
   - Missing integrity checks

9. **A09:2021 - Security Logging Failures**
   - Missing audit logs for sensitive operations
   - Logging sensitive data

10. **A10:2021 - SSRF**
    - User-controlled URLs in server-side requests
    - Missing URL validation

For each finding, provide:
- Vulnerability category (A01-A10)
- File and line number
- Code snippet
- Risk rating (High/Medium/Low)
- Remediation recommendation
"""


class DjangoSecuritySkill(Skill):
    """
    Skill for Django-specific security analysis.

    This skill provides expertise on Django's security features
    and common Django-specific vulnerabilities.
    """

    name = "django_security_analysis"
    description = "Analyze Django applications for framework-specific security issues"

    instructions = """
## Django Security Analysis Skill

When analyzing Django applications, pay special attention to:

### Authentication & Authorization
- Check for proper use of `@login_required` decorator
- Verify `@permission_required` or `@user_passes_test` usage
- Look for missing authorization on views that modify data
- Check if `request.user` ownership is validated before operations

### ORM & Database
- **SAFE**: Django ORM methods (filter, get, exclude) auto-escape
- **UNSAFE**: `.raw()`, `.extra()`, `cursor.execute()` with string formatting
- Look for: `Model.objects.raw("SELECT * FROM x WHERE id=" + user_input)`

### Template Security
- Check for `|safe` filter misuse
- Look for `mark_safe()` on user input
- Verify `{% autoescape off %}` blocks

### CSRF Protection
- Ensure `{% csrf_token %}` in forms
- Check for `@csrf_exempt` decorators (should be rare)
- Verify AJAX requests include CSRF token

### Settings Security
- DEBUG should be False in production
- SECRET_KEY should not be hardcoded
- ALLOWED_HOSTS should be configured
- Check SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE

### File Handling
- Validate file uploads (type, size, content)
- Check for path traversal in file operations
- Verify MEDIA_ROOT restrictions

### Common Django Patterns to Flag
```python
# BAD: SQL Injection
User.objects.raw("SELECT * FROM users WHERE name = '%s'" % name)

# BAD: Missing authorization
def delete_item(request, item_id):
    Item.objects.filter(id=item_id).delete()  # No ownership check!

# BAD: XSS via mark_safe
return mark_safe(user_input)

# BAD: Open redirect
return redirect(request.GET.get('next'))
```

For each finding, note if Django provides a built-in protection that was bypassed.
"""


class SecurityReportSkill(Skill):
    """
    Skill for generating structured security reports.

    This skill ensures consistent, professional output format
    for security findings.
    """

    name = "security_report"
    description = "Generate structured security assessment reports"

    instructions = """
## Security Report Generation Skill

Structure your final output as a JSON security report:

```json
{
    "summary": {
        "total_findings": <number>,
        "critical": <number>,
        "high": <number>,
        "medium": <number>,
        "low": <number>
    },
    "findings": [
        {
            "id": "FINDING-001",
            "title": "SQL Injection in user search",
            "severity": "Critical",
            "category": "A03:2021 - Injection",
            "file": "views.py",
            "line": 45,
            "code_snippet": "cursor.execute('SELECT * FROM users WHERE name = ' + name)",
            "description": "User input is directly concatenated into SQL query",
            "impact": "Attacker can extract, modify, or delete database contents",
            "remediation": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE name = %s', [name])"
        }
    ],
    "recommendations": [
        "Implement input validation middleware",
        "Enable Django's security middleware",
        "Add automated SAST to CI/CD pipeline"
    ]
}
```

Severity Ratings:
- **Critical**: Direct path to data breach or system compromise
- **High**: Significant security impact, exploitable with some effort
- **Medium**: Security weakness that requires specific conditions
- **Low**: Minor issue or defense-in-depth recommendation
"""


# ------------------------------------------------------------------------------
# LLM Setup
# ------------------------------------------------------------------------------
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.3,  # Lower temperature for more consistent analysis
)

# Backend for filesystem access
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)


# ------------------------------------------------------------------------------
# Create Agent with Skills
# ------------------------------------------------------------------------------
# Base system prompt - skills will augment this
base_prompt = """You are a security analyst performing a code review.
Use your skills to conduct a thorough security assessment of the codebase.
The source code is available in the current directory.
"""

# Create agent with all three skills attached
agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,
    system_prompt=base_prompt,
    skills=[
        OWASPTop10Skill(),
        DjangoSecuritySkill(),
        SecurityReportSkill(),
    ],
)


# ------------------------------------------------------------------------------
# Analysis Function
# ------------------------------------------------------------------------------
def analyze_with_skills(task: str) -> str:
    """
    Run security analysis using the skill-enhanced agent.
    """
    print("[Agent] Running with skills: owasp_top10, django_security, security_report")
    print("[Agent] Streaming output...")

    final_output = ""
    for event in agent.stream({"messages": [{"role": "user", "content": task}]}):
        for key, value in event.items():
            if "Middleware" in key:
                continue
            if isinstance(value, dict) and "messages" in value:
                for msg in value["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"  -> {tc['name']}")
                    elif hasattr(msg, "content") and msg.content:
                        final_output = msg.content
    return final_output


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("DeepAgent Skills Demo - Security Assessment")
    print("=" * 60)
    print("\nSkills loaded:")
    print("  - OWASP Top 10 Analysis")
    print("  - Django Security Analysis")
    print("  - Security Report Generation")
    print()

    analysis_task = """
Perform a comprehensive security assessment of this Django application.

1. First, explore the directory structure to understand the codebase
2. Identify the main views and models
3. Apply OWASP Top 10 analysis to find vulnerabilities
4. Check for Django-specific security issues
5. Generate a structured security report with your findings

Focus on high-impact vulnerabilities that could lead to data breaches.
"""

    print("Starting analysis...")
    print("-" * 60)
    result = analyze_with_skills(analysis_task)
    print("\n" + "=" * 60)
    print("SECURITY REPORT:")
    print("=" * 60)
    print(result)
