import pandas as pd
import plotly.express as px
import streamlit as st

from src.config.settings import settings
from src.utils.formatting import get_anz_template


def create_interactive_charts(filtered_data: pd.DataFrame) -> None:
    """Create interactive charts using Plotly."""
    if filtered_data.empty:
        st.warning("No data available for visualization")
        return

    # Issue Type Distribution
    value_counts = filtered_data["Issue Type"].value_counts()
    chart_data = pd.DataFrame(
        {"Issue Type": value_counts.index, "Count": value_counts.values}
    )

    fig = px.bar(
        chart_data,
        x="Issue Type",
        y="Count",
        title="Issue Type Distribution",
        color="Issue Type",
        color_discrete_sequence=settings.charts.color_palette,
    )
    st.plotly_chart(fig, use_container_width=True)


def create_bar_chart(x, y, title: str, **kwargs):
    """Create a bar chart with ANZ styling."""
    df = pd.DataFrame({"x": x, "y": y})

    # Handle color and color_discrete_sequence
    color = kwargs.pop("color", None)
    color_sequence = kwargs.pop(
        "color_discrete_sequence", settings.charts.color_palette
    )
    if color:
        color_sequence = [color]

    fig = px.bar(
        df,
        x="x",
        y="y",
        title=title,
        color_discrete_sequence=color_sequence,
        template=get_anz_template(),
        **kwargs
    )
    return fig


def create_pie_chart(names, values, title: str, **kwargs):
    """Create a pie chart with ANZ styling."""
    df = pd.DataFrame({"names": names, "values": values})
    color_sequence = kwargs.pop("colors", settings.charts.color_palette)

    fig = px.pie(
        df,
        names="names",
        values="values",
        title=title,
        color_discrete_sequence=color_sequence,
        template=get_anz_template(),
        **kwargs
    )
    return fig