import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Fix for OpenMP issue on macOS

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_debug

set_debug(False)

# Load Env Variables
from dotenv import load_dotenv

load_dotenv()

# For BedRock
from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
faiss_db_path = os.path.join(SCRIPT_DIR, "..", "..", "vector_databases", "juice_shop.faiss")
db = FAISS.load_local(
    faiss_db_path,
    BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0"),
    allow_dangerous_deserialization=True,
)

retriever = db.as_retriever(
    search_type="mmr",  # Also test "similarity"
    search_kwargs={"k": 20},
)

system_prompt_template = """
ROLE:
You are an expert Senior Software Engineer and Application Security Specialist. You excel at identifying subtle logic bugs, performance bottlenecks, and security vulnerabilities (OWASP Top 10) within source code.

OBJECTIVE:
Analyze the provided source code through a rigorous multi-step reflection process. Your goal is to provide a deep-dive analysis that goes beyond the surface level to find "hidden" issues.

STEPS:
Follow this exact internal reasoning process:

1. INITIAL ANALYSIS:
   - Identify the primary functionality and tech stack.
   - List immediate observations regarding code quality, logic, and security.

2. CRITICAL REFLECTION (The "Adversarial" Phase):
   - What did I overlook in the first pass? 
   - Challenge your assumptions: "If I were an attacker, how would I bypass these checks?" or "How does this code fail under high load or edge-case inputs?"
   - Evaluate against industry best practices (e.g., DRY, SOLID, or language-specific idioms).

3. FINAL COMPREHENSIVE RESPONSE:
   - Synthesize the findings into a polished, actionable report.
   - Categorize issues by severity (Critical, High, Medium, Low).
   - Provide brief remediation suggestions for identified flaws.

STRUCTURE:
Maintain a professional, objective tone. Use the following format:

## 1. Initial Analysis
[Brief summary of obvious findings]

## 2. Reflection & Edge Cases
[Insights gained from re-evaluating the code; focus on what was nearly missed]

## 3. Final Comprehensive Analysis
### Functional Overview
[How the code works]
### Security & Logic Vulnerabilities
[List specific issues with impact and suggested fixes]
### Recommendations
[Best practices for improvement]

CODE FOR ANALYSIS:
{context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_template),
        ("human", """<question>{question}</question>"""),
    ]
)

llm = ChatBedrock(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    model_kwargs={"temperature": 0.6},
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

user_question = """
Tell me about the application, its functionality, libraries and framworks, and any potential security issues you can identify from the codebase provided in the context.
"""

# This is an optional addition to stream the output in chunks
# for a chat-like experience
for chunk in chain.stream(user_question):
    print(chunk, end="", flush=True)
