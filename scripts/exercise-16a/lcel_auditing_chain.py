from deepagents import create_deep_agent
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
repo_url = "https://github.com/railsbridge/bridge_troll.git"
repo_path = "./exercise-16a/repo"

if not (os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git"))):
    try:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned Bridge Troll into: {repo_path}")
    except Exception as e:
        print("Clone error:", e)
else:
    print("Repo already exists.")


# ------------------------------------------------------------------------------
# LLM Setup
# ------------------------------------------------------------------------------
llm = ChatBedrockConverse(
    model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.6,
)


# ------------------------------------------------------------------------------
# STEP 1: Context Gathering (DeepAgent)
# ------------------------------------------------------------------------------
context_agent = create_deep_agent(
    model=llm,
    tools=[],  # DeepAgent has built-in file tools
    system_prompt="""You are gathering context about how auditing and logging works in an application.

The code lives under ./exercise-16a/repo. Explore the repository and gather simple notes
about where and how auditing and logging appears to be implemented (e.g., policies, controllers, etc.).

Return a summary of what you found about the auditing and logging implementation.""",
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
    """You are writing a simple auditing and logging review plan.

Here is the context you gathered in Step 1:
---
{context}
---

Using ONLY this context, write a short, clear plan for reviewing
auditing and logging in this application. Keep it brief and easy to understand.

This plan MUST cover the following points:
- [ ] If an exception occurs, does the application fails securely?
- [ ] Do error messages reveal sensitive application or unnecessary execution details?
- [ ] Are Component, framework, and system errors displayed to end user?
- [ ] Does exception handling that occurs during security sensitive processes release resources safely and roll back any transactions?
- [ ] Are relevant user details and system actions logged?
- [ ] Is sensitive user input flagged, identified, protected, and not written to the logs?
  - [ ] Credit Card #s, Social Security Numbers, Passwords, PII, keys
- [ ] Are unexpected errors and inputs logged?
  - [ ] Multiple login attempts, invalid logins, unauthorized access attempts
- [ ] Are log details should be specific enough to reconstruct events for audit purposes?
  - [ ] Are logging configuration settings configurable through settings or environment variables and not hard-coded into the source?
- [ ] Is user-controlled data validated and/or sanitized before logging to prevent log injection?

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
# STEP 3: Review (DeepAgent)
# ------------------------------------------------------------------------------
review_agent = create_deep_agent(
    model=llm,
    tools=[],  # DeepAgent has built-in file tools
    system_prompt="""You are performing an in-depth auditing and logging review of the app under ./exercise-16a/repo.

You will receive an assessment plan from a previous step. Follow this plan at a high level.
Use your file tools to inspect all relevant files or directories that seem related to auditing and logging.
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


def run_auditing_chain(task: str):
    print("\nRunning 3-Step LCEL Auditing & Logging Chain...\n")
    result = full_chain.invoke(task)
    print("\n==============================")
    print("FINAL RESULT:\n", result)
    return result


if __name__ == "__main__":
    task = (
        "You are an expert code reviewer and application security auditor. Your task is to learn how auditing and logging functions work in the Bridge Troll application "
        "and perform an auditing and logging security review for possible gaps. Utilize all three steps of the LCEL framework to complete this task."
    )
    run_auditing_chain(task)
