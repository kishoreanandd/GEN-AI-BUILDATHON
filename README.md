# 🇮🇳 Tamil Nadu Government Schemes RAG Chatbot

An AI-powered **Retrieval-Augmented Generation (RAG) chatbot** that helps users find and understand Tamil Nadu Government schemes using information collected from the official Tamil Nadu Government schemes portal.

The system combines **Playwright web scraping, LangChain, OpenAI embeddings, FAISS vector search, GPT, LangSmith, DeepEval, Guardrails, Conversation Memory, and Streamlit** to provide grounded and source-aware answers.

---

## 🚀 Project Overview

Finding the right government scheme can be difficult because scheme information is spread across multiple department pages and contains different fields such as:

* Scheme name
* Department
* Beneficiaries
* Eligibility
* Funding pattern
* Benefits
* Application procedure
* Age requirements
* Income requirements
* Community information
* Scheme description

This project converts government scheme information into a searchable knowledge base and uses RAG to answer user questions based on the retrieved government data.

### Example

**User:**

> What is the funding pattern for Training to Farmers?

**Chatbot:**

> Funding pattern: Rs. 300 per farmer for 2 days.

The answer is generated using the retrieved government scheme information rather than relying only on the LLM's general knowledge.

---

# 🎯 Objectives

1. Collect Tamil Nadu Government scheme information automatically.
2. Convert unstructured web content into structured scheme data.
3. Create searchable vector representations using OpenAI embeddings.
4. Retrieve the most relevant scheme information for a question.
5. Generate answers using a RAG architecture.
6. Reduce hallucination by restricting answers to retrieved government data.
7. Support conversational follow-up questions.
8. Evaluate retrieval and answer quality using DeepEval.
9. Monitor LLM interactions using LangSmith.
10. Provide a simple user interface using Streamlit.

---

# 🏗️ System Architecture

```text
Tamil Nadu Government Website
            │
            ▼
     Playwright Scraper
            │
            ▼
     Structured JSON Data
       schemes.json
            │
            ▼
   Field-Level Documents
            │
            ▼
   OpenAI Embeddings
   text-embedding-3-small
            │
            ▼
       FAISS Vector DB
            │
            ▼
       User Question
            │
            ▼
   Scheme + Field Detection
            │
            ▼
      Relevant Retrieval
            │
            ▼
        RAG Context
            │
            ▼
      GPT-5-mini
            │
            ▼
      Guardrails / Validation
            │
            ▼
       Final Answer
            │
            ▼
         Streamlit UI
```

---

# 🧠 RAG Pipeline

The chatbot follows these major steps:

### 1. Data Collection

Playwright navigates the Tamil Nadu Government scheme portal and collects scheme detail pages.

### 2. Data Cleaning

The scraper extracts important fields from each scheme instead of storing the entire webpage as raw text.

### 3. Structured Storage

The extracted information is stored in:

```text
data/raw/schemes.json
```

### 4. Field-Level Document Creation

Each important scheme field is converted into a separate document.

For example:

```text
Scheme Name: Training to Farmers

Field: Funding Pattern

Funding Pattern:
Rs.300 per farmer for 2 days.
```

This improves retrieval precision.

### 5. Embeddings

OpenAI's:

```text
text-embedding-3-small
```

is used to convert scheme information into numerical vector representations.

### 6. Vector Database

FAISS stores the embeddings and enables similarity search.

### 7. Scheme-Aware Retrieval

The chatbot first attempts to identify the specific scheme mentioned by the user.

Example:

```text
Training to Farmers
```

### 8. Field-Aware Retrieval

The chatbot also identifies what information the user is asking for.

Examples:

```text
funding
beneficiaries
eligibility
how to apply
income
age
community
benefits
```

This prevents unrelated fields from being unnecessarily retrieved.

### 9. RAG Generation

The retrieved government information is passed to the LLM together with strict instructions to answer only from the provided context.

### 10. Guardrails

The chatbot blocks prompt-injection style requests and prevents answers when sufficient context is unavailable.

---

# 🛡️ Hallucination Prevention

Government scheme information is sensitive because incorrect eligibility, funding, or application information can mislead users.

The chatbot therefore follows these principles:

* Do not invent information.
* Do not guess eligibility requirements.
* Do not guess funding amounts.
* Do not guess application procedures.
* Do not use outside knowledge for scheme answers.
* Use retrieved government scheme information as the authority.
* Provide a fallback response when information is unavailable.
* Do not claim that a scheme is currently active unless the source supports that claim.

Fallback response:

```text
This information is not available in the current Tamil Nadu Government scheme data.
```

---

