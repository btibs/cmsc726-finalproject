# preprocessing for texts downloaded from Project Gutenberg (http://www.gutenberg.org/)

import re
import os

'''
Items to remove:
gutenberg disclaimer
table of contents

'''

ORIG_DIR = "downloads"
PROC_DIR = "processed"
booknames = [d[2] for d in os.walk(ORIG_DIR)][0] # could be better but this should work

for bookname in booknames:
    origfile = file(os.path.join(ORIG_DIR, bookname))
    procfile = file(os.path.join(PROC_DIR, bookname), 'w')

    # remove gutenberg disclaimer
    for line in origfile:
        if line.startwith("***START OF THE PROJECT GUTENBERG EBOOK"):
            pass
        else:
            break

    # we skipped the first part
    # now get to the actual text