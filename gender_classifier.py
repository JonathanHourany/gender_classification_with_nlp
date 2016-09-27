import praw
import numpy as np
from collector import Redditor
from collections import Counter
from nltk.corpus import stopwords

class GenderClassifier:
    '''Classifier Redditor Based on Comments. Works with any estimator
    that impliments .fit() and .predict()'''
    
    def __init__(self, estimator, pipeline=False):
        user_agent     = 'NLP Webscrapper 0.4'
        self.pipeline  = pipeline
        self.estimator = estimator
        self.gender = {0: 'Male', 1: 'Female'}
        self.reddit = praw.Reddit(user_agent=user_agent)
    
    def fit(self, X, y):
        if self.pipline:
            pipeline = Pipeline([('vect', CountVectorizer()),
                                 ('tfidf', TfidfTransformer()),
                                 ('clf', self.estimator)])
            self.estimator = pipeline
        self.pipeline.fit(X, y)

    @staticmethod
    def clean_text(self, text, pattern=None):
        if not pattern:
            allowable = (':', ')', '(')           # Punctuation marks used in emoticons
            punctuation  = '[' + ''.join([ch for ch in punctuation if ch not in allowable]) + ']'
            emoticon_pat = '(?<!\:)\)|(?<!\:)\('  # Don't pick up common emoticons
            special_pat  = '[\n]'
            markup_link  = '\[\w+\]|\(http.*\)'   # Markup syntax for hyperlinks
            pattern = "|".join((emoticon_pat, markup_link, special_pat, punctuation))
        text = re.sub(pattern, '', text)
        return text.strip()
    
    def get_comments(self, username):
        '''Not enought time to impliment'''
        pass
    
    def predict(self, username):
        redditor = self.reddit.get_redditor(username)
        comments = [clean_text(comment.body.strip(), set(stopwords.words('english')))
                    for comment in redditor.get_comments(limit=10)]
        predictions = np.asarray([self.estimator.predict([comment]) for comment in comments])
        return self.gender[Counter(predictions.ravel()).most_common(1)[0][0]]
    
    def online_score(self, num_redditors=20):
        '''Not enought time to impliment'''
        pass 