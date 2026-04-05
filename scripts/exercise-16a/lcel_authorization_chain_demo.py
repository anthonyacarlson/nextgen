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
repo_url = "https://github.com/railsbridge/bridge_troll.git"
repo_path = os.path.join(SCRIPT_DIR, "repo")

if not (os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git"))):
    try:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned Bridge Troll into: {repo_path}")
    except Exception as e:
        print("Clone error:", e)
else:
    print("Repo already exists.")

print(f"Repo path: {repo_path}")


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


# ------------------------------------------------------------------------------
# STEP 1: Context Gathering (DeepAgent with filesystem access)
# ------------------------------------------------------------------------------
context_agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,
    system_prompt="""You are gathering context about how authorization works in an application.

The code is available in the current directory. Use ls, read_file, and other file tools to explore
the repository and gather simple notes about where and how authorization appears to be implemented
(e.g., policies, controllers, etc.).

Start by listing the directory structure to understand the codebase layout.

Return a summary of what you found about the authorization implementation.""",
)


def _run_context(task: str) -> dict:
    """Run the context-gathering step and wrap output in a dict for LCEL."""
    result = context_agent.invoke({
        "messages": [{"role": "user", "content": task}]
    })
    summary = result["messages"][-1].content
    print("\n[STEP 1 OUTPUT] Context Summary:\n", summary)
    return {"context": summary}


context_step = RunnableLambda(_run_context)


# ------------------------------------------------------------------------------
# STEP 2: Assessment Plan (NO TOOLS, PURE LCEL)
# ------------------------------------------------------------------------------
plan_prompt = ChatPromptTemplate.from_template(
    """You are writing a simple authorization review plan.

Here is the context you gathered in Step 1:
---
{context}
---

Using ONLY this context, write a short, clear plan for reviewing
authorization in this application. Keep it brief and easy to understand.

In your plan, start with a line like:
"This plan is based on the context gathered in Step 1 above."
"""
)

plan_step = (
    RunnableLambda(
        lambda state: (
            print("\n[STEP 1 OUTPUT -> STEP 2 INPUT] Context:\n", state.get("context", "")),
            state,
        )[1]
    )
    | plan_prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(lambda text: {"plan": text})
)


# ------------------------------------------------------------------------------
# STEP 3: Review (DeepAgent with filesystem access)
# ------------------------------------------------------------------------------
review_agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,
    system_prompt="""You are performing a lightweight authorization review of an application.

The code is available in the current directory. Use ls, read_file, and other file tools to inspect
relevant files or directories related to authorization.

You will receive an assessment plan from a previous step. Follow this plan at a high level.
Return simple, high-level findings.

In your response:
1. First include: "I used the assessment plan from Step 2 above to decide what to review."
2. Print a heading: "Plan from Step 2 used for this review:"
3. Echo the plan text you received (verbatim)
4. Describe what you actually reviewed (files/directories/policies) and what you found.""",
)


def _run_review(state: dict) -> str:
    """Run the review step based on the plan from step 2."""
    plan_text = state.get("plan", "")
    print("\n[STEP 2 OUTPUT -> STEP 3 INPUT] Assessment Plan:\n", plan_text)

    result = review_agent.invoke({
        "messages": [{"role": "user", "content": f"Execute this assessment plan:\n\n{plan_text}"}]
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


def run_authorization_chain(task: str):
    print("\nRunning 3-Step LCEL Authorization Chain...\n")
    result = full_chain.invoke(task)
    print("\n==============================")
    print("FINAL RESULT:\n", result)
    return result


if __name__ == "__main__":
    task = (
        "Learn how authorization appears to work in the Bridge Troll application "
        "and perform a simple authorization review."
    )
    run_authorization_chain(task)
