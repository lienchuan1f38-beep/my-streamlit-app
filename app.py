import streamlit as st

from utils.analysis import (
    build_period_comparison,
    build_period_summary,
    build_summary_metrics,
    generate_insight_text,
)
from utils.charts import build_metric_chart
from utils.data_loader import EXPECTED_COLUMNS, load_data, load_sample_data


def dataframe_to_csv_bytes(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8-sig")


st.set_page_config(page_title="个人成长数据看板", layout="wide")

st.title("个人成长数据看板系统")
st.caption("用一个本地网页，快速查看学习、阅读、睡眠和运动的阶段表现。")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .tips-box {
        background: linear-gradient(135deg, #f6f8fc 0%, #eef6ff 100%);
        border: 1px solid #d9e7ff;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 18px;
        color: #1f2937;
        line-height: 1.7;
    }
    .tips-box strong {
        color: #111827;
        font-size: 1.05rem;
    }
    .tips-box span {
        color: #334155;
    }
    .section-note {
        color: #4a5568;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="tips-box">
        <strong>使用说明</strong><br>
        <span>你可以上传自己的 CSV 或 Excel 数据文件。</span><br>
        <span>如果暂时没有准备数据，系统会自动展示示例数据，方便你先看效果。</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. 数据导入")
uploaded_file = st.file_uploader(
    "上传 CSV 或 Excel 文件",
    type=["csv", "xlsx"],
)

with st.expander("查看真实数据模板"):
    st.write("你的数据文件需要包含下面 5 列，列名要完全一致：")
    st.code(", ".join(EXPECTED_COLUMNS))
    st.write("示例：")
    st.code(
        "date,study_hours,reading_hours,sleep_hours,exercise_minutes\n"
        "2026-06-01,3,1,7.5,30\n"
        "2026-06-02,2.5,0.5,8.0,20"
    )

df = None

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.success("文件读取成功。")
    except ValueError as error:
        st.error(f"文件读取失败：{error}")
        st.info("当前将继续展示示例数据。你可以修改文件后重新上传。")
        df = load_sample_data()
else:
    df = load_sample_data()
    st.info("当前未上传文件，正在展示示例数据。")

st.subheader("2. 日期筛选")
st.markdown(
    "<div class='section-note'>你可以按时间范围筛选数据，下面的统计和图表会同步更新。</div>",
    unsafe_allow_html=True,
)

min_date = df["date"].min().date()
max_date = df["date"].max().date()
selected_dates = st.date_input(
    "选择开始日期和结束日期",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = min_date
    end_date = max_date

filtered_df = df[
    (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
].copy()

st.caption(f"当前筛选范围：{start_date} 至 {end_date}")

if filtered_df.empty:
    st.warning("当前筛选范围内没有数据，请重新选择日期范围。")
    st.stop()

download_week_df = build_period_summary(filtered_df, "week")
download_month_df = build_period_summary(filtered_df, "month")

with st.popover("下载结果"):
    st.markdown("你可以下载当前筛选后的原始数据，以及按周、按月汇总后的结果。")
    st.download_button(
        "下载筛选后原始数据",
        data=dataframe_to_csv_bytes(filtered_df),
        file_name="filtered_growth_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "下载按周汇总",
        data=dataframe_to_csv_bytes(download_week_df),
        file_name="weekly_growth_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "下载按月汇总",
        data=dataframe_to_csv_bytes(download_month_df),
        file_name="monthly_growth_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.subheader("4. 数据预览")
st.markdown(
    "<div class='section-note'>这里会显示当前读取到的数据内容，便于你检查格式是否正确。</div>",
    unsafe_allow_html=True,
)
st.dataframe(filtered_df, width="stretch")

st.subheader("5. 核心统计")
metrics = build_summary_metrics(filtered_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("总学习时长", f"{metrics['study_total']:.1f} 小时")
col2.metric("总阅读时长", f"{metrics['reading_total']:.1f} 小时")
col3.metric("总睡眠时长", f"{metrics['sleep_total']:.1f} 小时")
col4.metric("总运动时长", f"{metrics['exercise_total']} 分钟")

st.subheader("5.1 日均表现")
avg_col1, avg_col2, avg_col3, avg_col4, avg_col5 = st.columns(5)
avg_col1.metric("记录天数", f"{metrics['record_days']} 天")
avg_col2.metric("日均学习", f"{metrics['study_daily_avg']:.1f} 小时")
avg_col3.metric("日均阅读", f"{metrics['reading_daily_avg']:.1f} 小时")
avg_col4.metric("日均睡眠", f"{metrics['sleep_daily_avg']:.1f} 小时")
avg_col5.metric("日均运动", f"{metrics['exercise_daily_avg']:.1f} 分钟")

st.subheader("6. 趋势图表")
st.markdown(
    "<div class='section-note'>通过折线图查看不同指标随时间的变化趋势。</div>",
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.plotly_chart(
        build_metric_chart(filtered_df, "study_hours", "学习时长趋势", "小时"),
        width="stretch",
    )
    st.plotly_chart(
        build_metric_chart(filtered_df, "sleep_hours", "睡眠时长趋势", "小时"),
        width="stretch",
    )

with chart_col2:
    st.plotly_chart(
        build_metric_chart(filtered_df, "reading_hours", "阅读时长趋势", "小时"),
        width="stretch",
    )
    st.plotly_chart(
        build_metric_chart(filtered_df, "exercise_minutes", "运动时长趋势", "分钟"),
        width="stretch",
    )

st.subheader("7. 周 / 月汇总")
st.markdown(
    "<div class='section-note'>如果你记录了更长时间的数据，这里可以帮你做阶段汇总。</div>",
    unsafe_allow_html=True,
)
summary_type = st.radio("选择汇总方式", ["按周汇总", "按月汇总"], horizontal=True)
period = "week" if summary_type == "按周汇总" else "month"

st.subheader("7.1 最近周期对比")
comparison = build_period_comparison(filtered_df, period)
if comparison:
    st.markdown(
        f"<div class='section-note'>当前展示的是筛选结果中最近一个{comparison['label'].replace('本', '')}相较前一个{comparison['previous_label'].replace('上', '')}的变化。</div>",
        unsafe_allow_html=True,
    )
    compare_col1, compare_col2, compare_col3, compare_col4 = st.columns(4)
    compare_columns = [compare_col1, compare_col2, compare_col3, compare_col4]

    for column, item in zip(compare_columns, comparison["items"]):
        column.metric(
            item["title"],
            item["current_display"],
            item["delta_display"],
        )

summary_df = download_week_df if period == "week" else download_month_df
st.dataframe(summary_df, width="stretch")

st.subheader("8. 自动一句话总结")
st.success(generate_insight_text(filtered_df))
