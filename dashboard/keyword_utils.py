import nltk

# Download only standard NLTK resources ('punkt', 'stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from rake_nltk import Rake

def extract_keywords_from_text(text, num_keywords=30, method="both"):
    """
    Extract keywords from text using either 'nltk', 'rake', or 'both'.
    - 'nltk': statistical, single-word keywords.
    - 'rake': phrase-based keywords.
    - 'both': combine both and deduplicate.
    """
    if not text or not isinstance(text, str):
        return []

    result_keywords = set()
    methods = []
    # NLTK method: single-word keywords
    if method in ("nltk", "both"):
        try:
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
            freq_dist = Counter(keywords)
            nltk_keywords = [kw for kw, _ in freq_dist.most_common(num_keywords)]
            methods.append(nltk_keywords)
        except Exception:
            pass  # Fail gracefully, don't break the app

    # RAKE method: phrase extraction
    if method in ("rake", "both"):
        try:
            r = Rake()
            r.extract_keywords_from_text(text)
            rake_keywords = r.get_ranked_phrases()[:num_keywords]
            methods.append(rake_keywords)
        except Exception:
            pass  # Fail gracefully

    # Combine and deduplicate
    for kw_list in methods:
        for kw in kw_list:
            if kw:
                result_keywords.add(kw.strip())
    return list(result_keywords)[:num_keywords]