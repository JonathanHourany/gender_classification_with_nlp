import re
import praw
import pandas as pd
from string import punctuation


class Redditor:
    def __init__(self, username, sex, age=None, comments={}, subreddits=set()):
        self.username = username
        self.sex = sex
        self.age = age
        self.comments = comments
        self.subreddits = subreddits

    @classmethod
    def from_post_title(cls, submission_obj, reddit_session, comment_limit=200):
        '''Automatically contruct a redditor from a post link

        Parameters
        -----------
        cls:            A class object
        submission_obj: PRAW Submission Object
        reddit_session: Instance of a PRAW Reddit Session 

        Returns
        -------
        redditor:   Instance of Redditor
        '''
        sex, age, *_ = submission_obj.title.lower().split('/')
        age = int(age)
        username = submission_obj.author
        redditor = cls(username, sex, age)
        try:
            r = reddit_session.get_redditor(username)
        except:
            pass
        comments_obj = r.get_comments(limit=comment_limit)
        redditor.subreddits, redditor.comments = redditor.process_comment(comments_obj)
        return redditor

    @classmethod
    def from_flair(cls, submission_obj, reddit_session):
        pass

    @staticmethod
    def process_comment(comments_obj):
        '''Parses a comments_obj for relavent data

        Parameters
        -----------
        comments_obj: PRAW Comment Object

        Returns
        -------
        subreddits: list,
            A list of strings containing subreddits comments were made in

        comments: tuple, (comment_id, string)
            A tuple of comments and their reddit designated ids
        '''
        comments = []
        subreddits = []
        for comment in comments_obj:
            subreddits.append(comment.subreddit.display_name)
            comments.append((comment.fullname, comment.body.strip()))
        return subreddits, comments

    @staticmethod
    def process_text(self, comment):
        comment = self._clean_text(comment)
        return comment.lower()

    @staticmethod
    def _clean_text(self, text, pattern):
        allowable = (':', ')', '(')           # Punctuation marks used in emoticons
        punctuation  = '[' + ''.join([ch for ch in punctuation if ch not in allowable]) + ']'
        emoticon_pat = '(?<!\:)\)|(?<!\:)\('  # Don't pick up common emoticons
        special_pat  = '[\n]'
        markup_link  = '\[\w+\]|\(http.*\)'   # Markup syntax for hyperlinks
        pattern = "|".join((emoticon_pat, markup_link, special_pat, punctuation))
        text = re.sub(pattern, '', text)
        return text.strip()
        self._comments = dict(comments)

    @property
    def username(self):
        '''Getter for username attribute'''
        return self._username

    @username.setter
    def username(self, username):
        '''Setter for username attribute. 

        Parameters
        ----------
        username: str

        Exceptions
        -----------
        Raises ValueError if parameters do not match reddit's restriction on usernames
        '''
        if not re.search('[a-zA-Z0-9\_\-]', str(username)):
            print("Raise: ", username)
            raise ValueError('{username} is not a valid reddit username'.format(username))
        self._username = str(username).lower()

    @property
    def sex(self):
        '''Getter for sex attribute'''
        return self._sex

    @sex.setter
    def sex(self, sex):
        '''Setter for sex attribute

        Parameters
        ----------
        sex: str

        Exceptions
        -----------
        Raises ValueError if parameters are not m or f
        '''
        sex = sex.lower()
        if sex not in ('m', 'f'):
            raise ValueError("Sex can only be 'm' or 'f'")
        gender = {'m': 0, 'f': 1}
        self._sex = gender[sex]

    @property
    def subreddits(self):
        '''Getter for subbreddits attribute'''
        return self._subreddits

    @subreddits.setter
    def subreddits(self, subreddits):
        '''Setter for subreddits attribute. Stores values as set()

        Parameters
        ----------
        subreddits: list
        '''
        self._subreddits = set(subreddit.lower() for subreddit in subreddits)

    @property
    def comments(self):
        '''Getter for comments attribute'''
        return self._comments

    @comments.setter
    def comments(self, comments):
        self._comments = dict(comments)

    def __str__(self):
        return self.username

    def __len__(self):
        return len(self.comments)


