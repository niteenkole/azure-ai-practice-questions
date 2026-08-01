# Azure AI Agent Service SDK - Thread Demo

This demo shows how **Threads** work in the Azure AI Agent Service SDK.

The main idea:

```text
Same Agent + Thread A = Remembers conversation history
Same Agent + Thread B = Starts fresh
```

This is useful for understanding the AI-103 concept:

```text
Thread = Conversation session + Message history
```

---

## What This Demo Proves

In the Azure AI Agent Service SDK, the main objects are:

```text
Client = Connection to Azure AI Agent Service
Agent = AI assistant definition
Thread = Conversation history / user-agent session
Run = One execution of the agent
```

This demo creates:

```text
One Agent
Two Threads
```

You manually enter facts into **Thread A**. Then you ask questions in Thread A and the agent remembers.

Then you create **Thread B** using the same agent, same model, and same instructions. When you ask the same questions in Thread B, the agent should not remember anything from Thread A.

That proves the conversation memory belongs to the **Thread**, not the Agent.

---

## Demo Architecture

```text
Same Agent
   |
   |-- Thread A
   |     |-- User fact 1
   |     |-- User fact 2
   |     |-- User fact 3
   |     |-- Verification questions
   |
   |-- Thread B
         |-- New conversation
         |-- No memory from Thread A
```

---

## Prerequisites

You need:

- Azure AI Foundry project
- Deployed model in your Foundry project
- Python 3.9 or later
- Azure CLI installed
- Azure CLI authenticated using `az login`
- Required Python packages:
  - `azure-ai-agents`
  - `azure-identity`
  - `python-dotenv`

---

## Step 1: Create Project Folder

```bash
mkdir ai-agent-thread-demo
cd ai-agent-thread-demo
```

---

## Step 2: Create Python Virtual Environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You should see this at the beginning of your terminal prompt:

```text
(.venv)
```

---

## Step 3: Install Packages

```bash
python -m pip install --upgrade pip
pip install azure-ai-agents azure-identity python-dotenv
```

Optional: create `requirements.txt`:

```text
azure-ai-agents
azure-identity
python-dotenv
```

Install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Step 4: Login to Azure

```bash
az login
```

If you have multiple subscriptions:

```bash
az account list --output table
az account set --subscription "<your-subscription-id-or-name>"
az account show --output table
```

---

## Step 5: Create `.env` File

Create a file named `.env` in the project folder.

```text
PROJECT_ENDPOINT=https://<your-ai-services-name>.services.ai.azure.com/api/projects/<your-project-name>
MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

Example:

```text
PROJECT_ENDPOINT=https://my-ai-resource.services.ai.azure.com/api/projects/my-project
MODEL_DEPLOYMENT_NAME=gpt-4o
```

Important:

- Use the **project endpoint** from Azure AI Foundry.
- Use the **deployment name**, not just the model name.
- Do not upload your `.env` file to GitHub.

---

## Step 6: Create `.env.example` for GitHub

Create a safe sample file named `.env.example`:

```text
PROJECT_ENDPOINT=<your-project-endpoint>
MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

Upload `.env.example` to GitHub, but never upload `.env`.

---

## Step 7: Create `.gitignore`

Create a `.gitignore` file:

```text
.env
.venv/
__pycache__/
*.pyc
.DS_Store
```

---

## Step 8: Create Python Script

Create a file named:

```text
thread_demo_interactive.py
```

Paste this code:

