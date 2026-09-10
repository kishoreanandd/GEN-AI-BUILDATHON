import streamlit as st

from rag.chatbot import TNGovernmentChatbot

from rag.guardrails import (
    is_allowed_question,
    has_relevant_context,
    get_fallback_message,
    validate_answer
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Tamil Nadu Schemes Assistant",
    page_icon="🏛️",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🏛️ Tamil Nadu Government Schemes Assistant"
)

st.caption(
    "Ask questions about Tamil Nadu Government schemes."
)


# ============================================================
# LOAD CHATBOT
# ============================================================

@st.cache_resource
def load_chatbot():

    return TNGovernmentChatbot()


chatbot = load_chatbot()


# ============================================================
# CHAT MEMORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# USER QUESTION
# ============================================================

question = st.chat_input(
    "Ask about a Tamil Nadu Government scheme..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # Save user question
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # --------------------------------------------------------
    # Display user question
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # ========================================================
    # GUARDRAIL 1
    # CHECK QUESTION
    # ========================================================

    if not is_allowed_question(question):

        answer = (
            "I can only help with Tamil Nadu Government "
            "scheme-related questions."
        )

        with st.chat_message("assistant"):

            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.stop()


    # ========================================================
    # REWRITE QUESTION
    # ========================================================

    standalone_question = chatbot.rewrite_question(
        question,
        st.session_state.messages[:-1]
    )


    # ========================================================
    # RETRIEVE DOCUMENTS
    # ========================================================

    documents = chatbot.retrieve(
        standalone_question
    )


    # ========================================================
    # GUARDRAIL 2
    # CHECK RETRIEVAL
    # ========================================================

    if not has_relevant_context(documents):

        answer = get_fallback_message()

        with st.chat_message("assistant"):

            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.stop()


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    with st.chat_message("assistant"):

        response = st.write_stream(
            chatbot.stream_answer(
                standalone_question,
                documents,
                st.session_state.messages
            )
        )


        # ====================================================
        # GUARDRAIL 3
        # VALIDATE ANSWER
        # ====================================================

        if not validate_answer(
            response,
            documents
        ):

            st.warning(
                get_fallback_message()
            )

            response = get_fallback_message()


        # ====================================================
        # SOURCES
        # ====================================================

        st.markdown(
            "### 📚 Sources"
        )

        displayed_sources = set()

        for document in documents:

            scheme_name = document.metadata.get(
                "scheme_name",
                "Unknown scheme"
            )

            department = document.metadata.get(
                "department",
                "Unknown department"
            )

            source_url = document.metadata.get(
                "source_url",
                ""
            )

            source_key = (
                scheme_name,
                source_url
            )

            if source_key in displayed_sources:

                continue

            displayed_sources.add(
                source_key
            )

            st.markdown(
                f"**Scheme:** {scheme_name}"
            )

            st.markdown(
                f"**Department:** {department}"
            )

            if source_url:

                st.markdown(
                    f"[View Government Source]({source_url})"
                )

            st.divider()


    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
