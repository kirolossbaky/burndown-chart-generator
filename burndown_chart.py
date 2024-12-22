import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

class BurndownChartError(Exception):
    """Custom exception for Burndown Chart related errors"""
    pass

class Task:
    def __init__(self, name, estimated_points, actual_points=None, complexity=None):
        """
        Represents a single task in the project
        
        :param name: Task name
        :param estimated_points: Points estimated for the task
        :param actual_points: Actual points taken to complete the task
        :param complexity: Task complexity (easy, medium, hard)
        """
        self.name = name
        self.estimated_points = estimated_points
        self.actual_points = actual_points
        self.complexity = complexity
        self.status = 'Not Started'
        self.start_date = None
        self.end_date = None

    def complete(self, actual_points=None, end_date=None):
        """
        Mark task as completed
        
        :param actual_points: Actual points taken
        :param end_date: Date of completion
        """
        self.status = 'Completed'
        self.actual_points = actual_points or self.estimated_points
        self.end_date = end_date or datetime.now()

class BurndownChart:
    def __init__(self, project_name, start_date, end_date, total_story_points):
        """
        Initialize a Burndown Chart for project tracking
        
        :param project_name: Name of the project
        :param start_date: Project start date
        :param end_date: Project end date
        :param total_story_points: Total story points for the project
        """
        # Input validation with more flexible handling
        if not project_name or not isinstance(project_name, str):
            raise BurndownChartError("Project name must be a non-empty string")
        
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise BurndownChartError("Start and end dates must be datetime objects")
        
        # Automatically adjust end date if it's before or equal to start date
        if start_date >= end_date:
            end_date = start_date + timedelta(days=14)
        
        if not isinstance(total_story_points, (int, float)) or total_story_points <= 0:
            raise BurndownChartError("Total story points must be a positive number")
        
        self.project_name = project_name
        self.start_date = start_date
        self.end_date = end_date
        self.total_story_points = float(total_story_points)
        
        # Task management
        self.tasks = []
        self.progress_log = []
        
        # Create initial dataframe for tracking
        self.df = self._create_initial_dataframe()
    
    def add_task(self, task):
        """
        Add a task to the project
        
        :param task: Task object to add
        """
        if not isinstance(task, Task):
            raise BurndownChartError("Must provide a Task object")
        
        self.tasks.append(task)
        return task
    
    def estimate_complexity_points(self, complexity):
        """
        Estimate points based on task complexity
        
        :param complexity: Task complexity (easy, medium, hard)
        :return: Estimated story points
        """
        complexity_map = {
            'easy': (1, 3),
            'medium': (3, 8),
            'hard': (8, 13)
        }
        
        if complexity.lower() not in complexity_map:
            raise BurndownChartError("Invalid complexity. Choose from: easy, medium, hard")
        
        min_points, max_points = complexity_map[complexity.lower()]
        return np.random.randint(min_points, max_points + 1)
    
    def _create_initial_dataframe(self):
        """
        Create initial dataframe with project timeline and ideal burndown
        """
        date_range = pd.date_range(start=self.start_date, end=self.end_date)
        total_days = len(date_range)
        
        # Create ideal burndown line
        ideal_burndown = [self.total_story_points - (self.total_story_points * day / (total_days - 1)) 
                          for day in range(total_days)]
        
        df = pd.DataFrame({
            'Date': date_range,
            'Ideal_Burndown': ideal_burndown,
            'Actual_Burndown': ideal_burndown.copy(),
            'Estimated_Burndown': ideal_burndown.copy()
        })
        
        return df
    
    def update_progress(self, date, completed_story_points, description=None):
        """
        Update actual progress for a specific date
        
        :param date: Date of progress update
        :param completed_story_points: Story points completed by this date
        :param description: Optional description of the progress update
        """
        # Input validation
        if not isinstance(date, datetime):
            raise BurndownChartError("Date must be a datetime object")
        
        if not isinstance(completed_story_points, (int, float)) or completed_story_points < 0:
            raise BurndownChartError("Completed story points must be a non-negative number")
        
        if completed_story_points > self.total_story_points:
            raise BurndownChartError("Completed story points cannot exceed total story points")
        
        # Ensure date is within project timeline
        if date < self.start_date or date > self.end_date:
            # Adjust date to project timeline if out of bounds
            date = max(min(date, self.end_date), self.start_date)
        
        # Log the progress update
        progress_entry = {
            'date': date,
            'completed_points': completed_story_points,
            'description': description
        }
        self.progress_log.append(progress_entry)
        
        # Update the dataframe
        mask = self.df['Date'] == pd.to_datetime(date)
        if mask.any():
            self.df.loc[mask, 'Actual_Burndown'] = self.total_story_points - completed_story_points
    
    def generate_chart(self, output_file='burndown_chart.png', show_progress_points=True):
        """
        Generate and save burndown chart
        
        :param output_file: File path to save the chart
        :param show_progress_points: Whether to show individual progress points
        """
        plt.figure(figsize=(14, 8))
        
        # Ideal Burndown Line
        plt.plot(self.df['Date'], self.df['Ideal_Burndown'], 
                 label='Ideal Burndown', color='blue', linestyle='--')
        
        # Actual Burndown Line
        plt.plot(self.df['Date'], self.df['Actual_Burndown'], 
                 label='Actual Burndown', color='red', marker='o')
        
        # Estimated Burndown Line
        plt.plot(self.df['Date'], self.df['Estimated_Burndown'], 
                 label='Estimated Burndown', color='green', linestyle=':')
        
        # Optionally show progress points
        if show_progress_points:
            progress_dates = [entry['date'] for entry in self.progress_log]
            progress_points = [self.total_story_points - entry['completed_points'] for entry in self.progress_log]
            plt.scatter(progress_dates, progress_points, color='purple', s=100, zorder=5, 
                        label='Progress Updates', marker='x')
        
        plt.title(f'Burndown Chart - {self.project_name}')
        plt.xlabel('Date')
        plt.ylabel('Remaining Story Points')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        print(f"Burndown chart saved to {output_file}")
    
    def get_progress_summary(self):
        """
        Generate a summary of project progress
        
        :return: Dictionary with progress statistics
        """
        if not self.progress_log:
            return {
                'total_story_points': self.total_story_points,
                'completed_story_points': 0,
                'progress_percentage': 0,
                'estimated_vs_actual_variance': 0
            }
        
        latest_progress = self.progress_log[-1]
        
        # Calculate estimated vs actual variance
        total_estimated = sum(task.estimated_points for task in self.tasks)
        total_actual = sum(task.actual_points or task.estimated_points for task in self.tasks)
        variance = abs(total_estimated - total_actual) / total_estimated * 100 if total_estimated else 0
        
        return {
            'total_story_points': self.total_story_points,
            'completed_story_points': latest_progress['completed_points'],
            'progress_percentage': (latest_progress['completed_points'] / self.total_story_points) * 100,
            'estimated_vs_actual_variance': variance
        }

