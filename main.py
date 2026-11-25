"""CLI entry point for the Crypto Analysis Agent."""
import uuid
from graphs.main_graph import build_main_graph


def main():
    graph, conn = build_main_graph()

    print("Crypto Analysis Agent")
    print("Ask me anything about cryptocurrencies.")
    print("Type 'exit' or 'quit' to leave.\n")

    # Keep the same thread ID throughout this conversation
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
        }
    }

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\nBye!")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("Bye!")
                break

            try:
                result = graph.invoke(
                    {
                        "request": user_input,
                        "messages": [
                            {"role": "user", "content": user_input}
                        ],
                    },
                    config=config,
                )

                if result["intent"] == "discussion":
                    response = result.get("discussion_response")
                    print(f"Agent: {response or '[No reply]'}\n")

                elif result["intent"] == "report":
                    error = result.get("validation_error")
                    print(f"Agent: {error or '[Report unavailable]'}\n")

            except Exception as e:
                print(
                    f"Agent: Something went wrong ({e}). "
                    "Please try again.\n"
                )

    except KeyboardInterrupt:
        print("\nBye!")

    finally:
        conn.close()


if __name__ == "__main__":
    main()