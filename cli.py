import asyncio
from agent.agent import run_query, reset_conversation


def main():
    print("=" * 60)
    print("  🤖  AI Email Assistant  (Groq + MCP)")
    print("=" * 60)
    print("Commands: 'reset' to clear history | 'exit' to quit")
    print("-" * 60)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            query = input("\nYou: ").strip()

            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                print("Goodbye! 👋")
                break
            if query.lower() == "reset":
                reset_conversation()
                print("Conversation reset.")
                continue

            print("Assistant: ", end="", flush=True)
            response = loop.run_until_complete(run_query(query))
            print(response)

        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n Error: {e}")

    loop.close()


if __name__ == "__main__":
    main()