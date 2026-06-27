from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLE_FILE = DATA_DIR / "sample_data.csv"
EXPECTED_COLUMNS = [
    "date",
    "study_hours",
    "reading_hours",
    "sleep_hours",
    "exercise_minutes",
]


def load_sample_data() -> pd.DataFrame:
    df = pd.read_csv(SAMPLE_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_data(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("仅支持 CSV 或 Excel 文件。")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    missing_columns = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "缺少必要列："
            + "，".join(missing_columns)
            + "。请检查模板列名是否正确。"
        )

    for column in EXPECTED_COLUMNS[1:]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[EXPECTED_COLUMNS].isnull().any().any():
        raise ValueError("数据中存在空值或无法识别的内容，请检查日期和数值格式。")

    return df
