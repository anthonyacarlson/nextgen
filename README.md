# 0xAI - Next-Gen Secure Code Review: Black Hat Edition

## Requirements
* Python 3.12
* Ollama
* Gemma3 and EmbeddingGemma in Ollama/local tasks

```
ollama pull gemma3
ollama pull embeddinggemma
```

* AWS/Bedrock Access (will be provided for in-person course)

## Setup & Check Install
Built targeting Python 3.12. Use other python versions at your own risk.
To run associated scripts:
```
# Create a virtual python environment
python3.12 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Run the chatbot 
python scripts/exercise-00/chatbot.py
```

### Errors

If you see an error about OpenMP runtime, set the following:

```
export KMP_DUPLICATE_LIB_OK=TRUE
```


## Overview
Elevate your application security expertise with this exclusive Black Hat course, co-developed by industry leaders Seth Law and Ken Johnson (co-hosts of the Absolute AppSec podcast). This training focuses on leveraging Generative AI and Large Language Models (LLMs) to enhance AppSec tasks and accelerate code analysis across diverse applications. Designed for engineers, consultants, and researchers, you will gain hands-on experience in building and integrating AI components and LLM agents. Learn to streamline analysis and prioritize security tasks, create custom tools for efficient vulnerability discovery, perform risk-based assessments and reviews, and uncover vulnerability edge cases, backdoors, and exploits. By the end of the course, you will be equipped with a battle-tested, AI-augmented methodology to confidently tackle AppSec and secure code review projects.

## Course Abstract
Learn an LLM-enhanced secure code review methodology for discovering vulnerabilities in code against any language or framework, no matter the amount of code in a special edition of this course purpose built for Black Hat attendees. Whether analyzing code as an engineer, consultant, or researcher, enhance your bug-hunting techniques and code review skills harnessing the power of Generative AI, Large Language Models, and a battle-tested methodology. You will perform each exercise using real OSS code bases as well as instructor-developed applications. During the training, you will learn and practice a methodology developed by Seth and Ken (co-hosts of the Absolute AppSec podcast) to find bugs in hundreds of code bases, including web, mobile, and IoT applications. 

The Black Hat Edition of this course starts with the building blocks of Generative AI alongside code review activities, going in-depth on utilizing any LLM (course focuses on Anthropic models, but students will also use Gemma, Deepseek, or OpenAI options in the exercises) to identify vulnerability edge cases, backdoors, exploits, and various information gathering activities.

This secure code review methodology now depends on AI to speed up analysis to enhance software security and development practices. Using both a custom vulnerable application and various open-source projects, participants will gain the confidence to take on code-review projects, create AI components, prioritize tasks, avoid unnecessary time sinks, integrate LLM agents, and work quickly to understand an application's security-relevant files and functions. The curriculum also covers essential topics such as embeddings, vector stores, and Langchain, offering insights into document & code loading, code analysis, and custom tool creation using Agent Executors. In summary students can expect from the course:


1. An explanation of risk-based code review principles.
2. Introduction into implementation and use of Generative AI to solve generic tasks.
3. Use of Generative AI for code review overview and specific tasks.
4. An overview of what to look for across various languages and frameworks - Basic considerations and Vulnerabilities. (General & App Specific).
5. Highlighting examples of files and particular problems within various languages and frameworks  - Attack Surface, Framework Nuances.
6. A hands-on experience using Generative AI to understand code and associated vulnerabilities.

## Training Outline
### Day 1: Building Block of LLMs 
#### #### Session 1 - Introduction & Course Overview 
* Welcome, introductions, and course objectives 
* Overview of Generative AI, LLM functionality, strengths, and limitations 
#### #### Session 2 - Lab Setup & Environment Check 
* Verify connectivity to LLM endpoints and vector databases
* Confirm access to required tools (Langchain, IDEs, etc.)
#### #### Session 3 - Langchain Fundamentals & Prompt Engineering 
* Overview of Langchain components and documentation concepts 
* Types of prompts (user, system, AI) and few‑shot prompting frameworks (CO‑STAR, CLARITY, SMART), Relfexion 
* Hands‑on exercise : Crafting effective prompts for security use cases
#### #### Session 4 - Context, Embeddings, & Vector Stores 
* Understanding context length/window and embedding fundamentals 
* Use cases: similarity searches and chaining for secure code analysis 
* Exercise: Leverage a vector store to enhance prompt performance 
#### #### Session 5 - Build Your Own Chatbot AppSec Assistant 
* Background & Use Cases 
* Retrieval Augmented Generation (RAG) Techniques 
* Maintain Chat History  
* Vectorize and store code & documents for Chatbot access 
* Exercise: Build an AI Assistant that use 
#### #### Session 6 - AI‑Powered Code Analysis & Agentic Tools 
* Empowering LLMs with System Access: Explore techniques to integrate LLMs with agent executors, granting autonomous access to tools. 
* Agentic Tools Architecture: Setup and configure tools that enable the LLM to interact with file and folder listings, view code files, and execute command-line tasks. 
* Exercise: Build a "Chain of Thought" prompt allowing the LLM to use reasoning and perform subsequent lookups using an Agentic Architecture to validate a vulnerability. 
#### #### Session 7 - Wrap‑Up and Q&A 
* Recap key takeaways from LLM integration in security
* Open Q&A and discussion of practical applications

