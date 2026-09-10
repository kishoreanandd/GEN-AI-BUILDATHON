from rag.chatbot import TNGovernmentChatbot


def test_retrieval():

    chatbot = TNGovernmentChatbot()

    questions = [
        "Who are the beneficiaries of Training to Farmers?",
        "What is the funding pattern for Training to Farmers?",
        "How can farmers avail the Training to Farmers scheme?"
    ]

    for question in questions:

        print("\n")
        print("=" * 80)
        print("QUESTION:")
        print(question)
        print("=" * 80)

        documents = chatbot.retrieve(question)

        for i, document in enumerate(documents, start=1):

            print(f"\nDOCUMENT {i}")
            print("-" * 80)

            print(
                "Scheme:",
                document.metadata.get("scheme_name")
            )

            print(
                "Department:",
                document.metadata.get("department")
            )

            print(
                "Source:",
                document.metadata.get("source_url")
            )

            print("\nCONTENT:")
            print(
                document.page_content[:1500]
            )