# ReAct to DeepAgent Migration Tracker

## Overview
Migration of all LangChain ReAct agents to the new DeepAgent framework.

**Branch:** `feature/react-to-deepagent-migration`
**Started:** 2026-04-05

---

## Key Changes Summary

| Aspect | ReAct (Old) | DeepAgent (New) |
|--------|-------------|-----------------|
| Import | `from langchain.agents import create_react_agent, AgentExecutor` | `from deepagents import create_deep_agent` |
| LLM | `ChatBedrock` | `ChatBedrockConverse` (recommended) |
| Prompt | Manual ReAct format with `Thought/Action/Observation` | Simple `system_prompt` string |
| Executor | Requires `AgentExecutor` wrapper | Not needed - returns compiled LangGraph |
| Input | `{"input": "..."}` | `{"messages": [{"role": "user", "content": "..."}]}` |
| Output | `result["output"]` | `result["messages"][-1].content` |
| File Tools | Custom `ViewFileTool`, `DirectoryListingTool`, etc. | Built-in `read_file`, `write_file`, `ls`, `glob`, `grep` |

---

## Migration Pattern

### Before (ReAct)
```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate

llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_kwargs={"temperature": 0.6},
)

REACT_TEMPLATE = """You are an agent...

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

When you have a response to say to the Human...
Final Answer: [your response here]

Begin!
New input: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(REACT_TEMPLATE)
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

result = executor.invoke({"input": task})
output = result["output"]
```

### After (DeepAgent)
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_aws import ChatBedrockConverse
import os

# CRITICAL: Use absolute paths for reliable file access
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_path = os.path.join(SCRIPT_DIR, "repo")

llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

# CRITICAL: FilesystemBackend is required for DeepAgent to access real files
# Without this, DeepAgent uses the default StateBackend (ephemeral, no filesystem access)
# virtual_mode=True restricts access to root_dir only (recommended for security)
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)

SYSTEM_PROMPT = """You are an agent designed to analyze code for vulnerabilities.
The source code is available in the current directory.

Your task is to:
1. Review the code for security issues
2. Identify OWASP Top 10 vulnerabilities
3. Return findings in JSON format

Output format:
- is_insecure: (bool) whether the code is insecure
- reason: (str) explanation of findings
"""

agent = create_deep_agent(
    model=llm,
    tools=[custom_non_file_tools],  # DeepAgent has built-in file tools
    backend=filesystem_backend,      # REQUIRED for real filesystem access
    system_prompt=SYSTEM_PROMPT,
)

result = agent.invoke({"messages": [{"role": "user", "content": task}]})
output = result["messages"][-1].content
```

---

## Files to Migrate

### Simple Single-Agent Files
| File | Status | Notes |
|------|--------|-------|
| `scripts/exercise-07/agentic_basic.py` | [x] Complete | IDOR analyzer, 1 agent, custom vector DB tool |
| `scripts/exercise-08/langgraph_react_demo.py` | [x] Complete | SAST demo, 1 agent, removed custom file tools |
| `scripts/exercise-11a/langgraph_react_demo.py` | [x] Complete | Security assessment, 1 agent, removed custom file tools |
| `scripts/extras/exercise-09/agentic_dast_xss.py` | [x] Complete | XSS scanner, 1 agent, kept HTTP tool |
| `scripts/extras/exercise-10/agentic_basic.py` | [x] Complete | IDOR analyzer (duplicate of ex-07) |

### Multi-Agent LCEL Chain Files
| File | Status | Notes |
|------|--------|-------|
| `scripts/exercise-16a/lcel_auditing_chain.py` | [x] Complete | 3-step LCEL, 2 agents (context + review), kept LCEL pattern |
| `scripts/exercise-16a/lcel_authorization_chain_demo.py` | [x] Complete | 3-step LCEL, 2 agents (context + review), kept LCEL pattern |
| `scripts/exercise-16a/rce.py` | [x] Complete | 3-step LCEL, 2 agents (context + review), kept LCEL pattern |
| `scripts/llm_training/audit.py` | [x] Complete | Generic audit chain, loads prompts from files |

---

## Tools Migration

### Tools to REMOVE (use DeepAgent built-ins instead)
- `ViewFileTool` -> DeepAgent's `read_file`
- `ViewFileLinesTool` -> DeepAgent's `read_file`
- `DirectoryListingTool` -> DeepAgent's `ls`
- `FileListingTool` -> DeepAgent's `ls` / `glob`
- `DirectoryStructureTool` -> DeepAgent's `ls` / `glob`

### Tools to KEEP (custom functionality)
- `CustomSearchTool` (vector DB search) - exercise-07, extras/exercise-10
- `HttpTool` (HTTP requests) - extras/exercise-09

---

## Dependencies

### Add to requirements
```
deepagents
```

### Import changes
```python
# Remove
from langchain.agents import create_react_agent, AgentExecutor
from langchain_aws import ChatBedrock

# Add
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend  # CRITICAL for file access
from langchain_aws import ChatBedrockConverse
```

---

## FilesystemBackend - Critical Requirement

**This is the most important change!** DeepAgent's built-in file tools (ls, read_file, etc.) only work with a proper backend configuration.

### The Problem
By default, DeepAgent uses `StateBackend` which is ephemeral and has NO real filesystem access. The agent will appear to run but won't find any files.

### The Solution
```python
from deepagents.backends import FilesystemBackend

# Use absolute path to the directory containing files to analyze
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_path = os.path.join(SCRIPT_DIR, "repo")

# Create backend pointing to your repo
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)

# Pass backend to create_deep_agent
agent = create_deep_agent(
    model=llm,
    tools=[],
    backend=filesystem_backend,  # <-- This enables real file access!
    system_prompt=system_prompt,
)
```

### Key Points
1. **Absolute paths**: Always use `os.path.dirname(os.path.abspath(__file__))` for reliable paths
2. **virtual_mode=True**: Restricts agent to only access files within root_dir (security best practice)
3. **System prompt**: Reference files as "current directory" not relative paths like "./repo"

---

## Testing Checklist

- [ ] Verify `deepagents` package is installed
- [ ] Test each migrated file runs without errors
- [ ] Verify agent output format matches expected structure
- [ ] Test LCEL chains maintain proper data flow between steps
- [ ] Confirm custom tools (vector DB, HTTP) still work with DeepAgent

---

## Notes

- DeepAgent returns a compiled LangGraph, so streaming and checkpointing are available
- The `system_prompt` replaces the verbose ReAct template - much cleaner
- LCEL chains should continue to work since DeepAgent agents are Runnables
- **FilesystemBackend is required** for any agent that needs to access real files on disk
- Import path for callbacks changed: `langchain.callbacks.manager` -> `langchain_core.callbacks.manager`
