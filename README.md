## Introduction

Implements a simple filesystem based MCP server and chat agent which uses the MCP server to response to queries about filesystem


## Running



**Setup Python Env**

Step 1. Preferably create a fresh `venv` and run following to install required dependencies.

```
python -m pip install -r requirements.txt

```

Step 2. Install OLLAMA and download qwen3:4b model. Start Ollama server by running following

```
ollama serve

```


Step 3. Run `agent.py` to start the chat agent

```
python3 agent.py
```
