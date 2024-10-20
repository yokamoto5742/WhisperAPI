import streamlit as st
import tempfile
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def load_markdown_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def transcribe_audio(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(file.getvalue())
            temp_audio_path = temp_audio.name

        with open(temp_audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(temp_audio_path), audio_file),
                model="whisper-large-v3-turbo",
                response_format="text",
                language="ja"
            )

        os.unlink(temp_audio_path)
        return transcription
    except Exception as e:
        st.error(f"文字起こし中にエラーが発生しました: {e}")
        return None


def show_setting_modal():
    with st.expander("説明"):
        tab1, tab2 = st.tabs(["アプリについて", "プライバシーガイドライン"])

        with tab1:
            readme_content = load_markdown_file("README.md")
            st.markdown(readme_content)

        with tab2:
            privacy_content = load_markdown_file("privacy_guidelines.md")
            st.markdown(privacy_content)


def main():
    st.title("音声ファイルの文字起こしアプリ")

    # 音声ファイルのアップロード状態を初期化
    if 'uploaded_audio_file' not in st.session_state:
        st.session_state.uploaded_audio_file = None

    # 音声ファイルのアップロード
    uploaded_audio_file = st.file_uploader(
        "音声ファイルをアップロードしてください(25MB以下)",
        type=["mp3", "mp4", "webm", "wav", "mpeg", "mpga", "m4a"],
        key="audio_uploader"
    )

    if uploaded_audio_file is not None:
        st.session_state.uploaded_audio_file = uploaded_audio_file

        if uploaded_audio_file.size > 25 * 1024 * 1024:
            st.error("ファイルサイズが大きすぎます。25MB以下のファイルをアップロードしてください。")
        else:
            st.audio(uploaded_audio_file)

            transcription_message = st.empty()
            transcription_message.subheader("文字起こし中...")

            transcript = transcribe_audio(uploaded_audio_file)

            transcription_message.empty()

            if transcript:
                st.subheader("出力結果")
                st.text_area("文字起こし文章", transcript, height=500)

                st.download_button(
                    label="ダウンロード",
                    data=transcript.encode("utf-8"),
                    file_name="transcription.txt",
                    mime="text/plain"
                )

    if st.button("アプリの説明"):
        show_setting_modal()


if __name__ == "__main__":
    main()