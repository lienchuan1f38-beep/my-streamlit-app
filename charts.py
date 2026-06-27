import pandas as pd
import plotly.express as px


def build_metric_chart(
    df: pd.DataFrame, column_name: str, title: str, y_axis_label: str
):
    chart_df = df.sort_values("date")

    fig = px.line(
        chart_df,
        x="date",
        y=column_name,
        markers=True,
        title=title,
    )
    fig.update_layout(
        xaxis_title="日期",
        yaxis_title=y_axis_label,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
