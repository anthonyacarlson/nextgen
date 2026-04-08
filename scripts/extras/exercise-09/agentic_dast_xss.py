from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from dotenv import load_dotenv
import httpx
import json

load_dotenv()


class HttpInput(BaseModel):
    req: str = Field(description="data to send with the request, example: {'url': 'http://example.com/path', 'method': 'GET', 'data': {}}")


class HttpTool(BaseTool):
    name: str = "http_tool"
    description: str = "Useful for when you need to make a request to a url. Can be used for GET and POST requests."
    args_schema: Type[HttpInput] = HttpInput

    def _run(
        self, req: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        data = json.loads(req)
        print(f"Making {data['method']} request to {data['url']} with data: {data['data'] if 'data' in data else 'N/A'}")
        try:
            if data["method"].upper() == "POST":
                response = httpx.post(data["url"], data=data["data"])
            else:
                response = httpx.get(data["url"])
            headers = str(response.headers)
            body = response.text
            status = response.status_code
            return f"Status Code: {status}\nHeaders:\n{headers}\n\nBody:\n{body}"
        except Exception as e:
            return f"HTTP request failed: {str(e)}"

    async def _arun(
        self, url: str, method: str = "GET", data: Optional[dict] = None, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("http_tool does not support async")


# Define tools and LLM
tools = [HttpTool()]
llm = ChatBedrockConverse(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0.6,
)

# System prompt - clean, no ReAct boilerplate
system_prompt = """You are an agent designed to confirm whether an HTTP request and response is vulnerable to cross-site scripting by analyzing HTTP responses using a multi-step reasoning process.

### Analysis Process
1. **Initial Request**: Make an HTTP request to the provided URL using the specified method (GET or POST).
2. **Response Analysis**: Analyze the response for possible XSS in the following locations:
   - Headers: (str) The headers of the response
   - Body: (str) The body of the response
3. **Final Response**: Return the relevant information from the HTTP request.

You have access to an HTTP tool that can make requests to URLs. It can handle both GET and POST requests.

### Output Format
Your final response must include:
- URL: (str) The URL of the request
- Parameters: (str) The parameters sent with the request
- XSS: (str) Any identified XSS vulnerabilities (Yes or No)
- Justification: (str) A brief justification ONLY if XSS is confirmed
"""

# Create DeepAgent
agent = create_deep_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)


def run_agent(url: str) -> dict:
    """
    Analyze the given URL using the agent and return the result.
    """
    response = agent.invoke({
        "messages": [{"role": "user", "content": url}]
    })
    return response


if __name__ == "__main__":
    # Example input for POST request
    url = "https://vtm.rdpt.dev/taskManager/login/"
    method = "POST"
    data = {"username": "admin", "password": "admin"}
    post_input = f"Test this endpoint for XSS: URL={url}, Method={method}, Data={data}"

    result = agent.invoke({
        "messages": [{"role": "user", "content": post_input}]
    })
    print(result["messages"][-1].content)