# 🔐 Prompt Injection Protection

The chatbot checks user questions for common prompt injection attempts such as:

```text
ignore previous instructions
ignore all previous instructions
ignore your instructions
system prompt
reveal your prompt
show your prompt
developer message
jailbreak
```

These requests are rejected instead of being passed through the normal RAG pipeline.

---

# 💬 Conversation Memory

The chatbot supports conversational interactions.

For example:

```text
User:
Tell me about Training to Farmers.

Assistant:
...

User:
Who are the beneficiaries?

Assistant:
The beneficiaries are Farmers.
```

Conversation history is used to understand follow-up questions while the actual scheme information is still retrieved from the government knowledge base.

---

# 📊 Evaluation

The project uses **DeepEval** to evaluate the RAG pipeline.

The current evaluation checks:

### Answer Relevancy

Measures whether the generated answer directly addresses the user's question.

### Faithfulness

Measures whether the answer is supported by the retrieved context.

### Contextual Relevancy

Measures whether the retrieved documents are relevant to the user's question.

---

## Current Evaluation Results

The current test set contains three questions:

1. Who are the beneficiaries of Training to Farmers?
2. What is the funding pattern for Training to Farmers?
3. How can farmers avail the Training to Farmers scheme?

Current results:

| Metric               | Average Score | Pass Rate |
| -------------------- | ------------: | --------: |
| Answer Relevancy     |          1.00 |      100% |
| Faithfulness         |          1.00 |      100% |
| Contextual Relevancy |          0.89 |    66.67% |

The evaluation demonstrates that the generated answers are highly relevant and faithful to the retrieved context.

The remaining contextual-relevancy issue is being addressed through improvements to field extraction and retrieval precision.

---

# 📈 Observed Improvement

The project initially used broader scheme-level chunks.

This resulted in unrelated information being retrieved together.

For example, a funding question could retrieve:

```text
Funding Pattern
Beneficiaries
Eligibility
Description
How To Avail
```

The system was then improved using **field-level documents**.

This significantly improved retrieval quality.

The next improvement was **scheme-aware retrieval**, followed by **field-aware retrieval**.

This architecture helps prevent similarly named schemes from contaminating the retrieved context.

---

# 🔍 Example Queries

The chatbot can answer questions such as:

```text
Who are the beneficiaries of Training to Farmers?
```

```text
What is the funding pattern for Training to Farmers?
```

```text
How can farmers avail the Training to Farmers scheme?
```

```text
What are the eligibility criteria?
```

```text
What benefits are provided?
```

```text
What is the income limit?
```

```text
What is the minimum age?
```

```text
How can I apply for this scheme?
```

---

# 🛠️ Technology Stack

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| Python        | Core development                |
| Playwright    | Web scraping                    |
| LangChain     | RAG orchestration               |
| OpenAI        | Embeddings and LLM              |
| FAISS         | Vector database                 |
| Streamlit     | User interface                  |
| LangSmith     | LLM tracing and monitoring      |
| DeepEval      | RAG evaluation                  |
| python-dotenv | Environment variable management |
| Pytest        | Testing                         |

---

# 📁 Project Structure

```text
tn-schemes-rag-chatbot/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── scraper/
│   ├── __init__.py
│   └── scrape_schemes.py
│
├── ingestion/
│   ├── __init__.py
│   └── build_vectorstore.py
│
├── rag/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── guardrails.py
│   └── prompts.py
│
├── evaluation/
│   ├── __init__.py
│   └── evaluate_rag.py
│
├── data/
│   ├── raw/
│   │   └── schemes.json
│   │
│   └── vectorstore/
│
└── tests/
    └── test_rag.py
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd tn-schemes-rag-chatbot
```

---

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 4. Install Playwright Browser

```powershell
python -m playwright install
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_openai_api_key

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=tn-schemes-rag-chatbot
```

### Important

Never commit `.env` to GitHub.

The project includes `.gitignore` to protect API keys.

---

# 🕷️ Run the Scraper

Run:

```powershell
python scraper\scrape_schemes.py
```

The scraper collects scheme information and creates:

```text
data/raw/schemes.json
```

---

# 🧮 Build the Vector Database

After scraping:

```powershell
python ingestion\build_vectorstore.py
```

This creates the FAISS vector database:

```text
data/vectorstore/
```

---

# 🔎 Test Retrieval

Run:

```powershell
python inspect_retrieval.py
```

This allows retrieval quality to be inspected before running the full application.

---

# 📊 Run Evaluation

Run:

```powershell
python evaluation\evaluate_rag.py
```

DeepEval evaluates:

* Answer Relevancy
* Faithfulness
* Contextual Relevancy

