# extract features from books, pickle, store in files

import os
import cPickle as pickle
from projsettings import *
import re

def extractAll():
    r = '[' + '|'.join(BookInfo.punct) + ']|\w+'
    r = r.replace('(', '\(').replace(')', '\)').replace('-', '\-')  # escape regex characters TODO do this the not-dumb way
    
    wordsplit = re.compile(r)
    
    booknames = [d[2] for d in os.walk(PROC_DIR)][0] # could be better but this should work
    for bookname in booknames:
        print "processing",bookname,"...",
        auth, title = bookname.split(" - ")
        inf = BookInfo(auth, title)
        
        # open book file
        procfile = file(os.path.join(PROC_DIR, bookname))
        
        # read book
        # we want to track words, phrases/clauses, sentences, paragraphs
        flens = {'phrase':0, 'sent':0, 'par':0}
        for line in procfile:
            line = line.strip() # remove spaces and newlines at beginning and end of lines
            if len(line) == 0: # blank line
                # update all word levels
                for f, l in flens.iteritems():
                    inf.update(f, l)
                    flens[f] = 0
            
            else:   # line contains words
                words = wordsplit.findall(line)
                
                # put words into vocabulary
                for i, wd in enumerate(words):
                    if wd in BookInfo.punct:
                        inf.punctuation[wd] += 1
                        
                        # check if punctuation signifies end of something
                        if wd in BookInfo.separators['sent']:
                            if wd == '.':
                                # check if not abbreviation
                                # TODO make better (things like i.e., e.g. ignored; if at end of sentence is messed up)
                                abbr = False
                                if i > 0:
                                    if words[i-1].lower() in ['mr', 'mrs', 'dr', 'ms', 'etc', 'et', 'al']:
                                        abbr = True
                                if abbr:
                                    pass
                                else:
                                    inf.update('sent', flens['sent'])
                                    flens['sent'] = 0
                            else:
                                inf.update('sent', flens['sent'])
                                flens['sent'] = 0
                                inf.update('phrase', flens['phrase'])
                                flens['phrase'] = 0
                        
                        elif wd in BookInfo.separators['phrase']:
                            # ignore possessive "'s"
                            if wd == "'" and i<len(words)-1 and words[i+1] == 's':
                                pass
                            else:
                                inf.update('phrase', flens['phrase'])
                                flens['phrase'] = 0
                    
                    else:   # is an actual word
                        inf.vocabulary[wd.lower()] += 1
                        
                        # increment word count
                        # ignore if possessive "'s"
                        if wd == 's' and i > 0 and words[i-1] == "'":
                            pass
                        else:   # actual word
                            inf.update("word", len(wd))
                            for f,l in flens.iteritems():
                                flens[f] += 1
        
        # final update
        for f, l in flens.iteritems():
            inf.update(f, l)
            flens[f] = 0
        procfile.close()
        
        # write book info to file
        print "writing to file ...",
        featfile = file(os.path.join(FEAT_DIR, bookname), 'wb')
        pickle.dump(inf, featfile, pickle.HIGHEST_PROTOCOL)
        featfile.close()
        print "done."

# command line
if __name__ == "__main__":
    extractAll()