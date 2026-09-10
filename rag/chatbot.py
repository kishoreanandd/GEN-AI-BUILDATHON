import sys
from pathlib import Path

# Allow imports when running files from subfolders
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from rag.prompts import RAG_PROMPT
from rag.guardrails import (
    has_relevant_context,
    is_allowed_question,
    get_fallback_message,
    validate_answer,
)


# ============================================================
# CONFIGURATION
# ============================================================

VECTORSTORE_DIR = Path("data/vectorstore")

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-5-mini"

RETRIEVAL_K = 4

load_dotenv()


# ============================================================
# TAMIL NADU GOVERNMENT SCHEMES CHATBOT
# ============================================================

class TNGovernmentChatbot:

    def __init__(self):
        print("Loading Tamil Nadu Government Schemes chatbot...")

        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL
        )

        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0
        )

        self.vectorstore = self.load_vectorstore()

        print("Chatbot loaded successfully.")

    # ========================================================
    # LOAD VECTOR DATABASE
    # ========================================================

    def load_vectorstore(self):

        if not VECTORSTORE_DIR.exists():
            raise FileNotFoundError(
                f"Vectorstore not found at: {VECTORSTORE_DIR}\n"
                "Run the ingestion script first."
            )

        vectorstore = FAISS.load_local(
            str(VECTORSTORE_DIR),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        print(
            f"Loaded {len(vectorstore.docstore._dict)} "
            "documents from FAISS."
        )

        return vectorstore

    # ========================================================
    # GET ALL SCHEME NAMES
    # ========================================================

    def get_scheme_names(self):

        scheme_names = set()

        for document in self.vectorstore.docstore._dict.values():

            scheme_name = document.metadata.get(
                "scheme_name",
                ""
            ).strip()

            if scheme_name:
                scheme_names.add(scheme_name)

        return sorted(
            scheme_names,
            key=len,
            reverse=True
        )

    # ========================================================
    # DETECT SCHEME NAME
    # ========================================================

    def detect_scheme_name(self, question):

        question_lower = question.lower()

        scheme_names = self.get_scheme_names()

        for scheme_name in scheme_names:

            if scheme_name.lower() in question_lower:
                return scheme_name

        return None

    # ========================================================
    # DETECT QUESTION FIELD
    # ========================================================

    def detect_field(self, question):

        question_lower = question.lower()

        # ----------------------------------------------------
        # HOW TO APPLY / AVAIL
        # ----------------------------------------------------

        if (
            "how to avail" in question_lower
            or "how can farmers avail" in question_lower
            or "how can i avail" in question_lower
            or "how can we avail" in question_lower
            or "how do farmers avail" in question_lower
            or "how do i avail" in question_lower
            or "how to apply" in question_lower
            or "how can i apply" in question_lower
            or "how can farmers apply" in question_lower
            or "how can we apply" in question_lower
            or "how do farmers apply" in question_lower
            or "how do i apply" in question_lower
            or "application procedure" in question_lower
            or "application process" in question_lower
            or "where to apply" in question_lower
            or "where can i apply" in question_lower
            or "apply for the scheme" in question_lower
            or "application" in question_lower
            or "procedure to apply" in question_lower
        ):
            return "how_to_avail"

        # ----------------------------------------------------
        # FUNDING
        # ----------------------------------------------------

        if (
            "funding pattern" in question_lower
            or "funding" in question_lower
            or "financial assistance" in question_lower
            or "financial benefit" in question_lower
            or "how much" in question_lower
            or "amount" in question_lower
            or "money" in question_lower
            or "financial support" in question_lower
        ):
            return "funding_pattern"

        # ----------------------------------------------------
        # BENEFICIARIES
        # ----------------------------------------------------

        if (
            "beneficiary" in question_lower
            or "beneficiaries" in question_lower
            or "who can benefit" in question_lower
            or "who benefits" in question_lower
        ):
            return "beneficiaries"

        # ----------------------------------------------------
        # ELIGIBILITY
        # ----------------------------------------------------

        if (
            "eligibility" in question_lower
            or "eligible" in question_lower
            or "qualification" in question_lower
            or "qualify" in question_lower
            or "criteria" in question_lower
            or "who is eligible" in question_lower
            or "who can apply" in question_lower
        ):
            return "eligibility"

        # ----------------------------------------------------
        # BENEFIT TYPE
        # ----------------------------------------------------

        if (
            "type of benefit" in question_lower
            or "benefit type" in question_lower
            or "what benefit" in question_lower
            or "benefits provided" in question_lower
        ):
            return "benefit_type"

        # ----------------------------------------------------
        # INCOME
        # ----------------------------------------------------

        if (
            "income limit" in question_lower
            or "annual income" in question_lower
            or "income" in question_lower
        ):
            return "income"

        # ----------------------------------------------------
        # AGE FROM
        # ----------------------------------------------------

        if (
            "minimum age" in question_lower
            or "age from" in question_lower
            or "starting age" in question_lower
        ):
            return "age_from"

        # ----------------------------------------------------
        # AGE TO
        # ----------------------------------------------------

        if (
            "maximum age" in question_lower
            or "age to" in question_lower
            or "upper age" in question_lower
        ):
            return "age_to"

        # ----------------------------------------------------
        # COMMUNITY
        # ----------------------------------------------------

        if (
            "community" in question_lower
            or "caste" in question_lower
            or "sc" in question_lower
            or "st" in question_lower
            or "obc" in question_lower
        ):
            return "community"

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        if (
            "description" in question_lower
            or "details about" in question_lower
            or "tell me about" in question_lower
            or "what is this scheme" in question_lower
            or "about this scheme" in question_lower
        ):
            return "description"

        return None

    # ========================================================
    # RETRIEVE DOCUMENTS
    # ========================================================

    def retrieve(self, question):

        detected_scheme = self.detect_scheme_name(question)
        detected_field = self.detect_field(question)

        print(
            f"\nDetected scheme: "
            f"{detected_scheme}"
        )

        print(
            f"Detected field: "
            f"{detected_field}"
        )

        # Get every document stored in FAISS
        all_documents = list(
            self.vectorstore.docstore._dict.values()
        )

        filtered_documents = all_documents

        # ----------------------------------------------------
        # FILTER BY SCHEME
        # ----------------------------------------------------

        if detected_scheme:

            filtered_documents = [
                document
                for document in filtered_documents
                if document.metadata.get(
                    "scheme_name",
                    ""
                ).lower()
                == detected_scheme.lower()
            ]

        # ----------------------------------------------------
        # FILTER BY FIELD
        # ----------------------------------------------------

        if detected_field:

            field_documents = [
                document
                for document in filtered_documents
                if document.metadata.get(
                    "field",
                    ""
                ).lower()
                == detected_field.lower()
            ]

            # Only replace results if matching field
            # documents actually exist.
            if field_documents:

                filtered_documents = field_documents

        # ----------------------------------------------------
        # RETURN FILTERED RESULTS
        # ----------------------------------------------------

        if filtered_documents:

            # If only a few highly targeted documents exist,
            # return them directly.
            if len(filtered_documents) <= RETRIEVAL_K:

                return filtered_documents

            # ------------------------------------------------
            # SEMANTIC SEARCH INSIDE FILTERED DOCUMENTS
            # ------------------------------------------------

            temporary_vectorstore = FAISS.from_documents(
                filtered_documents,
                self.embeddings
            )

            return temporary_vectorstore.similarity_search(
                question,
                k=RETRIEVAL_K
            )

        # ----------------------------------------------------
        # FALLBACK TO NORMAL VECTOR SEARCH
        # ----------------------------------------------------

        print(
            "No filtered documents found. "
            "Using normal semantic retrieval."
        )

        return self.vectorstore.similarity_search(
            question,
            k=RETRIEVAL_K
        )

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(self, documents):

        context_parts = []

        for document in documents:

            scheme_name = document.metadata.get(
                "scheme_name",
                ""
            )

            department = document.metadata.get(
                "department",
                ""
            )

            field = document.metadata.get(
                "field_label",
                document.metadata.get("field", "")
            )

            source_url = document.metadata.get(
                "source_url",
                ""
            )

            content = document.page_content

            context = f"""
Scheme Name:
{scheme_name}

Department:
{department}

Field:
{field}

Source URL:
{source_url}

Government Scheme Information:
{content}
"""

            context_parts.append(
                context.strip()
            )

        return "\n\n---\n\n".join(
            context_parts
        )

    # ========================================================
    # BUILD CONVERSATION HISTORY
    # ========================================================

    def build_history(self, messages):

        if not messages:
            return "No previous conversation."

        history_parts = []

        for message in messages:

            role = message.get(
                "role",
                ""
            )

            content = message.get(
                "content",
                ""
            )

            if role == "user":

                history_parts.append(
                    f"User: {content}"
                )

            elif role == "assistant":

                history_parts.append(
                    f"Assistant: {content}"
                )

        return "\n".join(history_parts)

    # ========================================================
    # REWRITE FOLLOW-UP QUESTION
    # ========================================================

    def rewrite_question(
        self,
        question,
        messages=None
    ):

        if not messages:
            return question

        history = self.build_history(
            messages
        )

        rewrite_prompt = f"""
You are helping a Tamil Nadu Government
Schemes chatbot.

Rewrite the user's latest question into a
standalone question using the conversation
history.

Do not answer the question.

Do not add information that is not present
in the conversation.

Conversation History:
{history}

Latest User Question:
{question}

Standalone Question:
"""

        response = self.llm.invoke(
            rewrite_prompt
        )

        rewritten_question = response.content.strip()

        if not rewritten_question:
            return question

        return rewritten_question

    # ========================================================
    # STREAM ANSWER
    # ========================================================

    def stream_answer(
        self,
        question,
        documents,
        chat_history=""
    ):

        # ----------------------------------------------------
        # GUARDRAIL: QUESTION
        # ----------------------------------------------------

        if not is_allowed_question(question):

            yield get_fallback_message()
            return

        # ----------------------------------------------------
        # GUARDRAIL: CONTEXT
        # ----------------------------------------------------

        if not has_relevant_context(documents):

            yield get_fallback_message()
            return

        # ----------------------------------------------------
        # BUILD CONTEXT
        # ----------------------------------------------------

        context = self.build_context(
            documents
        )

        # ----------------------------------------------------
        # BUILD PROMPT
        # ----------------------------------------------------

        messages = RAG_PROMPT.format_messages(
            chat_history=chat_history,
            context=context,
            question=question
        )

        # ----------------------------------------------------
        # STREAM RESPONSE
        # ----------------------------------------------------

        full_answer = ""

        for chunk in self.llm.stream(
            messages
        ):

            text = chunk.content

            if text:

                full_answer += text

                yield text

        # ----------------------------------------------------
        # FINAL ANSWER VALIDATION
        # ----------------------------------------------------

        if not validate_answer(
            full_answer,
            documents
        ):

            yield "\n\n" + get_fallback_message()

    # ========================================================
    # GENERATE COMPLETE ANSWER
    # ========================================================

    def generate_answer(
        self,
        question,
        documents,
        chat_history=""
    ):

        if not is_allowed_question(question):

            return get_fallback_message()

        if not has_relevant_context(documents):

            return get_fallback_message()

        context = self.build_context(
            documents
        )

        messages = RAG_PROMPT.format_messages(
            chat_history=chat_history,
            context=context,
            question=question
        )

        response = self.llm.invoke(
            messages
        )

        answer = response.content.strip()

        if not validate_answer(
            answer,
            documents
        ):

            return get_fallback_message()

        return answer


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    chatbot = TNGovernmentChatbot()

    question = (
        "How can farmers avail the "
        "Training to Farmers scheme?"
    )

    documents = chatbot.retrieve(
        question
    )

    print("\n" + "=" * 70)
    print("QUESTION")
    print("=" * 70)

    print(question)

    print("\n" + "=" * 70)
    print("RETRIEVED DOCUMENTS")
    print("=" * 70)

    for i, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"\n--- RESULT {i} ---"
        )

        print(
            "Scheme:",
            document.metadata.get(
                "scheme_name"
            )
        )

        print(
            "Field:",
            document.metadata.get(
                "field"
            )
        )

        print(
            document.page_content
        )

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)

    answer = chatbot.generate_answer(
        question,
        documents
    )

    print(answer)