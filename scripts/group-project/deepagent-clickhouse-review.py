from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os
import git

load_dotenv()

# Git repo setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_url = "https://github.com/OpenHands/OpenHands.git"
repo_path = os.path.join(SCRIPT_DIR, "repo")

skills_dir = os.path.join(SCRIPT_DIR, "skills")

print(f"Skills directory: {skills_dir}")
print("Skills loaded:")
for skill_name in os.listdir(skills_dir):
    skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
    if os.path.exists(skill_path):
        print(f"  - {skill_name}")

if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
    print("Directory already contains a git repository.")
else:
    try:
        repo = git.Repo.clone_from(
            repo_url,
            repo_path,
            multi_options=["--no-checkout", "--filter=blob:none", "--sparse"],
        )
        repo.git.sparse_checkout("set", ".claude/skills")
        repo.git.checkout()
        print(f"Repository cloned into: {repo_path}")
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")

# LLM setup
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.1,
)

# Backend for local filesystem access - points to the repo directory
# virtual_mode=True restricts access to root_dir only (recommended for security)
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)

print(f"Repo path: {repo_path}")

# System prompt - no ReAct boilerplate needed
system_prompt = """You are a openhands expert agent designed to analyze openhands AI/ML agent integrations for best practice violations,
performance risks, and misconfiguration.

Source files are available in the
current directory.

---


"""

# Create DeepAgent - no custom file tools needed, DeepAgent has built-ins!
# Built-in tools include: read_file, write_file, ls, glob, grep, etc.
agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,
    skills=[skills_dir], 
    system_prompt=system_prompt,
)


def analyze_code(input_task: str) -> str:
    """
    Analyze code using the DeepAgent with streaming output.
    """
    print("[Agent] Running (streaming)...")
    final_output = ""
    for event in agent.stream({"messages": [{"role": "user", "content": input_task}]}):
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


if __name__ == "__main__":
    print("DeepAgent Github/Skills review")
    print("=" * 50)

    analysis_task = "Give me a summary and security considerations for the AI skills."

    print("\nDeepAgent Analysis:")
    result = analyze_code(analysis_task)
    print("\n" + "=" * 50)
    print("RESULT:")
    print(result)
