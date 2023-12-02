import streamlit as st

from openai import OpenAI

client = OpenAI()


def transcribe_audio(file):
    """ 音声ファイルを文字起こしする """
    try:
        return client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            response_format="text",
        )
    except Exception as e:
        st.error(f"文字起こし中にエラーが発生しました: {e}")


def main():
    st.title("音声ファイルの文字起こしツール")

    if 'uploaded_audio_file' not in st.session_state:
        st.session_state.uploaded_audio_file = None

    # 音声ファイルのアップロード
    uploaded_audio_file = st.file_uploader("音声ファイルをアップロードしてください(20MB以下)", type=["mp3"], key="audio_uploader")

    if st.button('クリア'):
        st.session_state.uploaded_audio_file = None
        st.experimental_rerun()

    if uploaded_audio_file is not None:
        st.session_state.uploaded_audio_file = uploaded_audio_file

        # ファイルサイズのチェック（20MB以上の場合はエラーメッセージを表示）
        if uploaded_audio_file.size > 20480 * 1024:
            st.error("ファイルサイズが大きすぎます。20MB以下のファイルをアップロードしてください。")
        else:
            # 音声を再生
            st.audio(uploaded_audio_file)

            transcription_message = st.empty()
            transcription_message.subheader("文字起こし中...")

            # 文字起こし
            transcript = transcribe_audio(uploaded_audio_file)

            # 文字起こし完了後、メッセージをクリアする
            transcription_message.empty()

            if transcript:
                # 出力結果の表示
                st.subheader("出力結果")
                st.text_area("文字起こし文章", transcript, height=500)

                # テキストファイルとしてダウンロード
                st.download_button(
                    label="ダウンロード",
                    data=transcript.encode("utf-8"),
                    file_name="transcription.txt",
                    mime="text/plain"
                )


if __name__ == "__main__":
    main()
