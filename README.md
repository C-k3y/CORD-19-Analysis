# CORD-19 COVID-19 Research Data Explorer

A Streamlit application for exploring and analyzing the CORD-19 dataset containing metadata about COVID-19 research papers.

## Features

- **Data Overview**: Basic dataset information, data types, and missing values analysis
- **Publication Trends**: Analysis of publications over time with interactive year range selection
- **Journal Analysis**: Top journals publishing COVID-19 research
- **Text Analysis**: Word clouds and frequency analysis of titles and abstracts
- **Source Analysis**: Distribution of publications by source
- **Sample Data**: Interactive data sampling with quality metrics

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd CORD-19-Analysis

```

Install required packages
```bash
pip install -r requirements.txt

```
Usage
```bash
streamlit run app.py

```
Project Structure

CORD-19-Analysis/
├── app.py                 # Main Streamlit application
├── data_analysis.py       # Data analysis functions
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── data/                 # Data directory (contains metadata.csv)

Data Source
The CORD-19 dataset is provided by the Allen Institute for AI and available on Kaggle:
https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge

License
This project is for educational purposes as part of the Frameworks assignment.

## How to Run the Project

1. Create the project directory structure
2. Save each code block in its respective file
3. Install the requirements: `pip install -r requirements.txt`
4. Download the `metadata.csv` file from Kaggle and place it in the `data/` directory
5. Run the application: `streamlit run app.py`

## Expected Outcomes

This implementation provides:

1. **Complete data analysis** with cleaning, exploration, and visualization
2. **Interactive Streamlit app** with multiple sections for different analyses
3. **Professional documentation** with setup instructions
4. **Modular code structure** that's easy to understand and extend

The application will help users explore COVID-19 research trends, identify key journals and sources, and understand the research landscape through interactive visualizations.

