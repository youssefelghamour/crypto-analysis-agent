import uuid
from langchain_core.messages import HumanMessage
from agent.graph import build_graph


def main():
    graph, conn = build_graph()

    print("Crypto Analysis Agent")
    print("Ask me anything about cryptocurrencies.")
    print("Type 'exit' or 'quit' to leave.\n")

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
                    {"messages": [HumanMessage(content=user_input)]},
                    config,
                )

                last_ai = next(
                    (
                        message
                        for message in reversed(result["messages"])
                        if message.type == "ai"
                        and not getattr(message, "tool_calls", [])
                    ),
                    None,
                )

                print(
                    f"Agent: {last_ai.content}\n"
                    if last_ai
                    else "Agent: [No reply]\n"
                )
            except Exception as e:
                print(f"Agent: Something went wrong ({e}). Please try again.\n")

    except KeyboardInterrupt:
        print("\nBye!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
