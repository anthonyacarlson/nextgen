# Exercise 0x08 - Advanced Agentic AI
## Objective
Build a Multi-Step Security Analysis Workflow

## Instructions
### 1. Run Demo Script
Open _exercise-08/langgraph\_react\_demo.py_ to observe the baseline workflow and output.

Once again, the initial script focuses on the VTM (Vulnerable Task Manager) application, but has the ability to browse directories and view files via tools.

```sh
python exercise-08/langgraph_react_demo.py
```

### 2. Improve Findings
Modify the script to enhance security finding accuracy and coverage. The prompt provided is both broad and unfocused, even though it uses reflection.

```python
instructions = """
You are an agent designed to analyze Python/Django code for vulnerabilities.
The source code is located at ./repo/

### Analysis Process
1. Initial Review:
   - Identify OWASP Top 10 issues
   - Identify Django security issues
   - Find logic flaws

2. Reflection Questions:
   Consider these questions carefully:
   - What are the OWASP Top 10 issues in the code?
   - What are the Django security issues in the code?
   - What are the logic flaws in the code?

3. Challenge Initial Assessment:
   - Is it really insecure
   - Am I certain
   - What would an attacker try first to bypass these controls?
```

### 3. Enhance Reporting
Improve the output format to make it better for readability and actionability.

```py
instructions = """
...
### **Output Format**
Your final response must be in JSON format, containing the following fields:
- `is_insecure`: (bool) Whether the code is considered insecure.
- `reason`: (str) The reason the code is considered insecure or secure.
...
```

### 4. Multi-Step Analysis (Optional)
Add in a new step that utilizes the output from the initial prompt as input to a new call to for report generation. This can be done in the current script or by creating a new script that takes specific input.

### 5. Custom Tools (Optional)
Build a new tool and add it to the tool list for expanded functionality.
