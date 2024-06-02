from nltk.tokenize import sent_tokenize, word_tokenize  # Importing tokenization functions from nltk
from bs4 import BeautifulSoup  # Importing BeautifulSoup for HTML parsing
from conditions import isfloat, ispercent  # Importing specific conditions

def extract_text_from_html(html, tag_text_sep="#"):
    """
    Extract text from HTML content, removing script and style elements and joining text with a separator.

    :param html: HTML string to be processed
    :param tag_text_sep: Separator to use between different HTML tags' text content
    :return: Extracted and cleaned text
    """
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style']):
        script.extract()  # Remove script and style elements
    text = soup.get_text(strip=True, separator=tag_text_sep)
    text = ' '.join(text.split())  # Normalize whitespace
    return text

def word_tokenization_ext(text):
    """
    Tokenize the text into words, removing specific unwanted tokens.

    :param text: Text to be tokenized
    :return: List of tokenized words
    """
    words = word_tokenize(text)
    while "#" in words:
        words.remove("#")  # Remove '#' tokens
    return words

def words_rule_based_replacement(words):
    """
    Apply rule-based replacements on the list of words, specifically joining floats and percent signs.

    :param words: List of words to be processed
    :return: List of processed words
    """
    for i in range(len(words)):
        words[i] = words[i].lower()
        if words[i] == '%' and isfloat(words[i-1]):
            words[i-1] = words[i-1] + words[i]  # Join float and percent sign
            words[i] = ''
    # Remove empty strings
    while '' in words:
        words.remove('')

    return words