def main():
    # Example usage with more detailed progress tracking
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    try:
        burndown = BurndownChart(
            project_name="Sample Project", 
            start_date=start_date, 
            end_date=end_date, 
            total_story_points=100
        )
        
        # Create tasks with complexity-based estimation
        task1 = burndown.add_task(Task(
            name="Backend Infrastructure", 
            estimated_points=burndown.estimate_complexity_points('hard'),
            complexity='hard'
        ))
        task1.complete(actual_points=10, end_date=datetime(2024, 1, 7))
        
        task2 = burndown.add_task(Task(
            name="Core Features", 
            estimated_points=burndown.estimate_complexity_points('medium'),
            complexity='medium'
        ))
        task2.complete(actual_points=15, end_date=datetime(2024, 1, 14))
        
        # Simulate progress updates with descriptions
        burndown.update_progress(datetime(2024, 1, 7), 30, "Completed backend infrastructure")
        burndown.update_progress(datetime(2024, 1, 14), 60, "Implemented core features")
        burndown.update_progress(datetime(2024, 1, 21), 85, "Added user interface")
        burndown.update_progress(datetime(2024, 1, 28), 100, "Final testing and deployment")
        
        # Generate chart
        burndown.generate_chart('burndown_chart.png')
        
        # Print progress summary
        progress_summary = burndown.get_progress_summary()
        print("\nProject Progress Summary:")
        for key, value in progress_summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
    except BurndownChartError as e:
        print(f"Error creating burndown chart: {e}")

if __name__ == "__main__":
    main()
