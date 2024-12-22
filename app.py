import streamlit as st
import os
from datetime import datetime
from burndown_chart import BurndownChart, Task, BurndownChartError
from trello_integration import TrelloIntegration, authenticate_trello

def main():
    st.set_page_config(
        page_title="Advanced Burndown Chart Generator", 
        page_icon="📊", 
        layout="wide"
    )
    
    st.title("🚀 Advanced Burndown Chart Generator")
    st.markdown("Create, track, and analyze your project's progress with precision!")

    # Trello Authentication
    trello_integration = authenticate_trello()

    # Trello Board and List Selection
    if trello_integration and hasattr(st.session_state, 'trello_boards'):
        st.sidebar.header("🔗 Trello Integration")
        
        # Select Board
        board_id = st.sidebar.selectbox(
            "Select Trello Board", 
            options=[board['id'] for board in st.session_state.trello_boards],
            format_func=lambda x: next(board['name'] for board in st.session_state.trello_boards if board['id'] == x)
        )
        
        # Get Lists in the Board
        lists = trello_integration.get_board_lists(board_id)
        list_id = st.sidebar.selectbox(
            "Select List", 
            options=[lst['id'] for lst in lists],
            format_func=lambda x: next(lst['name'] for lst in lists if lst['id'] == x)
        )
        
        # Import Tasks from Trello
        if st.sidebar.button("Import Trello Tasks"):
            try:
                cards = trello_integration.get_cards_from_list(list_id)
                st.sidebar.success(f"Imported {len(cards)} tasks from Trello")
                st.session_state.trello_tasks = cards
            except Exception as e:
                st.sidebar.error(f"Error importing tasks: {e}")

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
    col1, col2 = st.columns(2)
    with col1:
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
    
    # Trello Task Creation
    with col2:
        if trello_integration and st.button("Create Trello Card"):
            try:
                estimated_points = burndown.estimate_complexity_points(task_complexity.lower())
                card = trello_integration.create_burndown_card(
                    board_id=board_id, 
                    list_id=list_id, 
                    task_name=task_name, 
                    estimated_points=estimated_points,
                    complexity=task_complexity.lower()
                )
                st.success(f"Created Trello Card: {card['name']}")
            except Exception as e:
                st.error(f"Error creating Trello card: {e}")

    # Imported Trello Tasks
    if trello_integration and hasattr(st.session_state, 'trello_tasks'):
        st.subheader("📥 Imported Trello Tasks")
        imported_tasks = st.data_editor(
            data=st.session_state.trello_tasks,
            num_rows="dynamic",
            column_config={
                "name": st.column_config.TextColumn("Task Name"),
                "complexity": st.column_config.SelectboxColumn(
                    "Complexity", 
                    options=["easy", "medium", "hard"]
                ),
                "due_date": st.column_config.DateColumn("Due Date")
            },
            hide_index=True
        )
        
        # Add imported tasks to burndown chart
        if st.button("Add Imported Tasks to Burndown"):
            for task in imported_tasks:
                try:
                    burndown_task = Task(
                        name=task['name'], 
                        estimated_points=burndown.estimate_complexity_points(task['complexity']),
                        complexity=task['complexity']
                    )
                    burndown.add_task(burndown_task)
                except Exception as e:
                    st.error(f"Error adding task {task['name']}: {e}")
            st.success("Imported tasks added to Burndown Chart")

    # Progress Updates
    st.subheader("📈 Progress Updates")
    progress_updates = st.data_editor(
        data=[],
        num_rows="dynamic",
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "completed_points": st.column_config.NumberColumn("Completed Points", min_value=0),
            "description": st.column_config.TextColumn("Description"),
            "trello_card_id": st.column_config.TextColumn("Trello Card ID (Optional)")
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
                    
                    # Update Trello card if card ID is provided
                    if trello_integration and update.get('trello_card_id'):
                        try:
                            trello_integration.update_card_progress(
                                card_id=update['trello_card_id'], 
                                completed_points=update['completed_points'], 
                                status='In Progress' if update['completed_points'] < total_story_points else 'Completed'
                            )
                        except Exception as e:
                            st.error(f"Error updating Trello card: {e}")

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
