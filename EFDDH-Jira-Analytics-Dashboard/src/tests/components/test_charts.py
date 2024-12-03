import pytest

from src.components.charts import create_bar_chart, create_pie_chart


@pytest.fixture
def sample_chart_data():
    return {"labels": ["A", "B", "C"], "values": [1, 2, 3], "title": "Test Chart"}


def test_create_bar_chart(sample_chart_data):
    fig = create_bar_chart(
        x=sample_chart_data["labels"],
        y=sample_chart_data["values"],
        title=sample_chart_data["title"],
    )
    assert fig.layout.title.text == sample_chart_data["title"]
    assert fig.layout.template.layout.font.family == "Arial, sans-serif"
    assert fig.layout.template.layout.paper_bgcolor == "#FFFFFF"


def test_create_pie_chart(sample_chart_data):
    fig = create_pie_chart(
        names=sample_chart_data["labels"],
        values=sample_chart_data["values"],
        title=sample_chart_data["title"],
    )
    assert fig.layout.title.text == sample_chart_data["title"]
    assert fig.layout.template.layout.font.family == "Arial, sans-serif"
    assert fig.layout.template.layout.paper_bgcolor == "#FFFFFF"
