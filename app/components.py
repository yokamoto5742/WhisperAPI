import streamlit as st


def load_markdown_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def show_setting_modal() -> None:
    with st.expander("説明"):
        tab1, tab2 = st.tabs(["アプリについて", "プライバシーガイドライン"])

        with tab1:
            st.markdown(load_markdown_file("README.md"))

        with tab2:
            st.markdown(load_markdown_file("docs/privacy_guidelines.md"))
