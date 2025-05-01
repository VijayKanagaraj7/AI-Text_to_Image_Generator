import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def preprocess_text(text):
    """
    Preprocess and clean text input:
    1. Convert to lowercase
    2. Remove special characters except basic punctuation
    3. Tokenize text
    4. Remove common stopwords (optional)
    5. Rejoin tokens with proper spacing
    
    Args:
        text (str): The input text to preprocess
        
    Returns:
        str: The preprocessed text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Remove redundant punctuation
    clean_tokens = []
    for i, token in enumerate(tokens):
        # Skip consecutive punctuation
        if i > 0 and token in string.punctuation and tokens[i-1] in string.punctuation:
            continue
        clean_tokens.append(token)
    
    # Rejoin tokens with proper spacing
    preprocessed_text = ' '.join(clean_tokens)
    
    # Fix spacing around punctuation
    preprocessed_text = re.sub(r'\s+([.,!?])', r'\1', preprocessed_text)
    
    # Capitalize first letter and proper nouns (basic approach)
    preprocessed_text = preprocessed_text.capitalize()
    
    return preprocessed_text

def remove_stopwords(text):
    """
    Remove common stopwords from text
    
    Args:
        text (str): The input text
        
    Returns:
        str: Text with stopwords removed
    """
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
    return ' '.join(filtered_tokens)

def enhance_prompt(text):
    """
    Enhance a prompt by adding common improvement terms
    
    Args:
        text (str): The original prompt
        
    Returns:
        str: Enhanced prompt with additional descriptive terms
    """
    enhancement_terms = [
        "high quality", 
        "detailed", 
        "8k resolution", 
        "professional"
    ]
    
    # Only add enhancement if not already present
    for term in enhancement_terms:
        if term.lower() not in text.lower():
            text += f", {term}"
    
    return text
