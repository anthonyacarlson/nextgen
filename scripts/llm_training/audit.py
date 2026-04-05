from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os
import git

load_dotenv()

# ------------------------------------------------------------------------------
# Git Repo Setup
# ------------------------------------------------------------------------------
repo_url = "https://github.com/haiwen/seafile"
repo_path = "./repo"

if not (os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git"))):
    try:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned Seafile into: {repo_path}")
    except Exception as e:
        print("Clone error:", e)
else:
    print("Repo already exists.")


# ------------------------------------------------------------------------------
# LLM Setup
# ------------------------------------------------------------------------------
PLAN_LLM = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

EXEC_LLM = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.1,
)


# ------------------------------------------------------------------------------
# Step Factory
# ------------------------------------------------------------------------------
def new_step(name, llm):
    """Create a DeepAgent step that loads its system prompt from a file.

    Args:
        name: Name of the step (used to load prompts/{name}.txt)
        llm: The LLM to use for this step

    Returns:
        A RunnableLambda that can be chained in an LCEL pipeline
    """
    # Load the system prompt from file
    with open(f"prompts/{name}.txt") as fh:
        system_prompt = fh.read()

    # Add context about the repo location
    system_prompt += "\n\nThe source code for the application you are reviewing is accessible at ./repo/"

    # Create the DeepAgent - no custom tools needed, DeepAgent has built-ins
    agent = create_deep_agent(
        model=llm,
        tools=[],  # DeepAgent provides file tools (read_file, ls, glob, grep, etc.)
        system_prompt=system_prompt,
    )

    def _run_step(input_text: str) -> str:
        print(f"\n[{name.upper()} STEP INPUT]\n", input_text)
        result = agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })
        output = result["messages"][-1].content
        print(f"\n[{name.upper()} STEP RESULT]\n", output)

        # Save step output to file for reference
        os.makedirs("steps", exist_ok=True)
        with open(f"steps/{name}.txt", "w") as fh:
            fh.write(output)

        return output

    return RunnableLambda(_run_step)


def get_output(step_name):
    """Read the saved output from a previous step."""
    with open(f"steps/{step_name}.txt") as fh:
        return fh.read()


# ------------------------------------------------------------------------------
# Chain Definitions
# ------------------------------------------------------------------------------
info_step = new_step(name="info", llm=PLAN_LLM)
plan_step = new_step(name="plan", llm=PLAN_LLM)
scan_step = new_step(name="scan", llm=EXEC_LLM)

# Full chain - currently just info_step, uncomment to add more
full_chain = (
    RunnableLambda(lambda input: input)
    | info_step
    # | plan_step
    # | scan_step
)


if __name__ == "__main__":
    full_chain.invoke(
        "You are an expert code reviewer and application security auditor. "
        "I will give you instructions and you need to follow them precisely."
    )
