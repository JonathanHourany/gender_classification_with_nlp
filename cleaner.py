import re
import pandas as pd
from textblob import TextBlob
from string import punctuation
from nltk.corpus import stopwords

def clean_text(text, stopwords=[], pattern=None):
    if not pattern:
        allowable = (':', ')', '(')           # Punctuation marks used in emoticons
        punct     = '[' + ''.join([ch for ch in punctuation if ch not in allowable]) + ']'
        emoticon_pat = '(?<!\:)\)|(?<!\:)\('  # Don't pick up common emoticons
        special_pat  = '[\n]'
        markup_link  = '\[\w+\]|\(http.*\)'   # Markup syntax for hyperlinks
        hyperlinks   = '(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?'
        pattern = "|".join((emoticon_pat, hyperlinks, markup_link, special_pat, punct))

    text = re.sub(pattern, ' ', text)
    text = TextBlob(text).words
    text = ' '.join(word for word in text.lower() if word not in stopwords)
    return text.strip()


def main():
    # Table Inputs. These should be paths from the CLi but I didn't have
    # time to implement that
    comments_tbl_path = 'test/comments_df.csv'
    writeout_pth = 'test/cleaned_comments_df.csv'

    stopwords_set = set(stopwords.words('english'))
    stopwords_set |= set(['http', 'www', 'like', 'get', 'one', 'would', 'time', 'go', 'going'])
    df = pd.read_csv(comments_tbl_path)
    df['Comment'] = [clean_text(text=str(comment), stopwords=stopwords_set) for comment in df['Comment']]
    df.to_csv(writeout_pth)

if __name__ == '__main__':
     main() 
