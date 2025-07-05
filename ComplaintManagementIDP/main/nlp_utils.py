# Same as your nlp.py but as a utility module
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download necessary NLTK resources
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('vader_lexicon', quiet=True)


def preprocess_text(text):
    """Preprocess complaint text"""
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)


def categorize_complaint(text):
    """Categorize complaint and return department"""
    from .models import Department

    categories = {
        "Sanitation": ["garbage", "trash", "waste", "overflowing"],
        "Water": ["water", "leak", "pipe", "drain"],
        "Infrastructure": ["road", "pothole", "bridge", "broken"],
        "Public Safety": ["crime", "dangerous", "theft", "safety"]
    }

    for category, keywords in categories.items():
        if any(keyword in text.lower() for keyword in keywords):
            try:
                department = Department.objects.get(name=category)
                return category, department
            except Department.DoesNotExist:
                pass

    # Default to general department
    try:
        general_dept = Department.objects.get(name="General")
        return "General", general_dept
    except Department.DoesNotExist:
        # Return first available department
        return "General", Department.objects.first()


def assign_priority(text):
    """Assign priority based on keywords and sentiment"""
    high_priority_keywords = ['urgent', 'dangerous', 'critical', 'leaking', 'broken', 'serious']

    for keyword in high_priority_keywords:
        if keyword in text.lower():
            return "HIGH"

    # Sentiment-based priority
    sentiment, sentiment_priority = analyze_sentiment(text)
    return sentiment_priority


def analyze_sentiment(text):
    """Analyze sentiment and return priority"""
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)

    if sentiment['compound'] == 0.0:
        priority = "LOW"
    elif sentiment['compound'] < -0.5:
        priority = "HIGH"
    elif -0.5 <= sentiment['compound'] <= 0.5:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return sentiment, priority