import streamlit as st
import os
from datetime import datetime
from burndown_chart import BurndownChart, BurndownChartError

def main():
    st.set_page_config(
        page_title="Burndown Chart Generator", 
        page_icon="📊", 
        layout="wide"
    )
    
    st.title("🚀 Burndown Chart Generator")
    st.markdown("Create and visualize your project's progress!")

    # Project Details Input
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project Name", "My Project")
    
    with col2:
        total_story_points = st.number_input("Total Story Points", min_value=1, value=100)

    # Date Range Input
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Project Start Date", datetime.now())
    
    with col2:
        end_date = st.date_input("Project End Date", datetime.now())

    # Progress Tracking
    st.subheader("Progress Updates")
    progress_updates = st.data_editor(
        data=[],
        num_rows="dynamic",
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "completed_points": st.column_config.NumberColumn("Completed Points", min_value=0),
            "description": st.column_config.TextColumn("Description")
        },
        hide_index=True
    )

    # Generate Chart Button
    if st.button("Generate Burndown Chart"):
        try:
            # Convert dates to datetime
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())

            # Create Burndown Chart
            burndown = BurndownChart(
                project_name=project_name, 
                start_date=start_datetime, 
                end_date=end_datetime, 
                total_story_points=total_story_points
            )

            # Add Progress Updates
            for update in progress_updates:
                burndown.update_progress(
                    date=datetime.combine(update['date'], datetime.min.time()),
                    completed_story_points=update['completed_points'],
                    description=update.get('description', '')
                )

            # Generate Chart
            chart_filename = f"{project_name.replace(' ', '_')}_burndown.png"
            burndown.generate_chart(chart_filename)

            # Display Chart and Summary
            st.image(chart_filename)

            # Show Progress Summary
            summary = burndown.get_progress_summary()
            st.subheader("Project Progress Summary")
            for key, value in summary.items():
                st.metric(label=key.replace('_', ' ').title(), value=value)

        except BurndownChartError as e:
            st.error(f"Error creating burndown chart: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # Footer
    st.markdown("---")
    st.markdown("🔧 Built with ❤️ by Burndown Chart Generator")

if __name__ == "__main__":
    # Render requires binding to 0.0.0.0
    port = int(os.environ.get("PORT", 8501))
    st.run(port=port, host="0.0.0.0")
