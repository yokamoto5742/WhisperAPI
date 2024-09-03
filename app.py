import streamlit as st
import tempfile
import os
from groq import Groq

# Groqクライアントの設定
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def transcribe_audio(file):
    """ 音声ファイルを文字起こしする """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(file.getvalue())
            temp_audio_path = temp_audio.name

        with open(temp_audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(temp_audio_path), audio_file),
                model="whisper-large-v3",
                response_format="text",
                language="ja"
            )

        os.unlink(temp_audio_path)
        return transcription
    except Exception as e:
        st.error(f"文字起こし中にエラーが発生しました: {e}")
        return None


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

        # ファイルサイズのチェック（25MB以上の場合はエラーメッセージを表示）
        if uploaded_audio_file.size > 25 * 1024 * 1024:
            st.error("ファイルサイズが大きすぎます。25MB以下のファイルをアップロードしてください。")
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
