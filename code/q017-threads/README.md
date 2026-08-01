# Q017 - Azure AI Agent Service SDK Thread Demo

This folder contains a Python SDK demo that demonstrates how **Threads** work in Azure AI Agent Service SDK.

The demo supports the AI-103 concept:

> A Thread represents a user-agent conversation session and maintains conversation history.

---

# What This Demo Shows

This demo proves the following concept:

```text
Same Agent + Thread A = Remembers conversation history

Same Agent + Thread B = Starts fresh
```

The same Azure AI Agent can participate in multiple conversations.

Each conversation maintains its own history through a separate thread.

---

# Key Concept

Think of it this way:

```text
Agent = AI Assistant

Thread = Conversation History

Run = Execution

Client = Connection
```

The Agent defines behavior.

The Thread stores messages.

The Run executes the Agent against messages stored in the Thread.

---

# Demo Architecture

```text
Same Agent
   |
   |-- Thread A
   |     |-- My name is Niteen
   |     |-- I work on Azure AI Foundry demos
   |     |-- My favorite topic is AI Agents
   |     |
   |     |-- What is my name?
   |     |-- Where do I work?
   |     |-- What is my favorite topic?
   |     |
   |     |-- Remembers conversation history
   |
   |
   |-- Thread B
         |
         |-- What is my name?
         |-- Where do I work?
         |-- What is my favorite topic?
         |
         |-- Starts fresh
```

The Agent stays the same.

Only the Thread changes.

---

# Expected Learning Outcome

After running this demo you should understand:

```text
Client
```

Connects your application to Azure AI Agent Service.

```text
Agent
```

Defines the AI assistant.

```text
Thread
```

Maintains conversation history.

```text
Run
```

Processes messages inside a thread.

---

# Project Structure

```text
q017-threads
├── README.md
├── thread_demo_interactive.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

# Prerequisites

Before running the demo, ensure you have:

- Azure AI Foundry project
- Deployed model
- Python 3.9 or later
- Azure CLI installed
- Azure CLI authenticated
- Required Python packages

---

# Step 1 - Create Python Virtual Environment

## macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

After activation you should see:

```text
(.venv)
```

in your terminal.

---

# Step 2 - Install Dependencies

Install packages:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```text
azure-ai-agents
azure-identity
python-dotenv
```

---

# Step 3 - Authenticate to Azure

Login:

```bash
az login
```

Optional:

List subscriptions:

```bash
az account list --output table
```

Set subscription:

```bash
az account set --subscription "<subscription-name-or-id>"
```

Verify active subscription:

```bash
az account show --output table
```

---

# Step 4 - Configure Environment Variables

Create a local file named:

```text
.env
```

Add:

```text
PROJECT_ENDPOINT=<your-project-endpoint>
MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

Example:

```text
PROJECT_ENDPOINT=https://your-ai-resource.services.ai.azure.com/api/projects/your-project
MODEL_DEPLOYMENT_NAME=gpt-4o
```

Do not upload `.env` to GitHub.

---

# .env.example

The repository includes a safe template:

```text
PROJECT_ENDPOINT=<your-project-endpoint>
MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

Copy it locally and rename it to:

```text
.env
```

---

# Step 5 - Run the Demo

Execute:

```bash
python thread_demo_interactive.py
```

You should see:

```text
RUNNING FULLY MANUAL THREAD DEMO VERSION
```

If you do not see that line, verify you are running the correct script.

---

# Demo Walkthrough

## Create Agent

The script creates one Azure AI Agent.

Agent Instructions:

```text
Use only information provided in the current thread.

If information was not provided in the current thread,
clearly say you do not know.

Do not use information from other threads.
```

---

# Thread A

The script creates:

```text
Thread A
```

You manually enter facts.

Example:

```text
My name is Niteen.
```

```text
I work on Azure AI Foundry demos.
```

```text
My favorite Azure AI topic is Agents.
```

Then type:

```text
done
```

---

# Thread A Verification Questions

Example:

```text
What is my name?
```

```text
Where do I work?
```

```text
What is my favorite Azure AI topic?
```

```text
Summarize everything you know about me from this conversation.
```

Expected result:

```text
Thread A remembers previous messages.
```

---

# Thread B

The script then creates:

```text
Thread B
```

Same Agent.

Same Model.

Same Instructions.

Different Thread.

---

# Thread B Verification Questions

Ask similar questions:

```text
What is my name?
```

```text
Where do I work?
```

```text
What is my favorite Azure AI topic?
```

Expected result:

```text
Thread B does not know.
```

because those facts were never entered into Thread B.

---

# Expected Result

Thread A:

```text
Remembers conversation history
```

Thread B:

```text
Starts fresh
```

This proves:

```text
Memory belongs to the Thread.
```

---

---

# Troubleshooting

## Authentication Error

Login again:

```bash
az login
```

Verify subscription:

```bash
az account show --output table
```

---

## Missing Environment Variables

Confirm `.env` contains:

```text
PROJECT_ENDPOINT=...
MODEL_DEPLOYMENT_NAME=...
```

---

## Wrong Model Deployment Name

Use the deployment name configured in Azure AI Foundry.

Do not assume the deployment name matches the model name.

---

## Thread B Still Remembers

Verify the script creates:

```python
thread_b = agents_client.threads.create()
```

and that Agent instructions include:

```text
Do not use information from other threads.
```

---

# Security Notes

Never upload:

```text
.env
API Keys
Secrets
Tenant IDs
Subscription IDs
Personal Data
Company Data
```

Use:

```text
.env.example
```

for repository examples.

---

# Related Resources

Full Video:

```text
Coming Soon
```

Concept Short:

```text
Coming Soon
```

Question Short:

```text
Coming Soon
```

---

# Author

Niteen Kole

Cybersecurity Simplified
