import pandas as pd


def build_summary_metrics(df: pd.DataFrame) -> dict:
    record_days = int(df["date"].nunique())

    return {
        "study_total": float(df["study_hours"].sum()),
        "reading_total": float(df["reading_hours"].sum()),
        "sleep_total": float(df["sleep_hours"].sum()),
        "exercise_total": int(df["exercise_minutes"].sum()),
        "record_days": record_days,
        "study_daily_avg": float(df["study_hours"].mean()),
        "reading_daily_avg": float(df["reading_hours"].mean()),
        "sleep_daily_avg": float(df["sleep_hours"].mean()),
        "exercise_daily_avg": float(df["exercise_minutes"].mean()),
    }


def _describe_sleep(avg_sleep: float) -> str:
    if avg_sleep >= 8:
        return "睡眠比较充足，整体作息状态较稳定"
    if avg_sleep >= 7:
        return "睡眠时长基本达标，但仍有继续保持规律作息的空间"
    return "睡眠时长偏少，后续可以优先关注休息质量"


def _describe_exercise(avg_exercise: float) -> str:
    if avg_exercise >= 40:
        return "运动投入较好，身体活动保持得比较稳定"
    if avg_exercise >= 20:
        return "运动习惯有一定基础，可以继续提高稳定性"
    return "运动时长偏少，后续可以适当增加锻炼频率"


def _describe_learning(study_avg: float, reading_avg: float) -> str:
    if study_avg >= 3 and reading_avg >= 1:
        return "学习和阅读投入都比较稳定，整体节奏较好"
    if study_avg >= 3:
        return "学习投入较突出，但阅读部分还有提升空间"
    if reading_avg >= 1:
        return "阅读保持得不错，学习时长方面还可以继续加强"
    return "学习和阅读投入整体偏少，后续可以进一步优化时间分配"


def build_period_comparison(df: pd.DataFrame, period: str) -> dict:
    compare_df = df.copy()
    compare_df["date"] = pd.to_datetime(compare_df["date"])

    if period == "week":
        period_values = compare_df["date"].dt.to_period("W-MON")
    else:
        period_values = compare_df["date"].dt.to_period("M")

    compare_df["period_value"] = period_values
    current_period = compare_df["period_value"].max()

    if pd.isna(current_period):
        return {}

    previous_period = current_period - 1
    current_df = compare_df[compare_df["period_value"] == current_period]
    previous_df = compare_df[compare_df["period_value"] == previous_period]

    label = "本周" if period == "week" else "本月"
    previous_label = "上周" if period == "week" else "上月"

    metrics = [
        ("学习时长", "study_hours", "小时"),
        ("阅读时长", "reading_hours", "小时"),
        ("睡眠时长", "sleep_hours", "小时"),
        ("运动时长", "exercise_minutes", "分钟"),
    ]

    result = {
        "label": label,
        "previous_label": previous_label,
        "period_text": str(current_period),
        "items": [],
    }

    for title, column_name, unit in metrics:
        current_value = float(current_df[column_name].sum())
        previous_value = float(previous_df[column_name].sum())
        delta_value = current_value - previous_value

        if unit == "分钟":
            current_display = f"{int(current_value)} {unit}"
            delta_display = f"{delta_value:+.0f} {unit}"
        else:
            current_display = f"{current_value:.1f} {unit}"
            delta_display = f"{delta_value:+.1f} {unit}"

        result["items"].append(
            {
                "title": title,
                "current_display": current_display,
                "delta_display": f"较{previous_label} {delta_display}",
            }
        )

    return result


def build_period_summary(df: pd.DataFrame, period: str) -> pd.DataFrame:
    summary_df = df.copy()
    summary_df["date"] = pd.to_datetime(summary_df["date"])

    if period == "week":
        summary_df["period"] = summary_df["date"].dt.strftime("%Y-第%U周")
    else:
        summary_df["period"] = summary_df["date"].dt.strftime("%Y-%m")

    grouped_df = (
        summary_df.groupby("period", as_index=False)[
            ["study_hours", "reading_hours", "sleep_hours", "exercise_minutes"]
        ]
        .sum()
        .rename(
            columns={
                "period": "时间段",
                "study_hours": "学习时长(小时)",
                "reading_hours": "阅读时长(小时)",
                "sleep_hours": "睡眠时长(小时)",
                "exercise_minutes": "运动时长(分钟)",
            }
        )
    )

    return grouped_df


def generate_insight_text(df: pd.DataFrame) -> str:
    metrics = build_summary_metrics(df)
    learning_text = _describe_learning(
        metrics["study_daily_avg"], metrics["reading_daily_avg"]
    )
    sleep_text = _describe_sleep(metrics["sleep_daily_avg"])
    exercise_text = _describe_exercise(metrics["exercise_daily_avg"])

    return (
        f"在当前筛选范围内，你一共记录了 {metrics['record_days']} 天数据。"
        f"{learning_text}；{sleep_text}；{exercise_text}。"
    )
