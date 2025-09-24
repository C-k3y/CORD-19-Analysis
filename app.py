# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_analysis import CORD19Analyzer
import os

# Page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="main-header">CORD-19 COVID-19 Research Data Explorer</div>', 
                unsafe_allow_html=True)
    
    st.write("""
    This application provides an interactive exploration of the CORD-19 dataset, 
    which contains metadata about COVID-19 research papers. Explore publication trends, 
    top journals, and common research topics.
    """)
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_section = st.sidebar.radio(
        "Go to:",
        ["Data Overview", "Publication Trends", "Journal Analysis", 
         "Text Analysis", "Source Analysis", "Sample Data"]
    )
    
    # File upload
    st.sidebar.markdown("---")
    st.sidebar.header("Data Configuration")
    
    # Check if data file exists
    data_file = "data/metadata.csv"
    
    if not os.path.exists(data_file):
        st.error(f"Data file not found at: {data_file}")
        st.info("""
        Please download the metadata.csv file from the CORD-19 dataset:
        https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge
        
        Place the file in the 'data' directory.
        """)
        return
    
    # Initialize analyzer
    analyzer = CORD19Analyzer(data_file)
    
    # Load data with caching
    @st.cache_data
    def load_and_clean_data():
        if analyzer.load_data():
            analyzer.clean_data()
            return True
        return False
    
    if not load_and_clean_data():
        st.error("Failed to load data. Please check the data file.")
        return
    
    # Data Overview Section
    if app_section == "Data Overview":
        st.markdown('<div class="section-header">Dataset Overview</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Information")
            st.write(f"**Dataset Shape:** {analyzer.df.shape[0]} rows, {analyzer.df.shape[1]} columns")
            
            # Display data types
            st.subheader("Data Types")
            dtype_info = analyzer.df.dtypes.reset_index()
            dtype_info.columns = ['Column', 'Data Type']
            st.dataframe(dtype_info, use_container_width=True)
        
        with col2:
            st.subheader("Missing Values")
            missing_info = analyzer.basic_exploration()
            if missing_info is not None:
                # Show top 10 columns with most missing values
                st.dataframe(missing_info.head(10), use_container_width=True)
        
        # Basic statistics
        st.subheader("Basic Statistics")
        st.dataframe(analyzer.df.describe(), use_container_width=True)
    
    # Publication Trends Section
    elif app_section == "Publication Trends":
        st.markdown('<div class="section-header">Publication Trends Over Time</div>', 
                    unsafe_allow_html=True)
        
        st.write("Explore how COVID-19 research publications have evolved over time.")
        
        # Year range selector
        min_year = int(analyzer.df_clean['year'].min())
        max_year = int(analyzer.df_clean['year'].max())
        
        year_range = st.slider(
            "Select year range:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        
        # Filter data based on selection
        filtered_data = analyzer.df_clean[
            (analyzer.df_clean['year'] >= year_range[0]) & 
            (analyzer.df_clean['year'] <= year_range[1])
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Publications by Year")
            yearly_counts = filtered_data['year'].value_counts().sort_index()
            st.bar_chart(yearly_counts)
            
            # Display summary statistics
            st.metric("Total Publications in Range", len(filtered_data))
            st.metric("Average Publications per Year", 
                     round(len(filtered_data) / (year_range[1] - year_range[0] + 1)))
        
        with col2:
            st.subheader("Monthly Distribution (Latest Year)")
            latest_year_data = filtered_data[filtered_data['year'] == max_year]
            if not latest_year_data.empty:
                monthly_counts = latest_year_data['month'].value_counts().sort_index()
                st.bar_chart(monthly_counts)
            else:
                st.info(f"No data available for {max_year}")
    
    # Journal Analysis Section
    elif app_section == "Journal Analysis":
        st.markdown('<div class="section-header">Journal Analysis</div>', 
                    unsafe_allow_html=True)
        
        top_n = st.slider("Number of top journals to display:", 5, 20, 10)
        
        fig, journal_counts = analyzer.analyze_journals(top_n=top_n)
        st.pyplot(fig)
        
        # Display journal statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Journals", analyzer.df_clean['journal_clean'].nunique())
        with col2:
            st.metric("Publications with Journal Info", 
                     analyzer.df_clean['journal_clean'].notna().sum())
        with col3:
            if journal_counts is not None:
                st.metric("Top Journal Publications", journal_counts.iloc[0])
        
        # Show top journals table
        st.subheader(f"Top {top_n} Journals")
        journal_table = journal_counts.reset_index()
        journal_table.columns = ['Journal', 'Publication Count']
        journal_table['Rank'] = range(1, len(journal_table) + 1)
        st.dataframe(journal_table[['Rank', 'Journal', 'Publication Count']], 
                    use_container_width=True)
    
    # Text Analysis Section
    elif app_section == "Text Analysis":
        st.markdown('<div class="section-header">Text Analysis</div>', 
                    unsafe_allow_html=True)
        
        text_source = st.selectbox(
            "Select text source for analysis:",
            ["title", "abstract"]
        )
        
        max_words = st.slider("Maximum words in word cloud:", 50, 200, 100)
        
        fig, word_freq = analyzer.create_word_cloud(
            text_column=text_source, 
            max_words=max_words
        )
        st.pyplot(fig)
        
        # Show most frequent words
        if word_freq:
            st.subheader("Most Frequent Words")
            word_df = pd.DataFrame(list(word_freq.items()), 
                                 columns=['Word', 'Frequency']).sort_values('Frequency', ascending=False)
            st.dataframe(word_df.head(20), use_container_width=True)
    
    # Source Analysis Section
    elif app_section == "Source Analysis":
        st.markdown('<div class="section-header">Source Analysis</div>', 
                    unsafe_allow_html=True)
        
        fig, source_counts = analyzer.analyze_sources()
        st.pyplot(fig)
        
        if source_counts is not None:
            st.subheader("Publications by Source")
            source_table = source_counts.reset_index()
            source_table.columns = ['Source', 'Publication Count']
            st.dataframe(source_table, use_container_width=True)
    
    # Sample Data Section
    elif app_section == "Sample Data":
        st.markdown('<div class="section-header">Sample Data</div>', 
                    unsafe_allow_html=True)
        
        sample_size = st.slider("Number of samples to display:", 5, 50, 10)
        
        sample_data = analyzer.get_sample_data(sample_size)
        st.dataframe(sample_data, use_container_width=True)
        
        # Data quality metrics
        st.subheader("Data Quality Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completeness = (analyzer.df_clean['title'].notna().sum() / len(analyzer.df_clean)) * 100
            st.metric("Title Completeness", f"{completeness:.1f}%")
        
        with col2:
            abstract_completeness = (analyzer.df_clean['abstract'].notna().sum() / len(analyzer.df_clean)) * 100
            st.metric("Abstract Completeness", f"{abstract_completeness:.1f}%")
        
        with col3:
            journal_completeness = (analyzer.df_clean['journal'].notna().sum() / len(analyzer.df_clean)) * 100
            st.metric("Journal Completeness", f"{journal_completeness:.1f}%")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **About this app:** This application analyzes the CORD-19 dataset containing COVID-19 research papers metadata.
    The data is provided by the Allen Institute for AI and available on Kaggle.
    """)

if __name__ == "__main__":
    main()
