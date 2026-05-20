import streamlit as st

from app.components import show_setting_modal
from service.transcription_service import transcribe_uploaded_file
from utils.env_loader import load_environment_variables
from utils.log_rotation import setup_logging

load_environment_variables()
setup_logging()


def main() -> None:
    st.title("音声ファイルの文字起こしアプリ")

    if "uploaded_audio_file" not in st.session_state:
        st.session_state.uploaded_audio_file = None

    uploaded_audio_file = st.file_uploader(
        "音声ファイルをアップロードしてください(25MB未満)",
        type=["mp3", "mp4", "webm", "wav", "mpeg", "mpga", "m4a"],
        key="audio_uploader",
    )

    if uploaded_audio_file is not None:
        st.session_state.uploaded_audio_file = uploaded_audio_file

        if uploaded_audio_file.size > 25 * 1024 * 1024:
            st.error(
                "ファイルサイズが大きすぎます。25MB未満のファイルをアップロードしてください。"
            )
        else:
            st.audio(uploaded_audio_file)

            transcription_message = st.empty()
            transcription_message.subheader("文字起こし中...")

            transcript = transcribe_uploaded_file(uploaded_audio_file)

            transcription_message.empty()

            if transcript:
                st.subheader("出力結果")
                st.text_area("文字起こし文章", transcript, height=500)
                st.download_button(
                    label="ダウンロード",
                    data=transcript.encode("utf-8"),
                    file_name="transcription.txt",
                    mime="text/plain",
                )

    if st.button("アプリの説明"):
        show_setting_modal()


if __name__ == "__main__":
    main()
