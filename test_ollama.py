import sys

from ollama import chat


def main() -> None:
    """
    Test whether Python can communicate with Ollama.
    """

    try:
        response = chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Reply with exactly: "
                        "Local AI connection successful."
                    ),
                }
            ],
        )

        print(response.message.content)

    except Exception as error:
        print("Local AI connection failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Error details: {error}")
        print(
            "Make sure the Ollama application is running "
            "and that llama3.2 is installed."
        )

        sys.exit(1)


if __name__ == "__main__":
    main()