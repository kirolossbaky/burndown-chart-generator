# Burndown Chart Generator 🚀

## Overview
A web-based tool to create and visualize project burndown charts, helping teams track progress and manage project timelines.

## Features
- Interactive web interface
- Dynamic progress tracking
- Automatic chart generation
- Progress summary

## Deployment

### Render (Free Hosting)
1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py`
   - Python Version: 3.9

### Local Development
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage
1. Enter project details
2. Add progress updates
3. Generate burndown chart
4. View project progress summary

## Technologies
- Python
- Streamlit
- Matplotlib
- Pandas

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
