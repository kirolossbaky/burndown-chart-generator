from burndown_chart import BurndownChart
from datetime import datetime, timedelta

def main():
    # Define project timeline
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2024, 2, 28)
    
    # Create burndown chart for a software development project
    try:
        project_burndown = BurndownChart(
            project_name="Web Application Development", 
            start_date=start_date, 
            end_date=end_date, 
            total_story_points=120
        )
        
        # Log progress updates
        project_burndown.update_progress(
            date=datetime(2024, 2, 5), 
            completed_story_points=20, 
            description="Completed project setup and initial architecture"
        )
        
        project_burndown.update_progress(
            date=datetime(2024, 2, 12), 
            completed_story_points=50, 
            description="Implemented core backend services"
        )
        
        project_burndown.update_progress(
            date=datetime(2024, 2, 19), 
            completed_story_points=85, 
            description="Developed frontend components and integrated APIs"
        )
        
        project_burndown.update_progress(
            date=datetime(2024, 2, 26), 
            completed_story_points=120, 
            description="Final testing and deployment preparation"
        )
        
        # Generate burndown chart
        project_burndown.generate_chart('web_app_burndown.png')
        
        # Print progress summary
        progress_summary = project_burndown.get_progress_summary()
        print("\nProject Progress Summary:")
        for key, value in progress_summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
