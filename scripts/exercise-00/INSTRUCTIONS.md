# Exercise 0x00 - Lab Setup

## Objective
Install all libraries and support software needed to execute course scripts. Test functionality for both local (Ollama) and remote (AWS Bedrock) LLM access.

## Instructions
### 1. Clone Repository
Clone the course repository from GitHub
```sh
git clone https://github.com/absoluteappsec/nextgen
```

### 2. Create Virtual Environment
Setup and run an isolated Python 3.12 environment
```sh
python3.12 -m venv venv
source venv/bin/activate
export KMP_DUPLICATE_LIB_OK=TRUE
```

### 3. Install Dependencies
Install the required python packages
```sh
pip install -r requirements.txt
```

### 4. Configure the Environment (AWS Bedrock)
_Note: Skip to Extras section if running Ollama and local only models_
Place the provided AWS tokens into the `.env` file in the _scripts_ directory
```sh
mv scripts/.env.example scripts/.env
```

### 5. Test Setup
Run the chatbot from the _scripts_ directory via the provided script.
```sh
cd scripts
python exercise-00/chatbot.py
```
Output:
```
Juice Shop Assistant (type 'exit' to quit)

You: How can you help me?
I can help you with various aspects of the OWASP Juice Shop application. Based on the context provided, I can assist you with:

1. Chatbot Interactions
- I can help you understand how the support chatbot works
- I can explain how to interact with the chatbot
- I can provide insights into chatbot-related challenges

2. Application Features
- Explain different routes and endpoints
- Discuss security configurations
- Help you understand various application functionalities

3. Challenges and Security
- Provide information about different security challenges
- Explain potential vulnerabilities in the application
- Discuss mitigation strategies

What specific area would you like to explore or get help with? I'm ready to provide clear and concise information about the OWASP Juice Shop application.
```

## Extras
### Alternate Instructions for Ollama/Local Only LLMs

### 4. Configure the Environment (Ollama)
Make sure Ollama is running locally with required models installed

```sh
ollama list
```
Should see EmbeddingGemma and Gemma3 installed
```
NAME                                 ID              SIZE      MODIFIED   
embeddinggemma:latest                85462619ee72    621 MB    2 weeeks ago    
gemma3:latest                        a2af6cc3eb7f    3.3 GB    2 weeks ago  
```
#### 4b. Install gemma3 (if not installed)
```sh
ollama pull gemma3
ollama pull embeddinggemma
```

### 5. Test Setup
Run the chatbot from the _scripts_ directory via the provided script.
```sh
cd scripts
python exercise-1/chatbot_ollama.py
```
