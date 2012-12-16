# extract features from books, pickle, store in files

import os
from projsettings import *

def extractAll():
    booknames = [d[2] for d in os.walk(PROC_DIR)][0] # could be better but this should work
    for bookname in booknames:
        procfile = file(os.path.join(PROC_DIR, bookname))
        featfile = file(os.path.join(FEAT_DIR, bookname), 'w')
        
        procfile.close()
        featfile.close()


# command line
if __name__ == "__main__":
    extractAll()