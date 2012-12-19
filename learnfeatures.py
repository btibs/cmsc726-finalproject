# actually use info from feature extraction

from projsettings import *
import cPickle as pickle
import os

# we are doing kmeans stuff

VERBOSE = True

class AveragedPerceptron:
    def __init__(self, author):
        # container class; author only for reference later
        self.author = author
        self.weights = []
        self.bias = 0
    
    # Algorithm 7 in CIML Chapter 3
    def train(self, data, maxIter):
        '''
        Data must be in the format:
        [[x0,x1,...,xn], y]
        where xi is +/-1 feature value and y is +/-1 true label
        '''
        w = [0 for i in range(len(features))]  # weights
        b = 0  # bias
        u = [0 for i in range(len(features))]  # cached weights
        B = 0  # cached bias
        c = 0  # counter
        for _ in range(maxIter):
            for d,(x,y) in enumerate(data):
                # d is the index
                # x is the feature input vector (+/- 1 for each feature)
                # y is the true label (+/- 1)
                sum = 0
                for i in range(len(x)):
                    sum += w[i] + x[i]
                #activation = sum_over_features( w[d], x[d] ) + b
                activation = sum + b
                if y * activation <= 0: # prediction was wrong, update weight vectors
                    w = w + y * x
                    b = b + y
                    u = u + y * c * x
                    B = B + y * c
            c += 1
        
        # return w - u/c
        finalw = []
        for i in range(len(w)):
            w[i] -= u[i] / float(c)
        finalb = b - B / float(c)
        return (finalw, finalb)

class Classifier:
    def __init__(self):
        self.rawfeatures = {"train":[], "test":[]}
        self.vocabulary = {}    # holds list of all words seen in training data
        self.data = {}          # holds data to pass to perceptron
        self.classifiers = {}   # holds classifiers

    def printstats(self):
        # print some pretty stats or something here?
        print "stats"
        
    def supervisedLearn(self):
        # using author info for labeled examples
        if VERBOSE: print "Supervised learning i.e. neural network"

    def unsupervisedLearn(self):
        # TODO: k-means clustering ?
        if VERBOSE: print "Unsupervised learning"

    def classify(self, inputTxt):
        # OVA
        # AVA
        if VERBOSE: print "classifying"

    def loadFeatures(self):
        for n in ["train", "test"]:
            booknames = [d[2] for d in os.walk(os.path.join(FEAT_DIR, n))][0] # could be better but this should work
            for bookname in booknames:
                if VERBOSE: print "loading",bookname,"...",
                ffile = file(os.path.join(FEAT_DIR, n, bookname), 'rb')
                f = pickle.load(ffile)
                ffile.close()
                self.rawfeatures[n].append(f)
                if VERBOSE: print "done."
        
        if VERBOSE: print "\n"
    
    def fixFeatures(self):
        # turn features into a nice data set
        # return data suitable for passing into AveragedPerceptronTrain
        
        for n, books in self.rawfeatures.iteritems():
            if VERBOSE: print "calculating %sing features..."%n,
            vocablist = BookStats()
            for book in books: # book = BookInfo object
                # the worst thing space-wise will be vocabulary countss
                # list of all words in books
                vocablist.add(book.vocabulary)
        
            # TODO remove all stop words
            for wd in ["a", "an", "the"]:
                vocablist.pop(wd)
            
            # TODO we need to normalize or center this around zero? I think?
            # actually bias should take care of this
            self.vocabulary[n] = vocablist
            
            # self.data = {'train': [[[x0,x1,...,xn], y], [...]], 'test':...}
            self.data[n] = []
            
            # calculate some stats about lengths
            # min, max, average, stddev
            for feat, vals in book.features.iteritems():    # sentence, par, etc. lengths
                self.data[n].append(min(vals))
                self.data[n].append(max(vals))
                
                avg = sum(vals) / float(len(vals))
                stddev =  ( sum([(i-avg)**2 for i in vals]) / (len(vals)-1) ) ** (0.5)
                self.data[n].append(avg)
                self.data[n].append(stddev)
            
            if VERBOSE: print "done."
            
        # after that, we add vocabulary to data
        # only add the training data vocabs so that the feature vectors are the same
        if VERBOSE: print "\nadding vocabulary features...",
        for word, val in self.vocabulary['train'].iteritems():
            self.data['train'].append(val)
            self.data['test'].append(self.vocabulary['test'][word])
        
        if VERBOSE:
            print "done.\n"
            print "Training:",len(self.data['train'])
            print "Testing: ",len(self.data['test']), "\n"

if __name__ == "__main__":
    c = Classifier()
    c.loadFeatures()
    c.fixFeatures()