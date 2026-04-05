from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os
import git

load_dotenv()

# Git repo setup
repo_url = "https://github.com/redpointsec/vtm.git"
repo_path = "./repo"

if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
    print("Directory already contains a git repository.")
else:
    try:
        repo = git.Repo.clone_from(repo_url, repo_path)
        print(f"Repository cloned into: {repo_path}")
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")

# LLM setup
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

# System prompt - no ReAct boilerplate needed
system_prompt = """You are an agent designed to analyze Python/Django code for vulnerabilities.
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

### Output Format
Your final response must be in JSON format, containing the following fields:
- `is_insecure`: (bool) Whether the code is considered insecure.
- `reason`: (str) The reason the code is considered insecure or secure.
"""

# Create DeepAgent - no custom file tools needed, DeepAgent has built-ins!
# Built-in tools include: read_file, write_file, ls, glob, grep, etc.
agent = create_deep_agent(
    model=llm,
    tools=[],  # DeepAgent's built-in file tools are sufficient
    system_prompt=system_prompt,
)


def analyze_code(input_task: str) -> dict:
    """
    Analyze code using the DeepAgent and return the result.
    """
    response = agent.invoke({
        "messages": [{"role": "user", "content": input_task}]
    })
    return response


# Note: analyze_code_with_langgraph() is no longer needed because
# create_deep_agent() already returns a compiled LangGraph!
# The agent variable IS the LangGraph.


if __name__ == "__main__":
    print("DeepAgent SAST Demo")
    print("=" * 50)

    analysis_task = "Analyze the Python/Django code in ./repo/ for security vulnerabilities. Start by exploring the directory structure to understand the codebase."

    print("\nDeepAgent Analysis:")
    result = analyze_code(analysis_task)
    print(result["messages"][-1].content)
