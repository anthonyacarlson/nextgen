from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os
import git

load_dotenv()

# ------------------------------------------------------------------------------
# Git Repo Setup
# ------------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_url = "https://github.com/MISP/MISP.git"
repo_path = os.path.join(SCRIPT_DIR, "group-exercise", "repo")

if not (os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git"))):
    try:
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned MISP into: {repo_path}")
    except Exception as e:
        print("Clone error:", e)
else:
    print("Repo already exists.")


# ------------------------------------------------------------------------------
# LLM Setup
# ------------------------------------------------------------------------------
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.0,
)

# Backend for local filesystem access - points to the repo directory
# virtual_mode=True restricts access to root_dir only (recommended for security)
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)

print(f"Repo path: {repo_path}")


# ------------------------------------------------------------------------------
# STEP 1: Context Gathering (DeepAgent)
# ------------------------------------------------------------------------------
context_agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,
    system_prompt="""You are a security researcher gathering context about how remote code execution (RCE) could be achieved in the examined application.

The code is available in the current directory. Use ls, read_file, and other file tools to explore
the repository and identify files that could contain RCE vulnerabilities such as:
- Command execution (exec, system, shell_exec, passthru, popen, etc.)
- Code evaluation (eval, assert, preg_replace with /e, create_function, etc.)
- Deserialization (unserialize, json_decode with object instantiation, etc.)
- File inclusion (include, require, file_get_contents with user input, etc.)
- Process spawning and external program execution

Start by listing the directory structure to understand the codebase layout.

You must provide a minimum of 10 files.

Your response MUST be a structured list in this exact format:
```
FILES TO REVIEW FOR RCE:
1. [file path] - [brief reason why this file may contain RCE vectors]
2. [file path] - [brief reason]
...
```""",
)


def _run_context(task: str) -> dict:
    """Run the context-gathering step and wrap output in a dict for LCEL."""
    result = context_agent.invoke({
        "messages": [{"role": "user", "content": task}]
    })
    summary = result["messages"][-1].content
    print("\n[STEP 1 OUTPUT] Context Summary:\n", summary)
    return {"context": summary, "original_task": task}


context_step = RunnableLambda(_run_context)


# ------------------------------------------------------------------------------
# STEP 2: Assessment Plan (NO TOOLS, PURE LCEL)
# ------------------------------------------------------------------------------
plan_prompt = ChatPromptTemplate.from_template(
    """You are creating a code review plan focused on finding Remote Code Execution (RCE) vulnerabilities.

Here is the original user request:
---
{original_task}
---

Here are the files identified in Step 1 as potentially containing RCE vectors:
---
{context}
---

Create a focused, actionable plan to review these files for RCE vulnerabilities. For each file listed above:
1. Specify what RCE patterns to look for (command execution, eval, deserialization, file inclusion, etc.)
2. Note what user-controlled inputs could reach dangerous functions
3. Identify what sanitization or validation to check for

You MUST include EVERY file from the context above in your plan.
If the user requested specific files, prioritize those.

Output format:
```
RCE CODE REVIEW PLAN

File: [path]
- Check for: [specific RCE patterns]
- User input vectors: [how user data reaches this code]
- Validation needed: [what to verify]

[repeat for each file]
```
"""
)


def _run_plan(state: dict) -> dict:
    """Run the plan step and preserve the original task."""
    print("\n[STEP 1 OUTPUT -> STEP 2 INPUT] Context:\n", state.get("context", ""))

    result = plan_prompt | llm | StrOutputParser()
    plan_text = result.invoke({
        "context": state.get("context", ""),
        "original_task": state.get("original_task", ""),
    })

    return {"plan": plan_text, "original_task": state.get("original_task", "")}


plan_step = RunnableLambda(_run_plan)


# ------------------------------------------------------------------------------
# STEP 3: Review (DeepAgent)
# ------------------------------------------------------------------------------
review_agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,
    system_prompt="""You are executing an RCE-focused code review plan.

The code is available in the current directory. You must review ALL code files mentioned in the plan.
For each file, use your file tools to read the code and identify actual RCE vulnerabilities.

Provide detailed findings for each file reviewed.""",
)


def _run_review(state: dict) -> str:
    """Run the review step based on the plan from step 2."""
    plan_text = state.get("plan", "")
    original_task = state.get("original_task", "")

    combined_input = f"Original User Request:\n{original_task}\n\nPlan to Execute:\n{plan_text}"

    print("\n[STEP 2 OUTPUT -> STEP 3 INPUT] Assessment Plan:\n", plan_text)
    print("\n[ORIGINAL TASK PRESERVED]:\n", original_task)

    result = review_agent.invoke({
        "messages": [{"role": "user", "content": combined_input}]
    })
    output = result["messages"][-1].content
    print("\n[STEP 3 OUTPUT] Review Findings:\n", output)
    return output


review_step = RunnableLambda(_run_review)


# ------------------------------------------------------------------------------
# FULL LCEL PIPELINE: task -> context -> plan -> review
# ------------------------------------------------------------------------------
full_chain = (
    RunnableLambda(lambda task: task)
    | context_step
    | plan_step
    | review_step
)


def run_rce_chain(task: str):
    print("\nRunning 3-Step LCEL RCE Review Chain...\n")
    result = full_chain.invoke(task)
    print("\n==============================")
    print("FINAL RESULT:\n", result)
    return result


if __name__ == "__main__":
    task = """You are a skilled security engineer who detects remote code execution flaws exclusively."""
    run_rce_chain(task)
