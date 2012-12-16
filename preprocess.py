# preprocessing for texts downloaded from Project Gutenberg (http://www.gutenberg.org/)

import re
import os

from projsettings import *

'''
Items to remove:
gutenberg disclaimer
table of contents

'''

def processTexts():
    booknames = [d[2] for d in os.walk(ORIG_DIR)][0] # could be better but this should work
    for bookname in booknames:
        origfile = file(os.path.join(ORIG_DIR, bookname))
        procfile = file(os.path.join(PROC_DIR, bookname), 'w')
        
        # stops
        pastDisclaimer = False
        pastTOC = False
        
        for line in origfile:
            # remove gutenberg disclaimer
            if not pastDisclaimer:
                if line.startwith("*** START OF THIS PROJECT GUTENBERG EBOOK") or\
                    line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK") or\
                    line.startswith("*END THE SMALL PRINT! FOR PUBLIC DOMAIN ETEXTS"):
                    pastDisclaimer = True
            
            # skip TOC
            elif not pastTOC:
                if line.contains("Contents"):
                    pass
        # quitting here, not formatted consistently enough to warrant this

def processChaucer():
    '''because why not have a special function'''
    origfile = file(os.path.join(PROC_DIR, 'Chaucer, Geoffrey - The Canterbury Tales and Other Poems.txt'), 'r')
    
    print origfile
    newfile = file(os.path.join(PROC_DIR, 'Chaucer, Geoffrey - The Canterbury Tales and Other Poems.txt.2'), 'w')
    
    pats = [[r'^(.*)(\s\s\*.*)$', [1]],             # match notes at end of sentence
            [r'^(.*)(\s{3,}.*\*)$', [1]],            # match notes continuing on next line
            [r'^(.*)(\s?\<\d+\>\s?)(.*)$', [1,3]],  # match references
           ]
    fnre = re.compile(r'^\d+\. ')           # match footnotes
    repats = [(re.compile(p), "\\"+"\\".join([str(vv) for vv in v])) for (p,v) in pats]
    
    inFootnotes = False
    lastLineBlank = False
    
    print "okay go"
    for line in origfile:
        # check if title
        if line.startswith("   "):          # is a title, skip
            continue
        
        # check if matches re's
        for (r, p) in repats:
            line = r.sub(p, line)           # remove footnotes / endnotes
            
        line = line.replace('*', '')        # remove asterisks
        
        line = line.strip()                 # remove extra whitespace on end
        if line == '':                      # blank line, skip
            if inFootnotes and lastLineBlank:   # no longer in footnotes if two blank lines in a row
                inFootnotes = False
            lastLineBlank = True
            continue
        else:
            lastLineBlank = False
            
        # skip footnotes
        if line.startswith("Notes to the ") or fnre.match(line) is not None:
            inFootnotes = True
        if inFootnotes:
            continue
        
        # if we got here -- hooray, we have a line with text on it
        newfile.write(line + "\n")
        
    print "closing"
    origfile.close()
    newfile.close()

def convertProcessedToFeatures():
    booknames = [d[2] for d in os.walk(PROC_DIR)][0]
    for bookname in booknames:
        procfile = file(os.path.join(PROC_DIR, bookname), 'r')
        featfile = file(os.path.join(FEAT_DIR, bookname+".features"), 'w')

if __name__ == "__main__":
    #processTexts()
    #convertProcessedToFeatures()
    processChaucer()