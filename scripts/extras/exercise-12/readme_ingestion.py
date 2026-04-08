import requests
from langchain_core.documents import Document
#from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_aws import ChatBedrock

# Load Env Variables
from dotenv import load_dotenv
load_dotenv()

# UNCOMMENT FOR OLLAMA
#llm = Ollama(model="gemma3", temperature=0.6)
llm = ChatBedrock(
    model_id='us.anthropic.claude-haiku-4-5-20251001-v1:0',
    model_kwargs={"temperature": 0.6},
)

question = """
QUESTION
========
{question}

CONTEXT
=======
{context}
"""
prompt = ChatPromptTemplate.from_template(template=question)
README_URL = 'https://raw.githubusercontent.com/juice-shop/juice-shop/master/README.md'
response = requests.get(README_URL)
if response.status_code == 200:
    readme_content = response.content
    doc = Document(
        page_content=readme_content, 
        metadata={"source": "README.md"}
    )
    chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    # Stream the output in chunks for a chat-like experience
    for chunk in chain.stream({
        "question":"You are being provided the README file from a software project. Please provide a summary of the purpose of the application and any other relevant details you can think to share.", 
        "context": doc
    }):
        print(chunk, end="", flush=True)
