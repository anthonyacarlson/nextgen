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
from langchain_aws import ChatBedrockConverse

llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

SYSTEM_PROMPT = """You are an agent designed to analyze code for vulnerabilities.

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
from langchain_aws import ChatBedrockConverse
```

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
