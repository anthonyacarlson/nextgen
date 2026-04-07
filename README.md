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

## Alternative LLM Options

* Ollama
* Gemma3 and EmbeddingGemma in Ollama/local tasks

```
ollama pull gemma3
ollama pull embeddinggemma
```
