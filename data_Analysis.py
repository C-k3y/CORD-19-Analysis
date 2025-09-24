import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class CORD19Analyzer:
    def __init__(self, file_path):
        """Initialize the analyzer with the dataset path"""
        self.file_path = file_path
        self.df = None
        self.df_clean = None
        
    def load_data(self):
        """Load the metadata.csv file"""
        try:
            self.df = pd.read_csv(self.file_path)
            print(f"Dataset loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def basic_exploration(self):
        """Perform basic data exploration"""
        if self.df is None:
            print("Please load data first")
            return
        
        print("=== BASIC DATASET INFORMATION ===")
        print(f"Dataset shape: {self.df.shape}")
        print("\nColumn names and data types:")
        print(self.df.dtypes)
        
        print("\n=== MISSING VALUES ===")
        missing_data = self.df.isnull().sum()
        missing_percent = (missing_data / len(self.df)) * 100
        missing_info = pd.DataFrame({
            'Missing Count': missing_data,
            'Missing Percentage': missing_percent
        }).sort_values('Missing Count', ascending=False)
        print(missing_info.head(10))
        
        print("\n=== BASIC STATISTICS ===")
        print(self.df.describe())
        
        return missing_info
    
    def clean_data(self):
        """Clean and prepare the data for analysis"""
        if self.df is None:
            print("Please load data first")
            return
        
        # Create a copy for cleaning
        self.df_clean = self.df.copy()
        
        # Handle publication date
        print("Processing publication dates...")
        self.df_clean['publish_time'] = pd.to_datetime(
            self.df_clean['publish_time'], errors='coerce'
        )
        self.df_clean['year'] = self.df_clean['publish_time'].dt.year
        self.df_clean['month'] = self.df_clean['publish_time'].dt.month
        
        # Extract abstract word count
        print("Calculating abstract word counts...")
        self.df_clean['abstract_word_count'] = self.df_clean['abstract'].apply(
            lambda x: len(str(x).split()) if pd.notnull(x) else 0
        )
        
        # Clean journal names
        self.df_clean['journal_clean'] = self.df_clean['journal'].str.lower().str.strip()
        
        print(f"Data cleaning completed. Clean dataset shape: {self.df_clean.shape}")
        return self.df_clean
    
    def analyze_publications_over_time(self):
        """Analyze publication trends over time"""
        if self.df_clean is None:
            print("Please clean data first")
            return
        
        # Publications by year
        yearly_counts = self.df_clean['year'].value_counts().sort_index()
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Yearly trend
        ax1.bar(yearly_counts.index, yearly_counts.values)
        ax1.set_title('Number of Publications by Year')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Number of Publications')
        ax1.tick_params(axis='x', rotation=45)
        
        # Monthly trend for latest year
        latest_year = self.df_clean['year'].max()
        monthly_latest = self.df_clean[self.df_clean['year'] == latest_year]['month'].value_counts().sort_index()
        ax2.bar(monthly_latest.index, monthly_latest.values)
        ax2.set_title(f'Publications by Month ({latest_year})')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Number of Publications')
        
        plt.tight_layout()
        return fig, yearly_counts
    
    def analyze_journals(self, top_n=15):
        """Analyze publications by journal"""
        if self.df_clean is None:
            print("Please clean data first")
            return
        
        # Top journals
        journal_counts = self.df_clean['journal_clean'].value_counts().head(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        journal_counts.plot(kind='barh', ax=ax)
        ax.set_title(f'Top {top_n} Journals by Number of Publications')
        ax.set_xlabel('Number of Publications')
        plt.tight_layout()
        
        return fig, journal_counts
    
    def create_word_cloud(self, text_column='title', max_words=100):
        """Create a word cloud from text data"""
        if self.df_clean is None:
            print("Please clean data first")
            return
        
        # Combine all text
        all_text = ' '.join(self.df_clean[text_column].dropna().astype(str))
        
        # Clean text
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        word_freq = Counter(words)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'with', 'on', 
                     'as', 'by', 'from', 'that', 'this', 'is', 'are', 'was', 'were',
                     'be', 'been', 'have', 'has', 'had', 'but', 'not', 'which',
                     'their', 'from', 'can', 'we', 'our', 'an', 'will', 'has', 'study'}
        
        filtered_words = {word: count for word, count in word_freq.items() 
                         if word not in stop_words and count > 10}
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=max_words
        ).generate_from_frequencies(filtered_words)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'Word Cloud from {text_column.capitalize()}s')
        
        return fig, filtered_words
    
    def analyze_sources(self):
        """Analyze publications by source"""
        if self.df_clean is None:
            print("Please clean data first")
            return
        
        source_counts = self.df_clean['source_x'].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        source_counts.plot(kind='bar', ax=ax)
        ax.set_title('Publications by Source')
        ax.set_xlabel('Source')
        ax.set_ylabel('Number of Publications')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        return fig, source_counts
    
    def get_sample_data(self, n=5):
        """Get a sample of the cleaned data"""
        if self.df_clean is None:
            print("Please clean data first")
            return
        
        sample_columns = ['title', 'abstract', 'journal', 'year', 'source_x']
        available_columns = [col for col in sample_columns if col in self.df_clean.columns]
        
        return self.df_clean[available_columns].head(n)
