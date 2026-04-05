from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_aws import ChatBedrockConverse
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os
import git

load_dotenv()

# ------------------------------------------------------------------------------
# Git Repo Setup
# ------------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_url = "https://github.com/haiwen/seafile"
repo_path = os.path.join(SCRIPT_DIR, "repo")

if not (os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git"))):
    try:
        git.Repo.clone_from(repo_url, repo_path)
        print(f"Cloned Seafile into: {repo_path}")
    except Exception as e:
        print("Clone error:", e)
else:
    print("Repo already exists.")

print(f"Repo path: {repo_path}")

# Backend for local filesystem access - points to the repo directory
# virtual_mode=True restricts access to root_dir only (recommended for security)
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)


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


def stream_agent(agent, input_content: str, step_name: str) -> str:
    """Stream agent execution with verbose output."""
    final_output = ""
    for event in agent.stream({"messages": [{"role": "user", "content": input_content}]}):
        for key, value in event.items():
            if key == "agent" and "messages" in value:
                for msg in value["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"  [{step_name}] TOOL: {tc['name']}: {str(tc['args'])[:80]}...")
                    elif hasattr(msg, "content") and msg.content:
                        final_output = msg.content
            elif key == "tools" and "messages" in value:
                for msg in value["messages"]:
                    if hasattr(msg, "content"):
                        print(f"  [{step_name}] RESULT: {str(msg.content)[:150]}...")
    return final_output


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
    prompts_dir = os.path.join(SCRIPT_DIR, "prompts")
    prompt_path = os.path.join(prompts_dir, f"{name}.txt")

    if not os.path.isdir(prompts_dir):
        raise FileNotFoundError(
            f"Prompt directory not found: {prompts_dir}. "
            "Add the expected prompt files under scripts/llm_training/prompts/."
        )

    if not os.path.isfile(prompt_path):
        raise FileNotFoundError(
            f"Prompt file not found for step '{name}': {prompt_path}."
        )

    with open(prompt_path, encoding="utf-8") as fh:
        system_prompt = fh.read()

    # Add context about the repo location
    system_prompt += "\n\nThe source code for the application you are reviewing is accessible in the current directory."

    # Create the DeepAgent - no custom tools needed, DeepAgent has built-ins
    agent = create_deep_agent(
        model=llm,
        tools=[],
        backend=filesystem_backend,
        system_prompt=system_prompt,
    )

    def _run_step(input_text: str) -> str:
        print(f"\n[{name.upper()} STEP INPUT]\n", input_text)
        print(f"\n[{name.upper()} STEP] (streaming)...")
        output = stream_agent(agent, input_text, name.upper())
        print(f"\n[{name.upper()} STEP RESULT]\n", output)

        # Save step output to file for reference
        steps_dir = os.path.join(SCRIPT_DIR, "steps")
        os.makedirs(steps_dir, exist_ok=True)
        with open(os.path.join(steps_dir, f"{name}.txt"), "w") as fh:
            fh.write(output)

        return output

    return RunnableLambda(_run_step)


def get_output(step_name):
    """Read the saved output from a previous step."""
    steps_dir = os.path.join(SCRIPT_DIR, "steps")
    with open(os.path.join(steps_dir, f"{step_name}.txt")) as fh:
        return fh.read()


# ------------------------------------------------------------------------------
# Chain Definitions
# ------------------------------------------------------------------------------
info_step = new_step(name="info", llm=PLAN_LLM)
plan_step = new_step(name="plan", llm=PLAN_LLM)
scan_step = new_step(name="scan", llm=EXEC_LLM)

# Full chain - currently just info_step, uncomment to add more
full_chain = (
    RunnableLambda(lambda task: task)
    | info_step
    # | plan_step
    # | scan_step
)


if __name__ == "__main__":
    full_chain.invoke(
        "You are an expert code reviewer and application security auditor. "
        "I will give you instructions and you need to follow them precisely."
    )
