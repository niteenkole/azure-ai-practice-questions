import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

print("RUNNING FULLY MANUAL THREAD DEMO VERSION")

# ------------------------------------------------------------
# Load environment variables from .env file
# ------------------------------------------------------------
# Required values:
# PROJECT_ENDPOINT = Azure AI Foundry project endpoint
# MODEL_DEPLOYMENT_NAME = deployed model name in Azure AI Foundry
# ------------------------------------------------------------

load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]

# ------------------------------------------------------------
# Create AgentsClient
# ------------------------------------------------------------
# DefaultAzureCredential uses your Azure CLI login.
# Make sure you already ran:
#
# az login
#
# This client is the connection to Azure AI Agent Service.
# ------------------------------------------------------------

agents_client = AgentsClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)


def wait_for_run(thread_id, run_id):
    """
    Wait until an agent run finishes.

    A Run is one execution of the agent against a thread.

    The run can have different statuses:
    - queued
    - in_progress
    - completed
    - failed
    - cancelled
    - expired
    """

    while True:
        run = agents_client.runs.get(
            thread_id=thread_id,
            run_id=run_id
        )

        if run.status in ["completed", "failed", "cancelled", "expired"]:
            return run

        time.sleep(1)


def run_agent(agent_id, thread_id):
    """
    Execute the agent against the messages stored in a thread.

    Some SDK versions support create_and_process().
    If not, we fall back to create() and manually wait for completion.
    """

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
    """
    Extract readable text from an assistant message.

    SDK message content can contain different content item types.
    This helper extracts the text safely.
    """

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
    """
    Get the latest assistant response from a thread.

    A thread contains both user and assistant messages.
    This function filters assistant messages and returns the newest one.
    """

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
    """
    Send a user message to a specific thread and run the agent.

    This is the most important part of the demo.

    The same agent can be used with different threads.
    The thread_id determines which conversation history the agent can see.
    """

    print("\n" + "=" * 80)
    print("USER MESSAGE")
    print("=" * 80)
    print(user_message)

    # Add the user message to the selected thread.
    agents_client.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # Run the agent on the selected thread.
    run = run_agent(agent_id, thread_id)

    print("\nRUN STATUS")
    print("=" * 80)
    print(run.status)

    # Get and print latest assistant response from the same thread.
    assistant_response = get_latest_assistant_message(thread_id)

    print("\nASSISTANT RESPONSE")
    print("=" * 80)
    print(assistant_response)
    print("=" * 80)


def manual_loop(title, prompt_text, agent_id, thread_id):
    """
    Manual input loop.

    This lets you type messages live during the demo.
    Type 'done' to stop entering messages for the current section.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print("Type one message at a time.")
    print("Type 'done' when finished.")
    print("-" * 80)

    while True:
        user_input = input(prompt_text).strip()

        if user_input.lower() == "done":
            break

        if user_input:
            send_message(
                agent_id=agent_id,
                thread_id=thread_id,
                user_message=user_input
            )


def main():
    """
    Main demo flow.

    This demo creates:
    - One Agent
    - Thread A
    - Thread B

    Thread A receives facts and remembers them.
    Thread B starts fresh and does not know Thread A history.

    This proves:
    Thread = Conversation Session + Message History
    """

    print("\nCreating Azure AI Agent...")
    print("=" * 80)

    # ------------------------------------------------------------
    # Create one Agent
    # ------------------------------------------------------------
    # The agent defines:
    # - Model
    # - Instructions
    # - Behavior
    #
    # Important:
    # The agent does not hold conversation memory by itself.
    # Conversation memory is maintained by the Thread.
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # THREAD A
    # ------------------------------------------------------------
    # Thread A is the first conversation.
    # Messages added here are part of Thread A history.
    # ------------------------------------------------------------

    print("\nCreating THREAD A...")
    print("=" * 80)

    thread_a = agents_client.threads.create()

    print("Thread A created successfully.")
    print(f"Thread A ID: {thread_a.id}")
    print("=" * 80)

    print("\nVIDEO TALKING POINT:")
    print("This is Thread A.")
    print("Any messages we add here belong to this conversation.")
    print("Thread A will maintain conversation history for this session.")
    print("=" * 80)

    # Manually enter facts into Thread A.
    manual_loop(
        title="THREAD A: Enter facts or messages you want the assistant to remember",
        prompt_text="Thread A message: ",
        agent_id=agent.id,
        thread_id=thread_a.id
    )

    # Ask questions in Thread A.
    manual_loop(
        title="THREAD A: Ask any questions to prove this thread remembers",
        prompt_text="Thread A question: ",
        agent_id=agent.id,
        thread_id=thread_a.id
    )

    # ------------------------------------------------------------
    # THREAD B
    # ------------------------------------------------------------
    # Thread B uses the same agent, model, and instructions.
    # But Thread B is a new conversation.
    # It should not remember Thread A history.
    # ------------------------------------------------------------

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

    # Manually ask questions in Thread B.
    manual_loop(
        title="THREAD B: Manually ask questions to test if this new thread remembers Thread A",
        prompt_text="Thread B question: ",
        agent_id=agent.id,
        thread_id=thread_b.id
    )

    # ------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------

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

    # Optional cleanup.
    # Keeping or deleting the agent is your choice.
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
