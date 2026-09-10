import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from deepeval import evaluate

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric
)

from deepeval.test_case import LLMTestCase

from rag.chatbot import TNGovernmentChatbot


def run_evaluation():

    chatbot = TNGovernmentChatbot()

    test_questions = [
        {
            "question": "Who are the beneficiaries of Training to Farmers?",
            "expected": "Farmers."
        },
        {
            "question": "What is the funding pattern for Training to Farmers?",
            "expected": "Rs.300 per farmer for 2 days."
        },
        {
            "question": "How can farmers avail the Training to Farmers scheme?",
            "expected": "Farmers can apply through the specified Agriculture Department officers."
        }
    ]

    test_cases = []

    for test in test_questions:

        question = test["question"]

        documents = chatbot.retrieve(
            question
        )

        answer = chatbot.generate_answer(
            question,
            documents
        )

        retrieval_context = [
            document.page_content
            for document in documents
        ]

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            expected_output=test["expected"],
            retrieval_context=retrieval_context
        )

        test_cases.append(test_case)

        print("\n" + "=" * 70)
        print("QUESTION:")
        print(question)

        print("\nANSWER:")
        print(answer)

        print("\nRETRIEVED DOCUMENTS:")
        print(len(documents))

    metrics = [

        AnswerRelevancyMetric(
            threshold=0.7
        ),

        FaithfulnessMetric(
            threshold=0.7
        ),

        ContextualRelevancyMetric(
            threshold=0.7
        )
    ]

    evaluate(
        test_cases=test_cases,
        metrics=metrics
    )


if __name__ == "__main__":
    run_evaluation()