from pathlib import Path
import json

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# ============================================================
# CONFIGURATION
# ============================================================

RAW_FILE = Path("data/raw/schemes.json")
VECTORSTORE_DIR = Path("data/vectorstore")

EMBEDDING_MODEL = "text-embedding-3-small"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# LOAD SCRAPED JSON
# ============================================================

def load_scheme_data():
    """
    Load scheme information from schemes.json.
    """

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {RAW_FILE}\n"
            "Run the scraper first."
        )

    with open(
        RAW_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        schemes = json.load(file)

    print(f"Loaded {len(schemes)} schemes.")

    return schemes


# ============================================================
# CREATE FIELD-LEVEL DOCUMENTS
# ============================================================

def create_documents(schemes):
    """
    Create focused LangChain Documents.

    Instead of embedding the entire scheme page,
    each important field becomes a separate document.

    This improves retrieval precision and reduces
    irrelevant context for RAG evaluation.
    """

    documents = []

    # Fields that are useful for question answering
    fields = [
        ("funding_pattern", "Funding Pattern"),
        ("beneficiaries", "Beneficiaries"),
        ("benefit_type", "Types of Benefits"),
        ("eligibility", "Eligibility Criteria"),
        ("income", "Income"),
        ("age_from", "Age From"),
        ("age_to", "Age To"),
        ("community", "Community"),
        ("how_to_avail", "How To Avail"),
        ("description", "Description"),
        ("scheme_type", "Scheme Type"),
        ("introduced_on", "Introduced On"),
        ("validity", "Validity of Scheme"),
    ]

    for scheme in schemes:

        scheme_name = scheme.get(
            "scheme_name",
            ""
        ).strip()

        department = scheme.get(
            "department",
            ""
        ).strip()

        source_url = scheme.get(
            "source_url",
            ""
        ).strip()

        if not scheme_name:
            continue

        # ----------------------------------------------------
        # Create one document for each useful field
        # ----------------------------------------------------

        for field_name, field_label in fields:

            value = scheme.get(
                field_name,
                ""
            )

            if value is None:
                continue

            value = str(value).strip()

            # Skip empty fields
            if not value:
                continue

            # Skip obviously empty scraped values
            if value.lower() in [
                "na",
                "n/a",
                "none",
                "null"
            ]:
                continue

            page_content = (
              f"Scheme: {scheme_name}\n"
             f"{field_label}: {value}"
     )

            document = Document(

                page_content=page_content,

                metadata={
                    "scheme_name": scheme_name,
                    "department": department,
                    "source_url": source_url,
                    "field": field_name,
                    "field_label": field_label,
                    "page_title": scheme.get(
                        "page_title",
                        ""
                    )
                }
            )

            documents.append(document)

    print(
        f"Created {len(documents)} "
        f"field-level documents."
    )

    return documents


# ============================================================
# CREATE FAISS VECTORSTORE
# ============================================================

def create_vectorstore(documents):
    """
    Create embeddings and store them in FAISS.
    """

    print(
        f"Creating embeddings using: "
        f"{EMBEDDING_MODEL}"
    )

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vectorstore = FAISS.from_documents(
        documents,
        embeddings
    )

    return vectorstore


# ============================================================
# SAVE FAISS DATABASE
# ============================================================

def save_vectorstore(vectorstore):
    """
    Save FAISS database locally.
    """

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    vectorstore.save_local(
        str(VECTORSTORE_DIR)
    )

    print(
        f"FAISS vector database saved to: "
        f"{VECTORSTORE_DIR}"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def build_vectorstore():

    print("=" * 70)

    print(
        "BUILDING TAMIL NADU "
        "SCHEMES VECTOR DATABASE"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Step 1
    # Load JSON
    # --------------------------------------------------------

    schemes = load_scheme_data()

    # --------------------------------------------------------
    # Step 2
    # Create field-level documents
    # --------------------------------------------------------

    documents = create_documents(
        schemes
    )

    # --------------------------------------------------------
    # Step 3
    # Create FAISS
    # --------------------------------------------------------

    vectorstore = create_vectorstore(
        documents
    )

    # --------------------------------------------------------
    # Step 4
    # Save FAISS
    # --------------------------------------------------------

    save_vectorstore(
        vectorstore
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print("=" * 70)

    print(
        "VECTOR DATABASE BUILD COMPLETED"
    )

    print("=" * 70)

    print(
        f"Schemes          : {len(schemes)}"
    )

    print(
        f"Field Documents  : {len(documents)}"
    )

    print(
        f"Vectorstore      : {VECTORSTORE_DIR}"
    )

    print("=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    build_vectorstore()