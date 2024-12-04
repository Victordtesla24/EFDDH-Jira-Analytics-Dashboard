"""Agile Process UI component."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_poker_card(value: str, description: str) -> str:
    """Create a visual poker card using HTML/CSS."""
    return f"""
        <div style="
            display: inline-block;
            width: 100px;
            height: 140px;
            margin: 10px;
            padding: 10px;
            border: 2px solid #007DBA;
            border-radius: 10px;
            text-align: center;
            background: white;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            cursor: pointer;">
            <div style="
                font-size: 24px;
                font-weight: bold;
                color: #007DBA;
                margin-bottom: 10px;">
                {value}
            </div>
            <div style="
                font-size: 12px;
                color: #666;">
                {description}
            </div>
        </div>
    """


def create_process_step(number: int, title: str, duration: str, details: list) -> str:
    """Create a visual process step using HTML/CSS."""
    details_html = "".join([f"<li>{detail}</li>" for detail in details])
    return f"""
        <div style="
            margin: 20px 0;
            padding: 20px;
            border-left: 4px solid #007DBA;
            background: #f8f9fa;
            border-radius: 0 10px 10px 0;
            position: relative;">
            <div style="
                position: absolute;
                left: -15px;
                top: 50%;
                transform: translateY(-50%);
                background: #007DBA;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                text-align: center;
                line-height: 30px;
                font-weight: bold;">
                {number}
            </div>
            <h3 style="margin-left: 20px; color: #007DBA;">{title}</h3>
            <div style="
                margin-left: 20px;
                color: #666;
                font-size: 14px;
                margin-bottom: 10px;">
                {duration}
            </div>
            <ul style="margin-left: 20px;">
                {details_html}
            </ul>
        </div>
    """


def show_agile_process(data: pd.DataFrame = None) -> None:
    """Display the Agile process documentation with enhanced Planning Poker guide."""
    st.markdown('<div class="doc-section">', unsafe_allow_html=True)

    # Create tabs for different sections
    process_tabs = st.tabs(["Planning Poker Guide", "Sprint Cycle", "Best Practices"])

    with process_tabs[0]:
        st.title("Planning Poker: Interactive Team Estimation Guide")

        # Interactive Timer
        st.sidebar.markdown("### Session Timer")
        minutes = st.sidebar.number_input("Minutes", min_value=1, max_value=15, value=5)
        seconds = minutes * 60
        if st.sidebar.button("Start Timer"):
            st.sidebar.markdown(f"Time remaining: {minutes}:00")

        # Planning Poker Cards Display
        st.subheader("Planning Poker Cards")
        cards_html = ""
        for value, desc in [
            ("1", "Very Simple"),
            ("2", "Simple"),
            ("3", "Moderate"),
            ("5", "Complex"),
            ("8", "Very Complex"),
            ("13", "Extremely Complex"),
            ("?", "No Idea"),
            ("∞", "Too Big"),
            ("☕", "Break"),
        ]:
            cards_html += create_poker_card(value, desc)

        st.markdown(
            f"""
            <div style="
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                margin: 20px 0;">
                {cards_html}
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Process Flow Diagram
        st.subheader("Estimation Process Flow")
        process_steps = [
            (
                1,
                "Story Presentation",
                "5 mins",
                [
                    "Product Owner presents the story",
                    "Explains acceptance criteria",
                    "Clarifies requirements",
                    "Answers initial questions",
                ],
            ),
            (
                2,
                "Team Discussion",
                "5-10 mins",
                [
                    "Discuss implementation approach",
                    "Identify technical considerations",
                    "Share concerns and risks",
                    "Ask clarifying questions",
                ],
            ),
            (
                3,
                "Silent Estimation",
                "1 min",
                [
                    "Each team member selects a card",
                    "No discussion during selection",
                    "Consider all factors independently",
                    "Keep cards face down",
                ],
            ),
            (
                4,
                "Card Reveal",
                "1 min",
                [
                    "All cards revealed simultaneously",
                    "Scrum Master records estimates",
                    "Identify highest and lowest",
                    "Note any patterns",
                ],
            ),
            (
                5,
                "Discussion Round",
                "5-10 mins",
                [
                    "Highest/lowest explain reasoning",
                    "Share different perspectives",
                    "Discuss assumptions",
                    "Identify missing information",
                ],
            ),
            (
                6,
                "Re-estimation",
                "if needed",
                [
                    "Team re-estimates after discussion",
                    "Focus on reaching consensus",
                    "Document final estimate",
                    "Record key assumptions",
                ],
            ),
        ]

        process_html = "".join(
            [
                create_process_step(num, title, duration, details)
                for num, title, duration, details in process_steps
            ]
        )
        st.markdown(process_html, unsafe_allow_html=True)

        # Real Example with Interactive Elements
        st.subheader("Interactive Example")
        if data is not None and not data.empty:
            example_story = (
                data[data["Issue key"] == "EFDDH-902"].iloc[0]
                if len(data[data["Issue key"] == "EFDDH-902"]) > 0
                else None
            )

            if example_story is not None:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(
                        f"""
                    ### Story Details
                    **Key**: {example_story['Issue key']}
                    **Summary**: {example_story['Summary']}
                    **Final Points**: {example_story['Story Points']}
                    """
                    )

                    # Interactive Estimation Simulation
                    st.markdown("### Team Estimation Simulation")
                    selected_points = st.select_slider(
                        "Select your estimate", options=[1, 2, 3, 5, 8, 13], value=5
                    )

                    # Show distribution of estimates
                    estimates = [3, 5, 5, 8, selected_points]
                    fig = px.histogram(
                        x=estimates,
                        nbins=len(set(estimates)),
                        title="Team Estimates Distribution",
                    )
                    fig.update_layout(
                        showlegend=False,
                        xaxis_title="Story Points",
                        yaxis_title="Count",
                    )
                    st.plotly_chart(fig)

                with col2:
                    st.markdown("### Estimation Factors")
                    factors = {
                        "Technical Complexity": 0.8,
                        "Dependencies": 0.6,
                        "Testing Effort": 0.7,
                        "Documentation": 0.4,
                    }

                    # Radar chart for complexity factors
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatterpolar(
                            r=list(factors.values()),
                            theta=list(factors.keys()),
                            fill="toself",
                            name="Complexity Factors",
                        )
                    )
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                    )
                    st.plotly_chart(fig)
            else:
                st.warning("Example story (EFDDH-902) not found in the data")
        else:
            st.info("Upload JIRA data to see an interactive example")

        # Facilitation Tips with Visual Elements
        st.subheader("Facilitation Guide")

        tips_data = {
            "Before Session": [
                "Prepare stories",
                "Review criteria",
                "Set up tools",
                "Check timing",
            ],
            "During Session": [
                "Keep focus",
                "Encourage participation",
                "Manage time",
                "Note concerns",
            ],
            "After Session": [
                "Document decisions",
                "Update JIRA",
                "Review process",
                "Plan next steps",
            ],
        }

        col1, col2, col3 = st.columns(3)
        for (title, tips), col in zip(tips_data.items(), [col1, col2, col3]):
            with col:
                st.markdown(
                    f"""
                <div style="
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    border-left: 4px solid #007DBA;">
                    <h4>{title}</h4>
                    <ul>
                        {"".join([f"<li>{tip}</li>" for tip in tips])}
                    </ul>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with process_tabs[1]:
        st.header("Sprint Cycle Overview")

        # Create a Gantt-like chart for sprint cycle
        sprint_activities = {
            "Sprint Planning": [1, 2],
            "Daily Stand-ups": [2, 9],
            "Development": [2, 9],
            "Testing": [3, 9],
            "Sprint Review": [9, 10],
            "Retrospective": [10, 10],
        }

        fig = go.Figure()

        for idx, (activity, [start, end]) in enumerate(sprint_activities.items()):
            fig.add_trace(
                go.Bar(
                    name=activity,
                    y=[activity],
                    x=[end - start],
                    orientation="h",
                    base=[start],
                    marker_color=[
                        "#007DBA",
                        "#0A2F64",
                        "#78BE20",
                        "#1E1E1E",
                        "#FFFFFF",
                    ][idx % 5],
                    hovertemplate=f"{activity}<br>Days: {start}-{end}<extra></extra>",
                )
            )

        fig.update_layout(
            title="Sprint Timeline (10 Days)",
            barmode="stack",
            showlegend=False,
            xaxis_title="Sprint Days",
            height=300,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Sprint Activities Details
        for activity, [start, end] in sprint_activities.items():
            st.markdown(
                f"""
            <div style='
                padding: 15px;
                margin: 10px 0;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #007DBA;'>
                <h4>{activity}</h4>
                <p>Days {start}-{end}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with process_tabs[2]:
        st.header("Agile Best Practices")

        # Create an interactive best practices guide
        practices = {
            "Team Collaboration": {
                "Communication": 90,
                "Knowledge Sharing": 85,
                "Cross-functional Work": 80,
                "Pair Programming": 75,
            },
            "Quality Standards": {
                "Code Reviews": 95,
                "Testing Coverage": 90,
                "Documentation": 85,
                "CI/CD": 80,
            },
            "Process Improvement": {
                "Retrospectives": 90,
                "Metrics Tracking": 85,
                "Feedback Loops": 80,
                "Innovation": 75,
            },
        }

        for category, items in practices.items():
            st.subheader(category)

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=list(items.keys()), y=list(items.values()), marker_color="#007DBA"
                )
            )

            fig.update_layout(yaxis_title="Importance Score", height=300)

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
