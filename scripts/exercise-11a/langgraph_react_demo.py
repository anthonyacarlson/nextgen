from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os
import git

load_dotenv()

# Git repo setup
repo_url = "https://github.com/third-culture-software/bhima.git"
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
system_prompt = """You are an agent designed to gather information about an application for security assessment planning.
The application source code is located at ./repo/

Your goal is to collect information in three key areas (from the security assessment template):

## 1. Behavior
Understand what the application does by answering:
- What does it do? (business purpose)
- Who does it do this for? (internal / external customer base)
- What kind of information will it hold?
- What are the different types of roles?
- What aspects concern client/customer/staff the most?

## 2. Tech Stack
Identify the technology components:
- Framework & Language (e.g., Rails/Ruby, Django/Python, mux/Golang, Node.js/Express, Angular/React)
- 3rd party components (building libraries, JavaScript widgets, webhook-dependent applications)
- Datastores (Postgresql, MySQL, Memcache, Redis, MongoDB, etc.)

## 3. Brainstorming / Risks
Brainstorm about potential concerns (NOT specific vulnerability finding):
- What are potential failure modes for this feature/product?
- What technology-specific risks should we think about?
  (e.g., "ORM might have SQLi risks", "template language might have XSS risks")
- General security concerns to explore later

NOTE: This is information gathering and brainstorming, NOT vulnerability scanning.
You are collecting context to understand the application before deeper security analysis.

### Process
1. Explore the repository to understand the codebase structure
2. Read documentation (README, package files, config files) to understand the app
3. Collect factual information about behavior and tech stack
4. Brainstorm potential risk areas to investigate

TODO: You can add your own custom tool here to enhance information gathering.

### Output Format
Your final response must be in JSON format with these fields:
- `behavior`: (object) What the app does, users, data types, roles, concerns
- `tech_stack`: (object) Frameworks, 3rd party components, datastores identified
- `brainstorming`: (array) List of potential risk areas and concerns to explore
"""

# Create DeepAgent - no custom file tools needed, DeepAgent has built-ins!
# Built-in tools include: read_file, write_file, ls, glob, grep, etc.
agent = create_deep_agent(
    model=llm,
    tools=[],  # DeepAgent's built-in file tools are sufficient
    system_prompt=system_prompt,
)


def analyze_application(input_task: str) -> dict:
    """
    Analyze application using the DeepAgent and return the result.
    """
    response = agent.invoke({
        "messages": [{"role": "user", "content": input_task}]
    })
    return response


# Note: The LangGraph wrapper is no longer needed because
# create_deep_agent() already returns a compiled LangGraph!


if __name__ == "__main__":
    print("Security Assessment Information Gathering Demo")
    print("=" * 50)

    analysis_task = """Gather information about the application in ./repo/ by collecting:
1. Behavior - What does it do, who uses it, what data does it handle, what roles exist, what are the main concerns?
2. Tech Stack - What frameworks, languages, 3rd party components, and datastores are being used?
3. Brainstorming - What potential risk areas and security concerns should we think about for this type of application?

Start by exploring the directory structure, reading README files, package.json or requirements files, and configuration files.
Focus on GATHERING INFORMATION, not finding specific vulnerabilities."""

    print("\nDeepAgent Analysis:")
    result = analyze_application(analysis_task)
    print(result["messages"][-1].content)
