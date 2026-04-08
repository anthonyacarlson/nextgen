import os
import git
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain.text_splitter import Language
# UNCOMMENT FOR OLLAMA
#from langchain_community.embeddings import HuggingFaceEmbeddings
#from langchain_community.llms import Ollama
# For BedRock
from langchain_aws import BedrockEmbeddings
from langchain_aws import ChatBedrock
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load Env Variables
from dotenv import load_dotenv
load_dotenv()

repo_url = 'https://github.com/redpointsec/vtm.git'
local_path = 'exercise-15/repo'

embeddings = BedrockEmbeddings(model_id='amazon.titan-embed-text-v2:0')

faiss_db_path = "../vector_databases/vtm_code.faiss"
db = FAISS.load_local(
    faiss_db_path, 
    embeddings,
    allow_dangerous_deserialization=True
)

system_prompt_template = """
You are a helpful code assistant who is given acess to a
code base stored in vector format. You will be asked questions about that code.
Please provide helpful and accurate responses to the best of your ability.

</context>
{context}
</context>
"""

# CORRECT/FORMAL WAY TO PERFORM PROMPTING
prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_template),
                ("human", """<question>{question}</question>""")
            ]
)
retriever = db.as_retriever(
    search_type="mmr", # Also test "similarity"
    search_kwargs={"k": 8},
)

#llm = Ollama(model="llama3", temperature=0.6)
llm = ChatBedrock(
    model_id='us.anthropic.claude-haiku-4-5-20251001-v1:0',
    model_kwargs={"temperature": 0.6},
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# This is an optional addition to stream the output in chunks
# for a chat-like experience
question = """
Which Django authorization decorators are used in this 
application code base and where are they located?
"""
for chunk in chain.stream(question):
    print(chunk, end="", flush=True)

