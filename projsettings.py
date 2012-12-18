# variables for project

ORIG_DIR = "downloads"
PROC_DIR = "processed"
FEAT_DIR = "features"

class BookInfo():
    # TODO this is messy
    separators = {  'phrase': [
                        ',', ';', ':','--',"'", '"',
                        '(', ')', '{', '}', '[', ']'
                    ],
                    'sent': ['.', '!', '?'],
                }
    punct = [   # sentence
                '.', '!', '?',
                
                # phrase
                ',', ';', ':','--',"'", '"',
                '(', ')', '{', '}', '[', ']',
                
                # other
                ' ','\\', '/', '<', '>', '-', # single hyphen = word
            ] # standard punctuation symbols
    
    # isn't there a regex class for this
    # whitespace \s
    # digits \d
    # non-alphanumeric \W
    # this will split by whitespace and punctuation:
    #re.findall(r"[\w']+|[.,!?;]", "Hello, I'm a string!")
    
    def __init__(self, author="", title=""):
        self.author = author
        self.title = title
        self.features = {   'sent_len': [],
                            'par_len': [],
                            'word_len': [],
                            'phrase_len': [],
                        }
        self.punctuation = dict(zip(BookInfo.punct, [0 for i in BookInfo.punct]))
        self.vocabulary = BookStats()
    
    def update(self, feat, flen):
        if flen != 0:
            self.features[feat+'_len'].append(flen)

class BookStats(dict):
    # return 0 if key not in dictionary; else value
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)