---

# 🖥️ Run the Streamlit Application

Start the chatbot:

```powershell
streamlit run app.py
```

Streamlit will open the chatbot interface in the browser.

---

# 🔭 LangSmith Monitoring

LangSmith is integrated to monitor the RAG pipeline.

It can be used to inspect:

* User questions
* Question rewriting
* Retrieval
* Prompt execution
* LLM responses
* Latency
* Token usage
* Errors
* Traces

This makes debugging and improving the RAG system easier.

---

# 💡 Key Design Decisions

## Why FAISS?

FAISS provides fast local vector similarity search and is suitable for a lightweight RAG prototype.

## Why field-level documents?

Government schemes contain many different information fields. Separating these fields improves retrieval precision.

## Why scheme-aware retrieval?

Several schemes can have similar names or target similar beneficiaries.

Scheme-aware retrieval reduces cross-scheme information mixing.

## Why field-aware retrieval?

A user asking about funding should primarily retrieve funding information rather than unrelated eligibility or description information.

## Why Guardrails?

A government chatbot should avoid confidently generating information that is not present in its verified knowledge base.

## Why DeepEval?

RAG quality cannot be judged only by whether the application runs. Retrieval and generation need measurable evaluation.

---

# ⚠️ Current Limitations

This is a buildathon prototype and has some limitations:

1. The knowledge base depends on the information available on the source website.
2. Government website structure may change and require scraper updates.
3. Scheme information may change after the dataset is collected.
4. Current field detection uses rule-based question classification.
5. FAISS is currently used as a local vector database.
6. The evaluation dataset is currently small.
7. More schemes and question types should be added to the evaluation dataset.
8. Production deployment would require stronger authentication, monitoring, scaling, and data-refresh mechanisms.

---

# 🔮 Future Improvements

### 1. Automated Data Refresh

Schedule the scraper to periodically update the government scheme database.

### 2. Better Retrieval

Add:

* Metadata filtering
* MMR retrieval
* Reranking
* Hybrid keyword + semantic search

### 3. Better Query Understanding

Replace simple keyword field detection with an LLM-based structured query classifier.

### 4. Larger Evaluation Dataset

Create a comprehensive benchmark containing:

* Beneficiary questions
* Eligibility questions
* Funding questions
* Application questions
* Multi-turn questions
* Out-of-scope questions
* Adversarial questions

### 5. Multilingual Support

Support:

* English
* Tamil
* Tanglish

### 6. Source Citations

Provide clickable official government source links with every answer where appropriate.

### 7. Production Deployment

Deploy the chatbot using a scalable cloud architecture.

### 8. Advanced Guardrails

Add stronger:

* Input validation
* Output validation
* PII protection
* Prompt injection detection
* Groundedness verification

### 9. Automated Evaluation

Run DeepEval automatically whenever the RAG pipeline changes.

---

# 🌟 Why This Project Matters

Government schemes can provide valuable financial and social support, but citizens may struggle to discover the schemes relevant to them or understand complicated scheme information.

This project demonstrates how Generative AI and RAG can create a more accessible interface for government information while maintaining a strong focus on **grounded answers, retrieval accuracy, evaluation, and hallucination prevention**.

The goal is not to replace official government sources.

The goal is to make government scheme information **easier to search, understand, and access**.

---

# 🏆 Buildathon Highlights

### Data Engineering

* Automated government website scraping
* Structured scheme extraction
* Field-level data organization

### Generative AI

* OpenAI embeddings
* GPT-powered answer generation
* LangChain RAG pipeline

### Retrieval

* FAISS vector database
* Scheme-aware retrieval
* Field-aware retrieval

### Responsible AI

* Prompt injection protection
* Context-based answering
* Fallback responses
* Hallucination reduction

### Evaluation

* DeepEval
* Answer Relevancy
* Faithfulness
* Contextual Relevancy

### Observability

* LangSmith tracing
* RAG pipeline monitoring

### User Experience

* Streamlit chatbot
* Conversational memory
* Streaming responses

---

# 📌 Important Disclaimer

This chatbot is an AI-based interface for exploring Tamil Nadu Government scheme information.

Users should verify important information such as eligibility, funding, application procedures, deadlines, and current scheme availability with the **official Tamil Nadu Government source or concerned department** before making decisions or submitting applications.

---

# 👨‍💻 Project

**Tamil Nadu Government Schemes RAG Chatbot**

Built using:

```text
Python
Playwright
LangChain
OpenAI
FAISS
Streamlit
LangSmith
DeepEval
```

---

## 📄 License

This project is intended for educational and buildathon purposes.