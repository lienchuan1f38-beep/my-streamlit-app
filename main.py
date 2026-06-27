from pathlib import Path

from streamlit.web import bootstrap


if __name__ == "__main__":
    app_path = str(Path(__file__).resolve().parent / "app.py")
    bootstrap.run(
        app_path,
        "",
        [
            "--server.port=8501",
            "--server.address=127.0.0.1",
            "--browser.serverAddress=127.0.0.1",
        ],
        {},
    )