def main():
    # Messages to report changes in major phases
    start_msg    = '\n---- Reddit Mining Started ----\n'
    mining_msg   = '- Mining subreddits for posts'
    parse_msg    = '- Parsing data...'
    writeout_msg = '- Writting data to CSV file'
    user_agent   = 'NLP Webscrapper 0.4'

    # DataFrame columns
    df_user_columns = ['uid', 'Username', 'Sex', 'Age']
    df_comment_columns = ['uid', 'Comment_id', 'Comment']
    df_subreddits_columns = ['uid', 'Subreddit']

    # List of user features to map to dict
    user_features = ['Username', 'Sex', 'Age']

    # List of subreddits to data mine
    mineable_subreddits = ['progresspics']

    # Location of database tables
    users_tbl_path = 'test/users_df.csv'
    comments_tbl_path = 'test/comments_df.csv'
    subreddits_tbl_path = 'test/subreddits_df.csv'

    redditors = []
    db_exists = False
    count = 0   # Tracks count of posts processed. Purely for print outs.

    try:
        # Assume these tables already exsist and load them.
        users_df = pd.read_csv(users_tbl_path)
        comments_df = pd.read_csv(comments_tbl_path)
        subreddits_df = pd.read_csv(subreddits_tbl_path)
        user_id = users_df['uid'].max()
        db_exists = True
        collected_users = set(users_df['Username'])
    except IOError:
        # Raised if the tables don't exsist, so start the UID at somewhere
        user_id = 100
        collected_users = set()

    # Init and connect with Reddit API, start program
    reddit = praw.Reddit(user_agent=user_agent)
    print(start_msg)
    print(mining_msg)

    for subreddit in mineable_subreddits:
        print(' ~ Mining Subreddit: {}'.format(subreddit))
        posts = reddit.get_subreddit(subreddit)
        for submission in posts.get_hot(limit=400):
            try:
                redditor = Redditor.from_post_title(submission, reddit, comment_limit=200)
                if redditor.username not in collected_users:
                    redditors.append(redditor)
            except (AttributeError, ValueError):
                # Value errors raised by the Redditor Class going to be because of
                #  links that don't have the correct formatting (e.g. sticky posts)
                #  or when the user has made no comments. When these occur,
                #  its fine to just drop the submission
                pass
            except:
                # For all other exceptions, break out of the loop and attempt
                #  to save what data has ben collected
                break
            print('  ~ Processing User -- # {0}: '.format(count))
            count += 1

    # When Mining is complete, save data to appropriate files
    print(parse_msg)

    # Data is saved in Dict's and passed to pandas DataFrame. Keys
    # represent column headers in the DataFrame/CSV file
    user_dict = {'uid': []}
    comments_dict = {'uid': [], 'Comment_id': [], 'Comment': []}
    subreddits_dict = {'uid': [], 'Subreddit': []}
    for redditor in redditors:
        user_id += 1
        comments_dict['Comment_id'].extend(list(redditor.comments.keys()))
        comments_dict['Comment'].extend(list(redditor.comments.values()))
        comments_dict['uid'].extend([user_id] * len(redditor.comments))
        user_dict['uid'].append(user_id)
        subreddits_dict['uid'].extend([user_id] * len(redditor.subreddits))
        subreddits_dict['Subreddit'].extend(list(redditor.subreddits))
        for feature in user_features:
            user_dict.setdefault(feature, []).append(redditor.__getattribute__(feature.lower()))

    print(writeout_msg)

    if not db_exists:
        user_tbl = pd.DataFrame(user_dict, columns=df_user_columns)
        comments_tbl = pd.DataFrame(comments_dict, columns=df_comment_columns)
        subreddits_tbl = pd.DataFrame(subreddits_dict, columns=df_subreddits_columns)
    else:
        user_tbl = users_df.append(pd.DataFrame(user_dict,
                                   columns=df_user_columns))
        comments_tbl = comments_df.append(pd.DataFrame(comments_dict,
                                          columns=df_comment_columns))
        subreddits_tbl = subreddits_df.append(pd.DataFrame(subreddits_dict,
                                              columns=df_subreddits_columns))

    user_tbl.to_csv(users_tbl_path, index=False)
    comments_tbl.to_csv(comments_tbl_path, index=False)
    subreddits_tbl.to_csv(subreddits_tbl_path, index=False)

if __name__ == '__main__':
    main()
