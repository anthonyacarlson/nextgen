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
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.6,
)

EXEC_LLM = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.1,
)

# EXEC_LLM = ChatBedrockConverse(
#    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
#    temperature=0.1,
# )


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
    system_prompt += """

## Repository Context
The application source code is in the current directory. Begin exploring immediately.
"""

    # Create the DeepAgent - no custom tools needed, DeepAgent has built-ins
    agent = create_deep_agent(
        model=llm,
        tools=[],
        backend=filesystem_backend,
        system_prompt=system_prompt,
    )

    def _run_step(input_text: str) -> str:
        print(f"\n[{name.upper()} STEP INPUT]\n", input_text)
        print(f"\n[{name.upper()}] Running (streaming)...")

        # -------------------------------------------------------------------------
        # TIMEOUT HANDLING STRATEGY FOR LLM AGENTS
        # -------------------------------------------------------------------------
        # LLM API calls can timeout for several reasons:
        #   1. Network latency or temporary connectivity issues
        #   2. The model is processing a complex request (especially with tools)
        #   3. The agent spawned subagents via 'task' tool, multiplying API calls
        #   4. Rate limiting or service degradation on the provider side
        #
        # Our strategy:
        #   - Wrap the streaming loop in try/except to catch timeout errors
        #   - Collect partial output as we stream (don't wait until the end)
        #   - If a timeout occurs, return whatever we collected so far
        #   - Log the error clearly so users know what happened
        #   - Save partial results to disk so work isn't completely lost
        #
        # Common timeout exceptions to handle:
        #   - botocore.exceptions.ReadTimeoutError (AWS/Bedrock)
        #   - requests.exceptions.Timeout (HTTP clients)
        #   - TimeoutError (Python built-in)
        #   - httpx.ReadTimeout (if using httpx)
        # -------------------------------------------------------------------------

        final_output = ""
        tool_calls_made = []  # Track tools for debugging/partial results

        try:
            for event in agent.stream(
                {"messages": [{"role": "user", "content": input_text}]}
            ):
                for key, value in event.items():
                    # Skip middleware events (internal DeepAgent plumbing)
                    if "Middleware" in key:
                        continue
                    # Handle dict values with messages
                    if isinstance(value, dict) and "messages" in value:
                        for msg in value["messages"]:
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    tool_calls_made.append(tc["name"])
                                    print(f"  -> {tc['name']}")
                            elif hasattr(msg, "content") and msg.content:
                                # Capture content as we go - this is key for partial results
                                final_output = msg.content

        except Exception as e:
            # -------------------------------------------------------------------------
            # GRACEFUL DEGRADATION ON TIMEOUT
            # -------------------------------------------------------------------------
            # When a timeout occurs mid-stream, we have a few options:
            #   1. Return partial output if we collected any (preferred)
            #   2. Retry the request (risk: may timeout again, wastes tokens)
            #   3. Return an error message (last resort)
            #
            # We choose option 1 because:
            #   - Partial results are often still useful
            #   - The user can see what tools were called before failure
            #   - Retrying blindly can be expensive and may fail again
            # -------------------------------------------------------------------------
            error_type = type(e).__name__
            print(f"\n[{name.upper()}] ERROR: {error_type}")
            print(f"  Message: {str(e)[:200]}...")
            print(f"  Tools called before error: {tool_calls_made}")

            if final_output:
                print(f"  Returning partial output collected before error.")
            else:
                # No output collected - provide informative error as result
                final_output = (
                    f"[TIMEOUT ERROR]\n"
                    f"The agent timed out before completing the analysis.\n"
                    f"Tools called: {', '.join(tool_calls_made) or 'none'}\n\n"
                    f"Suggestions:\n"
                    f"1. Try running again (may be transient)\n"
                    f"2. Use a faster model (e.g., Haiku instead of Sonnet)\n"
                    f"3. Simplify the task to reduce processing time\n"
                    f"4. Check your network connection"
                )

        output = final_output
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
# Chain Definitions - Focused, completable steps
# ------------------------------------------------------------------------------
# Step 1: Quick discovery (max 10 tool calls)
discover_step = new_step(name="discover", llm=EXEC_LLM)

# Step 2: Focused auth analysis (max 15 tool calls)
auth_step = new_step(name="analyze_auth", llm=EXEC_LLM)

# Step 3: Focused injection analysis (max 15 tool calls)
injection_step = new_step(name="analyze_injection", llm=EXEC_LLM)

# Legacy steps (kept for reference)
# info_step = new_step(name="info", llm=PLAN_LLM)
# plan_step = new_step(name="plan", llm=PLAN_LLM)
# scan_step = new_step(name="scan", llm=EXEC_LLM)

# Full chain - focused steps that complete within timeout
full_chain = (
    RunnableLambda(lambda task: task)
    | discover_step
    | auth_step
    | injection_step
)


if __name__ == "__main__":
    full_chain.invoke(
        "Perform a security assessment of the application."
    )
