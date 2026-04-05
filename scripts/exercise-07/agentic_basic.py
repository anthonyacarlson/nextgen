from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from typing import Optional, Type
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from dotenv import load_dotenv

load_dotenv()


class SearchInput(BaseModel):
    query: str = Field(
        description="ONLY the function name - no extra words (e.g., 'can_create_project', 'login_required')"
    )


class CustomSearchTool(BaseTool):
    name: str = "function_lookup"
    description: str = (
        "Look up a specific function definition. Input must be EXACTLY the function name with no additional words. "
        "CORRECT: 'can_create_project' | INCORRECT: 'can_create_project function' or 'authorization check'"
    )
    args_schema: Type[SearchInput] = SearchInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        faiss_db_path = "../vector_databases/vtm_code.faiss"
        db = FAISS.load_local(
            faiss_db_path,
            BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0"),
            allow_dangerous_deserialization=True,
        )
        return db.similarity_search(query)

    async def _arun(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("function_lookup does not support async")


# Define tools and LLM
tools = [CustomSearchTool()]
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.6,
)

# System prompt - clean, no ReAct boilerplate
system_prompt = """You are an agent designed to analyze Python code for potential Insecure Direct Object Reference (IDOR) vulnerabilities.

### Analysis Process
1. Initial Review:
   - Identify where the code accesses or modifies database records
   - Locate user-supplied input that influences record access
   - Find authorization checks in the code

2. Reflection Questions:
   Consider these questions carefully:
   - How does the code determine which records a user can access?
   - What prevents a user from accessing records belonging to others?
   - Is there a mismatch between authorization scope and data access?
   - Could changing the input parameters bypass the authorization?

3. Challenge Initial Assessment:
   - What assumptions did you make about the authorization?
   - Are you certain the authorization check applies to the specific record?
   - What would an attacker try first to bypass these controls?

You have access to a vector database tool to search for code-related information. Use it to understand how custom functions handle authorization.

### Output Format
Your final response must be in JSON format, containing the following fields:
- `is_insecure`: (bool) Whether the code is considered insecure.
- `reason`: (str) The reason the code is considered insecure or secure.
"""

# Create DeepAgent
agent = create_deep_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)


def analyze_code(input_code: str) -> dict:
    """
    Analyze the given code using the agent and return the result.
    """
    response = agent.invoke({
        "messages": [{"role": "user", "content": input_code}]
    })
    return response


if __name__ == "__main__":
    input_code = """
    @login_required
    @user_passes_test(can_create_project)
    def update_user_active(request):
        user_id = request.GET.get('user_id')
        User.objects.filter(id=user_id).update(is_active=False)
    """
    result = analyze_code(input_code)
    print(result["messages"][-1].content)
