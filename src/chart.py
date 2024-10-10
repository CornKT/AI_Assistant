import plotly.express as px
import solara
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Sử dụng dữ liệu mẫu iris cho biểu đồ cột
df = px.data.iris()
np.random.seed(0)
time = pd.date_range(start='2023-01-01', periods=10, freq='D')
attribute1 = np.random.randint(-100, 500, size=10)
attribute2 = np.random.randint(200, 600, size=10)
attribute3 = np.random.randint(-300, 700, size=10)

# Tạo DataFrame từ dữ liệu
df_sample = pd.DataFrame({
    'Time': time,
    'Attribute1': attribute1,
    'Attribute2': attribute2,
    'Attribute3': attribute3
})

def create_plotly_figure(df, title="Data Visualization"):
    fig = go.Figure()

    df = df.sort_values("Time")
    df_dict = df.to_dict(orient='list')
    print(">>df_dict:",df_dict)
    min_y = np.inf
    max_y = -np.inf
    for column in df_dict.keys():
        if column != "Time":
            min_y = min(min_y, min(df_dict[column]))
            max_y = max(max_y, max(df_dict[column]))

    buffer = (max_y - min_y) * 0.05
    adjusted_min_y = min_y - buffer
    adjusted_max_y = max_y + buffer

    for column in df_dict.keys():
        if column != "Time":
            fig.add_trace(
                go.Bar(
                    x=df_dict["Time"],
                    y=df_dict[column],
                    name=column,
                    hoverinfo="y",
                    hovertemplate="%{y:,.0f}<extra></extra>",
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Value",
        legend_title="Properties",
        hovermode="closest",
        barmode="group",
        bargap=0.3,
        bargroupgap=0.2,
        height=600,
        yaxis=dict(
            range=[adjusted_min_y, adjusted_max_y],
            tickformat=",",
        ),
    )

    fig.add_annotation(
        text="Note: Y-axis does not start at zero",
        xref="paper",
        yref="paper",
        x=0,
        y=1.05,
        showarrow=False,
        font=dict(size=10),
        align="left",
    )

    return fig
@solara.component
def Page():
    with solara.VBox() as main:
        fig = create_plotly_figure(df_sample, title="Sample Data Visualization")
        fig.show()
    return main