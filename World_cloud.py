import pandas as pd
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import Counter
from connect_sql import read_data

# Read Data from Sql server
data = read_data()

# Read job keywords from the text file
with open('job keywords.txt', 'r') as file:
    job_keywords = file.read()

# Clean job keywords
job_keywords = job_keywords.replace("'", "").split(',')
job_keywords = [f" {keyword.strip().lower()} " for keyword in job_keywords]

# Set stopwords
stop_words = set(stopwords.words('english'))

# Extract the job descriptions column
job_descriptions = data['job_description'].dropna().tolist()

def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s\n]', '', text)  # Remove punctuation
    text = ' '.join([word for word in text.split() if word not in stop_words])  # Remove stopwords
    return text


preprocessed_descriptions = [preprocess_text(desc) for desc in job_descriptions]

# Combine all job descriptions into a single string
combined_text = ' '.join(preprocessed_descriptions)

keyword_freq = Counter()
for keyword in job_keywords:
    keyword_freq[keyword] = combined_text.count(keyword)

# Print keyword frequencies to check the content
print("Keyword Frequencies:", keyword_freq)

# Create a word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(keyword_freq)

# Plot the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