```python
import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]

agents_client = AgentsClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)


def wait_for_run(thread_id, run_id):
    while True:
        run = agents_client.runs.get(
            thread_id=thread_id,
            run_id=run_id
        )

        if run.status in ["completed", "failed", "cancelled", "expired"]:
            return run

        time.sleep(1)


def run_agent(agent_id, thread_id):
    try:
        run = agents_client.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent_id
        )
        return run
    except AttributeError:
        run = agents_client.runs.create(
            thread_id=thread_id,
            agent_id=agent_id
        )
        return wait_for_run(thread_id, run.id)


def extract_text_from_message(message):
    text_parts = []

    for content_item in message.content:
        if hasattr(content_item, "text") and content_item.text:
            if hasattr(content_item.text, "value"):
                text_parts.append(content_item.text.value)
            else:
                text_parts.append(str(content_item.text))
        else:
            text_parts.append(str(content_item))

    return "\n".join(text_parts)


def get_latest_assistant_message(thread_id):
    messages = list(agents_client.messages.list(thread_id=thread_id))

    assistant_messages = []

    for message in messages:
        role = str(message.role).lower()

        if "assistant" in role or "agent" in role:
            assistant_messages.append(message)

    if not assistant_messages:
        return "No assistant response found."

    try:
        latest_message = sorted(
            assistant_messages,
            key=lambda msg: msg.created_at,
            reverse=True
        )[0]
    except Exception:
        latest_message = assistant_messages[0]

    return extract_text_from_message(latest_message)


def send_message(agent_id, thread_id, user_message):
    print("\n" + "=" * 80)
    print("USER MESSAGE")
    print("=" * 80)
    print(user_message)

    agents_client.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    run = run_agent(agent_id, thread_id)

    print("\nRUN STATUS")
    print("=" * 80)
    print(run.status)

    assistant_response = get_latest_assistant_message(thread_id)

    print("\nASSISTANT RESPONSE")
    print("=" * 80)
    print(assistant_response)
    print("=" * 80)


def interactive_input_loop(title, prompt_text):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print("Type one item at a time.")
    print("Type 'done' when finished.")
    print("-" * 80)

    items = []

    while True:
        user_input = input(prompt_text).strip()

        if user_input.lower() == "done":
            break

        if user_input:
            items.append(user_input)

    return items


def main():
    print("\nCreating Azure AI Agent...")
    print("=" * 80)

    agent = agents_client.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="thread-memory-demo-agent",
        instructions=(
            "You are a helpful assistant. "
            "Use only information provided in the current thread. "
            "If information was not provided in the current thread, clearly say you do not know. "
            "Do not use information from other conversations or other threads."
        )
    )

    print("Agent created successfully.")
    print(f"Agent ID: {agent.id}")
    print("=" * 80)

    # THREAD A
    print("\nCreating THREAD A...")
    print("=" * 80)

    thread_a = agents_client.threads.create()

    print("Thread A created successfully.")
    print(f"Thread A ID: {thread_a.id}")
    print("=" * 80)

    print("\nVIDEO TALKING POINT:")
    print("This is Thread A. Any messages we add here belong to this conversation.")
    print("The thread will maintain conversation history for this session.")
    print("=" * 80)

    facts = interactive_input_loop(
        title="THREAD A: Enter facts you want the assistant to remember",
        prompt_text="Enter fact for Thread A: "
    )

    if not facts:
        print("\nNo facts entered. Exiting demo.")
        agents_client.delete_agent(agent.id)
        return

    print("\nSending facts to THREAD A...")
    print("=" * 80)

    for fact in facts:
        send_message(
            agent_id=agent.id,
            thread_id=thread_a.id,
            user_message=fact
        )

    thread_a_questions = interactive_input_loop(
        title="THREAD A: Enter questions to test what the assistant remembers",
        prompt_text="Enter question for Thread A: "
    )

    if not thread_a_questions:
        print("\nNo Thread A questions entered. Exiting demo.")
        agents_client.delete_agent(agent.id)
        return

    print("\nASKING QUESTIONS IN THREAD A")
    print("=" * 80)
    print("Expected result: The assistant should remember facts entered in Thread A.")
    print("=" * 80)

    for question in thread_a_questions:
        send_message(
            agent_id=agent.id,
            thread_id=thread_a.id,
            user_message=question
        )

    # THREAD B
    print("\nCreating THREAD B...")
    print("=" * 80)

    thread_b = agents_client.threads.create()

    print("Thread B created successfully.")
    print(f"Thread B ID: {thread_b.id}")
    print("=" * 80)

    print("\nVIDEO TALKING POINT:")
    print("Now we are using the same agent, same model, and same instructions.")
    print("But this is a brand-new thread.")
    print("Thread B should not remember anything from Thread A.")
    print("=" * 80)

    thread_b_questions = interactive_input_loop(
        title="THREAD B: Enter questions manually to test if this new thread remembers Thread A",
        prompt_text="Enter question for Thread B: "
    )

    if not thread_b_questions:
        print("\nNo Thread B questions entered. Skipping Thread B test.")
    else:
        print("\nASKING QUESTIONS IN THREAD B")
        print("=" * 80)
        print("Expected result: The assistant should NOT know facts from Thread A.")
        print("=" * 80)

        for question in thread_b_questions:
            send_message(
                agent_id=agent.id,
                thread_id=thread_b.id,
                user_message=question
            )

    # FINAL SUMMARY
    print("\nDEMO COMPLETE")
    print("=" * 80)

    print("Key takeaway:")
    print("Same Agent + Thread A = Remembers Thread A conversation history")
    print("Same Agent + Thread B = Starts fresh")
    print()
    print("Agent = AI Assistant Definition")
    print("Thread = Conversation Session + Message History")
    print("Run = One Execution")
    print("Client = Connection to Azure AI Agent Service")
    print("=" * 80)

    cleanup = input("\nDelete the test agent now? Type yes or no: ").strip().lower()

    if cleanup == "yes":
        print("\nDeleting test agent...")
        agents_client.delete_agent(agent.id)
        print("Test agent deleted.")
    else:
        print("\nTest agent kept.")
        print(f"Agent ID: {agent.id}")


if __name__ == "__main__":
    main()
```

---

## Step 9: Run The Demo

```bash
python thread_demo_interactive.py
```

---

## Suggested Demo Inputs

### Thread A Facts

Enter these one by one:

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

### Thread A Questions

Enter these one by one:

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

Then type:

```text
done
```

Expected result: the assistant should remember the facts.

---

### Thread B Questions

Enter these one by one:

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

Then type:

```text
done
```

Expected result: the assistant should not know the Thread A facts.

---

---


