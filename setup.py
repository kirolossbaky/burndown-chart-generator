from setuptools import setup, find_packages

setup(
    name="burndown-chart-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.8.2",
        "pandas==2.2.1",
        "numpy==1.26.3",
        "streamlit==1.32.2"
    ],
    python_requires='>=3.9',
)