### Day 2: Secure Code Review 
#### #### Session 1 - Secure Code Review Overview & Methodology 
* Code Review Philosophy 
* Presentation of the "Circle‑K Framework" and overall secure code review approach 
* Tools and lab setup; review of the OWASP Top 10 
#### #### Session 2 - Code Review Fundamentals & Risk Assessment 
Principles of secure code review 
Techniques for assessing application behavior, technology stack, and architecture 
Note‑taking and risk profiling 
Exercise: App Behavior/Tech Stack/Architecture + Risk 
#### Session 3 - Information Gathering & Mapping 
* Techniques for gathering code and application information 
* Mapping exercises: outlining application flow and attack surface 
* AI Exercise: Integrating AI to enhance data collection 
#### Session 4 - Authorization Reviews 
* Deep dive into reviewing authorization functions and common vulnerabilities (e.g., broken access control, mass assignment) 
* Interactive exercise: Using manual and AI enhanced techniques to analyze authorization flows 
#### Session 5 - Authentication Reviews 
* Authentication review: identifying issues like broken authentication, #### Session management, authentication bypasses, multi-factor authentication, username enumeration, and more. 
* Interactive exercise: Using manual review techniques along with AI tooling to analyze and enhance authentication review 
#### Session 6 - Auditing 
* Auditing review: logging and sensitive data exposure vulnerabilities 
* Hands‑on checklist exercises 
#### Session 7 - Injection - Input Validation 
* Injection Review: input validation, source to sink tracing 
* Input Validation Exercise: Use manual techniques to identify validation routines along with AI to identify possible edge cases 

### Day 3: Secure Code Review 
#### Session 1 - Injection - Output Encoding 
* Injection Review: output encoding, dangerous functions 
* Output Encoding Exercise: Use manual techniques to identify dangerous functions (SQL, XSS, SSRF) along with AI to find possible vulnerabilities 
#### Session 2 - Cryptographic 
* Cryptographic analysis: encoding, encryption, hashing, and stored secrets 
* Cryptographic Exercise: manual and AI techniques for identifying cryptographic issues in code. 
#### Session 3 - Configuration Analysis 
* Configuration review: understanding framework gotchas, dependency issues, and config file pitfalls 
* Configuration Exercise: Manual analysis, AI integration with additional tools 
#### Session 4 - Recap & Advanced Secure Code Review Concepts 
* Brief summary of discussed theory and methodologies
* Discussion of advanced techniques and AI trends in secure code analysis
#### Session 5 - Live Walkthrough: End‑to‑End Code Review 
* Instructor‑led demonstration using a sample application (e.g., Django Vulnerable Task Manager)
* Step‑by‑step analysis: risk assessment, vulnerability identification, and remediation strategies

### Day 4: Group Breakout 
#### Session 1 - Briefing & Group Formation 
* Overview of the OSS code base selected for analysis
* Group assignments, objectives, and deliverable expectations
* Review of methodologies and tools (both manual and AI‑aided)
#### Session 2 - Breakout Lab: Hands‑On Analysis 
* In‑depth group work analyzing the OSS code base for security flaws
* Instructors circulate to provide guidance and answer questions
* Application of secure code review and LLM‑enhanced analysis techniques
#### Session 3 - Group Presentations & Peer Review 
* Each group presents their findings and analysis approach
* Peer discussion and feedback on vulnerabilities uncovered and remediation suggestions
#### Session 4 - Final Wrap‑Up & Key Takeaways 
* Consolidation of lessons learned from the breakout #### Session
* Open Q&A, discussion on applying techniques in real‑world scenarios, and course feedback
* Final remarks and next steps
