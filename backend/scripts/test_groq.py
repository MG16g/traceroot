from app.llm.provider import get_llm


def main():
    llm = get_llm()

    response = llm.invoke(
        "Reply with exactly: TraceRoot Groq connection successful"
    )

    print(response.content)


if __name__ == "__main__":
    main()