import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

print("RUNNING FULLY MANUAL THREAD DEMO VERSION")

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


def manual_loop(title, prompt_text, agent_id, thread_id):
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

    # ------------------------------------------------------------------
    # THREAD A
    # ------------------------------------------------------------------

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

    manual_loop(
        title="THREAD A: Enter facts or messages you want the assistant to remember",
        prompt_text="Thread A message: ",
        agent_id=agent.id,
        thread_id=thread_a.id
    )

    manual_loop(
        title="THREAD A: Ask any questions to prove this thread remembers",
        prompt_text="Thread A question: ",
        agent_id=agent.id,
        thread_id=thread_a.id
    )

    # ------------------------------------------------------------------
    # THREAD B
    # ------------------------------------------------------------------

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

    manual_loop(
        title="THREAD B: Manually ask questions to test if this new thread remembers Thread A",
        prompt_text="Thread B question: ",
        agent_id=agent.id,
        thread_id=thread_b.id
    )

    # ------------------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------------------

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
