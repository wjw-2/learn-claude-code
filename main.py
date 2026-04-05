import os
import sys
import uuid
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("DASHSCOPE_API_KEY"):
    print("ERROR: DASHSCOPE_API_KEY not found!")
    print("Please configure your Aliyun DashScope API Key in .env file.")
    sys.exit(1)

from agent.graph import agent_graph


def main():
    print("=" * 50)
    print("Code Agent powered by LangGraph + DashScope (Qwen)")
    print("Arch: LangChain + LangGraph + Qwen Model")
    print("=" * 50)
    print("Type 'exit' or 'quit' to exit.\n")

    # Each session gets a unique thread_id for conversation persistence
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            query = input("[User]> ")
            if query.strip().lower() in ["exit", "quit"]:
                print("Bye!")
                break
            if not query.strip():
                continue

            print("[Agent] Thinking...\n")

            result = agent_graph.invoke(
                {"messages": [{"role": "user", "content": query}]},
                config=config,
            )

            # Extract the final assistant message
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content and not getattr(msg, "tool_calls", None):
                    print(f"\n[Response]:\n{msg.content}\n")
                    print("-" * 50)
                    break
            else:
                print("\n[Response]: Agent completed without text output.\n")
                print("-" * 50)

        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"\n[Error]: {e}\n")


if __name__ == "__main__":
    main()
