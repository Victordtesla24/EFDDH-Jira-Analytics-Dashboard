"""JIRA Handbook UI component."""

import pandas as pd
import streamlit as st


def show_handbook(data: pd.DataFrame = None) -> None:
    """Display the JIRA handbook documentation."""
    st.markdown('<div class="doc-section">', unsafe_allow_html=True)
    st.header("📚 JIRA Handbook")

    # Tabs within the handbook
    handbook_tabs = st.tabs(
        ["Mandatory Fields", "Estimation Guide", "Project Guidelines"]
    )

    with handbook_tabs[0]:
        st.subheader("Required Fields and Impact Analysis")

        # Create a DataFrame for the mandatory fields table
        mandatory_fields = {
            "Field Name": [
                "Story Points",
                "Status",
                "Issue Type",
                "Priority",
                "Epic Link",
                "Sprint",
                "Assignee",
                "Created Date",
                "Summary",
            ],
            "Responsible": [
                "Assignee",
                "Assignee/Scrum Master",
                "Story Creator",
                "Story Creator",
                "Story Creator",
                "Scrum Master",
                "Scrum Master",
                "System Generated",
                "Story Creator",
            ],
            "Impact if Missing": [
                "Velocity metrics, capacity planning, and effort estimation will be inaccurate",
                "Progress tracking, completion rates, and workflow analysis will be affected",
                "Issue categorization and filtering capabilities will be limited",
                "Work prioritization and resource allocation analysis will be impacted",
                "Epic progress tracking and feature completion metrics will be incomplete",
                "Sprint velocity and timeline analysis will be affected",
                "Resource allocation and capacity management will be inaccurate",
                "Timeline analysis and trend reporting will be affected",
                "Issue identification and search capabilities will be limited",
            ],
        }

        df_fields = pd.DataFrame(mandatory_fields)
        st.markdown('<div class="styled-table">', unsafe_allow_html=True)
        st.table(df_fields)
        st.markdown("</div>", unsafe_allow_html=True)

    with handbook_tabs[1]:
        st.subheader("Story Point Estimation Guide")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                """
            ### Story Point Scale

            | Points | Complexity | Time Estimate |
            |--------|------------|---------------|
            | 1 | Very Simple | Few hours |
            | 2 | Simple | Half day |
            | 3 | Moderate | 1 day |
            | 5 | Complex | 2-3 days |
            | 8 | Very Complex | 3-5 days |
            | 13 | Extremely Complex | 5+ days |
            """
            )

            st.markdown(
                """
            ### Estimation Best Practices

            1. **Compare to Benchmark Stories**
               - Use known completed stories as reference
               - Consider relative complexity

            2. **Consider All Factors**
               - Technical complexity
               - Dependencies
               - Testing requirements
               - Documentation needs

            3. **Team Consensus**
               - Use planning poker
               - Discuss different perspectives
               - Reach team agreement
            """
            )

        with col2:
            st.markdown("### Benchmark Story Example")
            if data is not None and not data.empty:
                # Find and display a 1-point story as benchmark
                benchmark_stories = data[
                    (data["Story Points"] == 1) & (data["Issue Type"] == "Story")
                ]
                if not benchmark_stories.empty:
                    benchmark_story = benchmark_stories.iloc[0]
                    st.markdown(
                        f"""
                    **Issue Key**: {benchmark_story['Issue key']}

                    **Summary**: {benchmark_story['Summary']}

                    **Story Points**: 1

                    This story represents our baseline for a 1-point story because:
                    - Clear, single-purpose task
                    - Minimal dependencies
                    - Well-defined scope
                    - Standard implementation
                    """
                    )
            else:
                st.info("Upload JIRA data to see a benchmark story example")

            st.markdown(
                """
            ### Estimation Process

            1. **Preparation**
               - Review story details
               - Understand acceptance criteria
               - Identify dependencies

            2. **Team Discussion**
               - Share understanding
               - Raise concerns
               - Identify risks

            3. **Estimation**
               - Compare to benchmarks
               - Consider complexity factors
               - Use planning poker

            4. **Finalization**
               - Reach consensus
               - Document assumptions
               - Update story points
            """
            )

    with handbook_tabs[2]:
        st.subheader("Project Management Guidelines")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                """
            ### Issue Management

            #### Creation Guidelines
            - Use clear, descriptive titles
            - Include detailed acceptance criteria
            - Link related issues
            - Add relevant labels

            #### Workflow States
            1. To Do
            2. In Progress
            3. Review
            4. Done

            #### Quality Standards
            - Complete acceptance criteria
            - Proper issue links
            - Updated status
            - Regular updates
            """
            )

        with col2:
            st.markdown(
                """
            ### Sprint Management

            #### Planning
            - Regular backlog refinement
            - Clear sprint goals
            - Realistic capacity planning
            - Risk assessment

            #### Execution
            - Daily updates
            - Blocker resolution
            - Progress tracking
            - Team communication

            #### Review
            - Demo preparation
            - Stakeholder feedback
            - Documentation updates
            - Lessons learned
            """
            )

    st.markdown("</div>", unsafe_allow_html=True)
