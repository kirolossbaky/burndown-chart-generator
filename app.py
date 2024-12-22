import streamlit as st
import os
from datetime import datetime
from burndown_chart import BurndownChart, Task, BurndownChartError

def main():
    st.set_page_config(
        page_title="Advanced Burndown Chart Generator", 
        page_icon="📊", 
        layout="wide"
    )
    
    st.title("🚀 Advanced Burndown Chart Generator")
    st.markdown("Create, track, and analyze your project's progress with precision!")

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

    # Task Management Section
    st.subheader("🛠 Task Management")
    
    # Task Input
    task_name = st.text_input("Task Name")
    task_complexity = st.selectbox("Task Complexity", ["Easy", "Medium", "Hard"])
    
    # Initialize burndown chart
    burndown = BurndownChart(
        project_name=project_name, 
        start_date=datetime.combine(start_date, datetime.min.time()), 
        end_date=datetime.combine(end_date, datetime.min.time()), 
        total_story_points=total_story_points
    )
    
    # Task Creation and Estimation
    if st.button("Add Task"):
        try:
            # Estimate points based on complexity
            estimated_points = burndown.estimate_complexity_points(task_complexity.lower())
            
            # Create and add task
            task = Task(
                name=task_name, 
                estimated_points=estimated_points,
                complexity=task_complexity.lower()
            )
            burndown.add_task(task)
            
            st.success(f"Task '{task_name}' added with {estimated_points} estimated points")
        except BurndownChartError as e:
            st.error(f"Error adding task: {e}")

    # Progress Updates
    st.subheader("📈 Progress Updates")
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
            # Validate date range
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())

            if start_datetime >= end_datetime:
                st.error("End date must be after start date")
                return

            # Add Progress Updates
            for update in progress_updates:
                if update.get('date') and update.get('completed_points') is not None:
                    burndown.update_progress(
                        date=datetime.combine(update['date'], datetime.min.time()),
                        completed_story_points=update['completed_points'],
                        description=update.get('description', '')
                    )

            # Generate Chart
            chart_filename = f"{project_name.replace(' ', '_')}_burndown.png"
            burndown.generate_chart(chart_filename)

            # Display Chart
            st.image(chart_filename)

            # Show Progress Summary
            summary = burndown.get_progress_summary()
            st.subheader("🔍 Project Progress Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Story Points", summary['total_story_points'])
            with col2:
                st.metric("Completed Points", summary['completed_story_points'])
            with col3:
                st.metric("Progress", f"{summary['progress_percentage']:.2f}%")
            with col4:
                st.metric("Est. vs Actual Variance", f"{summary['estimated_vs_actual_variance']:.2f}%")

            # Task Details
            st.subheader("📋 Task Breakdown")
            task_data = []
            for task in burndown.tasks:
                task_data.append({
                    "Name": task.name,
                    "Complexity": task.complexity,
                    "Estimated Points": task.estimated_points,
                    "Actual Points": task.actual_points or "Not Completed",
                    "Status": task.status
                })
            
            st.dataframe(task_data)

        except BurndownChartError as e:
            st.error(f"Error creating burndown chart: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    # Footer
    st.markdown("---")
    st.markdown("🔧 Built with ❤️ by Advanced Burndown Chart Generator")

if __name__ == "__main__":
    main()
