# Exercise 0x04 - Embed & Store (aka RAG)
## Objective
Learn to transform code repositories, documents, and other content into searchable vector databases using FAISS. This foundational technique enables semantic search across documents, making it possible to find relevant code snippets and text based on meaning rather than exact keyword matches. 

## Instructions
### 1. Open the Script
Open _exercise-04/embed\_and\_store.py_ and view the process taken to parse identify relevant source code files, parse them appropriately, and store them in a vector database utilizing AI embeddings.

The initial script focuses on the Bridge Troll open source application. Since we know this is Ruby on Rails application, the loader script checks for .rb files for analysis.

```py
loader = GenericLoader.from_filesystem(
    local_path,
    glob="**/*",
    # CHANGE .rb TO THE RELEVANT FILE EXTENSION
    suffixes=[".rb"],
    # CHANGE Language.RUBY TO THE RELEVANT LANGUAGE
    parser=LanguageParser(language=Language.RUBY),
    show_progress=True,
)

documents = loader.load()
```

Once loaded into a document array, each file is parsed using a language-focused splitter, which maintains overlap to keep files and functions together.
```py
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.RUBY, chunk_size=8000, chunk_overlap=100
)
texts = splitter.split_documents(documents)
```

Finally, this array of texts is vectorized using the specified embeddings and the vector database is created

```py
db_name = "bridge_troll"

db = FAISS.from_documents(texts, embeddings)
db.save_local(f"../vector_databases/{db_name}.faiss")
```

This script only needs to be run one time to create the database. Multiple runs does not change the stored results unless the source files or metadata has been updated. Run the script to create the database for the bridge troll application.

```sh
python scripts/exercise-04/embed_and_store.py
```

### 2. Modify Script
This script was built to be run against a Ruby on Rails application. Pick out another open source project from GitHub that is built using a different language (e.g. Python, PHP, Java).

Your task is to modify and run both the _embed\_and\_store.py_ and _exercise-02\building_with_context.py\_ script against a different open source project. This will create a feature-complete process of pulling code, creating vectorized context, and querying those results for specific knowledge.

Note that creating vector databases can be a lengthy process when you are analyzing millions of lines of code. The targeted application in this case should be of reasonable size (let's stay away from the linux kernel and kubernetes for now) to allow for completion.