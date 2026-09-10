from rag.chatbot import TNGovernmentChatbot

chatbot = TNGovernmentChatbot()

questions = [
    "Who are the beneficiaries of Training to Farmers?",
    "What is the funding pattern for Training to Farmers?",
    "How can farmers avail the Training to Farmers scheme?",
]

for question in questions:
    print("\n" + "=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    documents = chatbot.retrieve(question)

    for i, document in enumerate(documents, start=1):
        print("\n--- RESULT", i, "---")
        print("Scheme:", document.metadata.get("scheme_name"))
        print("Funding:", document.metadata.get("funding_pattern"))
        print("Beneficiaries:", document.metadata.get("beneficiaries"))
        print("CONTENT:")
        print(document.page_content)