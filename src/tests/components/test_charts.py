import pandas as pd
from plotly.graph_objects import Figure

from src.components.charts import (create_bar_chart, create_interactive_charts,
                                   create_pie_chart)


def test_create_interactive_charts(mock_streamlit):
    """Test interactive charts creation with sample data."""
    # Create sample data
    data = pd.DataFrame({"Issue Type": ["Bug", "Story", "Bug", "Epic", "Story"]})

    create_interactive_charts(data)
    assert mock_streamlit["plotly_chart"].called
    # Verify plotly_chart was called with a Figure object
    call_args = mock_streamlit["plotly_chart"].call_args
    assert isinstance(call_args[0][0], Figure)
    # Verify container width parameter
    assert call_args[1]["use_container_width"] is True


def test_create_bar_chart():
    """Test bar chart creation with basic data."""
    x = ["A", "B", "C"]
    y = [1, 2, 3]
    title = "Test Bar Chart"

    fig = create_bar_chart(x, y, title)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_bar_chart_with_color():
    """Test bar chart creation with custom color."""
    x = ["A", "B"]
    y = [1, 2]
    title = "Colored Bar Chart"
    color = "#FF0000"

    fig = create_bar_chart(x, y, title, color=color)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_bar_chart_with_custom_sequence():
    """Test bar chart creation with custom color sequence."""
    x = ["A", "B"]
    y = [1, 2]
    title = "Custom Sequence Chart"
    color_sequence = ["#FF0000", "#00FF00"]

    fig = create_bar_chart(x, y, title, color_discrete_sequence=color_sequence)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_pie_chart():
    """Test pie chart creation with basic data."""
    names = ["A", "B", "C"]
    values = [30, 20, 10]
    title = "Test Pie Chart"

    fig = create_pie_chart(names, values, title)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_pie_chart_with_custom_colors():
    """Test pie chart creation with custom colors."""
    names = ["A", "B"]
    values = [60, 40]
    title = "Colored Pie Chart"
    colors = ["#FF0000", "#00FF00"]

    fig = create_pie_chart(names, values, title, colors=colors)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_pie_chart_with_additional_params():
    """Test pie chart creation with additional parameters."""
    names = ["A", "B"]
    values = [70, 30]
    title = "Detailed Pie Chart"

    fig = create_pie_chart(
        names,
        values,
        title,
        hole=0.3,  # Creates a donut chart
        labels={"names": "Category", "values": "Amount"},
    )
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_interactive_charts_empty_data(mock_streamlit):
    """Test interactive charts with empty dataframe."""
    empty_data = pd.DataFrame(columns=["Issue Type"])
    create_interactive_charts(empty_data)
    assert mock_streamlit["warning"].called
    warning_msg = "No data available for visualization"
    assert mock_streamlit["warning"].call_args[0][0] == warning_msg


def test_create_bar_chart_single_item():
    """Test bar chart with single data point."""
    x = ["A"]
    y = [1]
    title = "Single Item Chart"

    fig = create_bar_chart(x, y, title)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title


def test_create_pie_chart_single_item():
    """Test pie chart with single data point."""
    names = ["A"]
    values = [100]
    title = "Single Item Pie"

    fig = create_pie_chart(names, values, title)
    assert isinstance(fig, Figure)
    assert fig.layout.title.text == title
