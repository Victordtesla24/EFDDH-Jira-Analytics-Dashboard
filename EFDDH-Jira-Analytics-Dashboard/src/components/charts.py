import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config.settings import settings


def create_interactive_charts(filtered_data: pd.DataFrame) -> None:
    """Create interactive charts using Plotly."""
    # Issue Type Distribution
    fig = px.bar(
        filtered_data["Issue Type"].value_counts().reset_index(),
        x="index",
        y="Issue Type",
        title="Issue Type Distribution",
        labels={"index": "Issue Type", "Issue Type": "Count"},
        color="index",
        color_discrete_sequence=settings.charts.color_palette,
    )
    st.plotly_chart(fig, use_container_width=True)


def get_anz_template():
    """Create ANZ-styled template for charts."""
    return go.layout.Template(
        layout=dict(
            font=dict(family=settings.charts.font_family),
            paper_bgcolor=settings.charts.background_color,
            plot_bgcolor=settings.charts.background_color,
            title=dict(font=dict(color=settings.charts.text_color)),
            xaxis=dict(gridcolor="#F5F5F5"),
            yaxis=dict(gridcolor="#F5F5F5"),
        )
    )


def create_bar_chart(x, y, title: str, **kwargs):
    """Create a bar chart with ANZ styling."""
    fig = px.bar(
        x=x,
        y=y,
        title=title,
        color_discrete_sequence=settings.charts.color_palette,
        template=get_anz_template(),
        **kwargs
    )
    return fig


def create_pie_chart(names, values, title: str, **kwargs):
    """Create a pie chart with ANZ styling."""
    fig = px.pie(
        names=names,
        values=values,
        title=title,
        color_discrete_sequence=settings.charts.color_palette,
        template=get_anz_template(),
        **kwargs
    )
    return fig
