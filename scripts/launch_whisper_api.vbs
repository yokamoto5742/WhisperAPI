Set ws = CreateObject("Wscript.Shell")

Dim cmd
cmd = "cd /d C:\Users\yokam\PycharmProjects\WhisperAPI && call .venv\Scripts\activate && streamlit run app.py"

' 0 で画面非表示、True で終了まで同期
ws.Run "cmd /c """ & cmd & """", 0, True