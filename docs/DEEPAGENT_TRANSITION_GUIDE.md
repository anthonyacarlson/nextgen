# Transitioning from ReAct to DeepAgent

## Why DeepAgent?

LangChain's **DeepAgent** framework represents the next evolution of agent development. It simplifies agent creation while providing more powerful capabilities out of the box.

| Feature | ReAct Agent | DeepAgent |
|---------|-------------|-----------|
| Setup complexity | High (manual prompt engineering) | Low (declarative) |
| Built-in tools | None | File system, planning, shell, subagents |
| Prompt format | Rigid `Thought/Action/Observation` template | Natural language system prompt |
| Execution | Requires `AgentExecutor` wrapper | Returns compiled LangGraph directly |
| Streaming | Manual setup | Built-in |
| Checkpointing | Manual setup | Built-in |

---

## The Problem with ReAct

ReAct agents require verbose, brittle prompt templates:

```python
REACT_TEMPLATE = """You are an agent designed to analyze code...

TOOLS:
------
You have access to the following tools:
{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human,
or if you do not need to use a tool,
you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

New input: {input}
{agent_scratchpad}
"""
```

This template is:
- **Fragile** - Small changes can break the agent's reasoning
- **Verbose** - Most of this is boilerplate repeated across every agent
- **Manual** - You must wire up `AgentExecutor`, handle parsing errors, etc.

---

## The DeepAgent Solution

DeepAgent abstracts away the complexity:

```python
from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

agent = create_deep_agent(
    model=llm,
    tools=[my_custom_tool],
    system_prompt="You are a security analyst. Review code for vulnerabilities.",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Analyze this code for IDOR issues"}]
})
```

That's it. No prompt template. No executor. No parsing error handlers.

---

## Side-by-Side Comparison

### Before: ReAct Agent (50+ lines)

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate

# LLM setup
llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 0.6},
)

# Verbose ReAct prompt template
instructions = """
You are an agent designed to analyze Python code for IDOR vulnerabilities.

### Analysis Process
1. Initial Review:
   - Identify where the code accesses or modifies database records
   - Locate user-supplied input that influences record access
   - Find authorization checks in the code
...

TOOLS:
------
You have access to the following tools:
{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human,
or if you do not need to use a tool,
you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

New input: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(instructions)

# Create agent and executor
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Invoke
result = agent_executor.invoke({"input": code_to_analyze})
output = result["output"]
```

### After: DeepAgent (20 lines)

```python
from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse

# LLM setup (note: ChatBedrockConverse is now recommended)
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

# Clean system prompt - no boilerplate
system_prompt = """You are an agent designed to analyze Python code for IDOR vulnerabilities.

Analyze the code by:
1. Identifying where the code accesses or modifies database records
2. Locating user-supplied input that influences record access
3. Finding authorization checks in the code

Return your findings as JSON with:
- is_insecure: (bool) whether the code is insecure
- reason: (str) explanation of findings
"""

# Create agent - no executor needed!
agent = create_deep_agent(
    model=llm,
    tools=[custom_search_tool],
    system_prompt=system_prompt,
)

# Invoke with message format
result = agent.invoke({
    "messages": [{"role": "user", "content": code_to_analyze}]
})
output = result["messages"][-1].content
```

---

## Key Migration Steps

### 1. Update Imports

```python
# Remove
from langchain.agents import create_react_agent, AgentExecutor
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate

# Add
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend  # Required for file access!
from langchain_aws import ChatBedrockConverse
import os
```

### 2. Update LLM Instantiation

```python
# Before
llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 0.6},
)

# After
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,  # Note: direct parameter, not in model_kwargs
)
```

### 3. Simplify Prompts

Remove all the ReAct boilerplate (`{tools}`, `{tool_names}`, `Thought/Action/Observation`, `{agent_scratchpad}`). Keep only the actual instructions.

### 4. Add FilesystemBackend (if using file tools)

```python
# Set up absolute path and backend
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_path = os.path.join(SCRIPT_DIR, "repo")
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)
```

### 5. Remove AgentExecutor

```python
# Before
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = agent_executor.invoke({"input": task})

# After
agent = create_deep_agent(
    model=llm,
    tools=tools,
    backend=filesystem_backend,  # Add this for file access
    system_prompt=prompt
)
result = agent.invoke({"messages": [{"role": "user", "content": task}]})
```

### 6. Update Input/Output Format

```python
# Before
result = agent_executor.invoke({"input": task})
output = result["output"]

# After
result = agent.invoke({"messages": [{"role": "user", "content": task}]})
output = result["messages"][-1].content
```

---

## Built-in Tools

DeepAgent includes these tools automatically:

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write to files |
| `edit_file` | Edit existing files |
| `ls` | List directory contents |
| `glob` | Find files by pattern |
| `grep` | Search file contents |
| `execute` | Run shell commands |
| `write_todos` | Task planning/decomposition |
| `task` | Spawn subagents |

This means you can **remove custom file tools** like `ViewFileTool`, `DirectoryListingTool`, etc.

---

## FilesystemBackend - Critical for File Access

**This is the most important thing to understand!**

DeepAgent's built-in file tools (ls, read_file, etc.) require a **FilesystemBackend** to access real files. Without it, the agent uses a default `StateBackend` that has NO filesystem access - the agent will run but won't find any files.

### The Problem

```python
# This WILL NOT WORK - agent can't access real files
agent = create_deep_agent(
    model=llm,
    tools=[],
    system_prompt="Analyze code in ./repo/...",
)
```

### The Solution

```python
from deepagents.backends import FilesystemBackend
import os

# Use absolute paths for reliability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_path = os.path.join(SCRIPT_DIR, "repo")

# Create backend pointing to directory you want the agent to access
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)

# Pass backend to create_deep_agent
agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,  # <-- This enables file access!
    system_prompt="Analyze code in the current directory...",
)
```

### Key Points

1. **FilesystemBackend is required** for any agent that needs to read files
2. **Use absolute paths** via `os.path.dirname(os.path.abspath(__file__))`
3. **virtual_mode=True** restricts access to root_dir only (security best practice)
4. **Update system prompts** to reference "current directory" instead of relative paths

---

## LCEL Chain Compatibility

DeepAgent works seamlessly with LCEL chains because `create_deep_agent()` returns a Runnable:

```python
from langchain_core.runnables import RunnableLambda

# DeepAgent in an LCEL chain
context_agent = create_deep_agent(
    model=llm,
    tools=tools,
    system_prompt="Gather context about the codebase...",
)

def run_context_step(task: str) -> dict:
    result = context_agent.invoke({
        "messages": [{"role": "user", "content": task}]
    })
    return {"context": result["messages"][-1].content}

context_step = RunnableLambda(run_context_step)

# Chain it with other steps
full_chain = context_step | plan_step | review_step
```

---

## Installation

```bash
pip install deepagents
```

Or add to your requirements.txt:
```
deepagents
```

---

## Resources

- [DeepAgent Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [DeepAgent Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)
- [GitHub Repository](https://github.com/langchain-ai/deepagents)
