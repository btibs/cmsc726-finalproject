# actually use info from feature extraction

from projsettings import *
import cPickle as pickle
import os
import random

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
        nfeats = len(data[0][0])
        
        w = [0 for i in range(nfeats)]  # weights
        b = 0  # bias
        u = [0 for i in range(nfeats)]  # cached weights
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
                    for i in range(len(x)):
                        w[i] = w[i] + y * x[i]      # update weights
                        u[i] = u[i] + y * c * x[i]  # update cached weights
                    b = b + y                       # update bias
                    B = B + y * c                   # update cached bias    
            c += 1
        
        # return w - u/c
        finalw = [0 for i in w]
        for i in range(len(w)):
            finalw[i] -= u[i] / float(c)
        finalb = b - B / float(c)
        self.weights = finalw
        self.bias = finalb
        return (finalw, finalb)

class Classifier:
    def __init__(self):
        self.rawfeatures = {"train":[], "test":[]}
        self.vocabulary = {"train":[], "test":[]}    # holds list of all words seen in training data
        self.authors = {"train":[], "test":[]}       # holds list of authors
        self.books = {"train":[], "test":[]}
        self.data = {"train":[], "test":[]}          # holds data to pass to perceptron
        self.classifiers = {}   # holds classifiers
        
    def supervisedLearn(self):
        # using author info for labeled examples
        if VERBOSE: print "supervised learning i.e. neural network"
        
        # now we make all the classifiers and train them all
        maxIter = 50
        
        for a in self.authors['train']:
            if VERBOSE: print "training classifier for",a,"...",
            self.classifiers[a] = AveragedPerceptron(a)
            
            # train them
            alldata = []    # format [ [[x0,x1,...,xn], y], [...], ... ] for each book; y = +-1 author
            for i, data in enumerate(self.data['train']):
                isauth = 1 if a == self.authors['train'][i] else -1
                alldata.append( [ data, isauth ] )
            
            self.classifiers[a].train(alldata, maxIter)
            print "\nbias:",self.classifiers[a].bias,"weights:",self.classifiers[a].weights[:10],
            print "maxw:",max(self.classifiers[a].weights),"minw:",min(self.classifiers[a].weights)
            if VERBOSE: print "done."
            
        # print to file
        if VERBOSE: print "pickling to file...",
        f = file("classifierpickle.txt", "wb")
        pickle.dump(self.classifiers, f)
        f.close()
        if VERBOSE: print "done."

    def testOVA(self):
        if VERBOSE: print "testing OVA\n",self.classifiers.keys()
        # test input on each classifier, the positive one wins (ties broken randomly)
        results = []
        for i, x in enumerate(self.data['test']):
            if VERBOSE: print "testing for author",self.authors['test'][i],"-",self.books['test'][i]
            acts = []
            scores = []
            for k,c in self.classifiers.iteritems():
                # compute activation for this data with this classifier
                #activation = sum_over_features( w[d], x[d] ) + b
                sum = 0
                for i in range(len(x)):
                    sum += c.weights[i] + x[i]
                activation = sum + c.bias
                acts.append(activation)
                scores.append(activation >= 0)
            if VERBOSE:
                #print "activations:",acts,"\nscores:",scores
                print "author".ljust(25),"activation\tscore"
                s = zip(self.classifiers.keys(),acts,scores)
                s.sort(key=lambda k:k[1])   # sort on activations
                for (a,ac,sc) in s:
                    print a.ljust(25),ac,"\t",sc
            
            # find positive examples
            positives = [i for (i,v) in enumerate(scores) if v==True]
            if len(positives) == 0:
                if VERBOSE: print "no positives found!"
                # pick one with highest activation?
                idx = acts.index(max(acts))
                results.append(self.classifiers.keys()[positives[idx]])
            elif len(positives) == 1:
                if VERBOSE: print "success: one classification found"
                results.append(self.classifiers.keys()[positives[0]])
            else:
                if VERBOSE: print "multiple classifications found, choosing random"#highest activation"
                idx = random.randint(0,len(positives)-1)
                results.append(self.classifiers.keys()[positives[idx]])
                # pick one with highest activation?
                #idx = acts.index(max(acts))
                #results.append(self.classifiers.keys()[positives[idx]])
            if VERBOSE: print "classified as:",results[-1],"\n"
        return results
    
    def loadClassifiers(self):
        if VERBOSE: print "loading classifiers...",
        f = file("classifierpickle.txt", "rb")
        self.classifiers = pickle.load(f)
        f.close()
        print "done."
        
    def printClassifiers(self):
        for k,v in self.classifiers.iteritems():
            print k
            print "Bias:",v.bias
            print "Weights:",v.weights[:20]
            print

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
        
        self.fixFeatures()
    
    def fixFeatures(self):
        # turn features into a nice data set
        # return data suitable for passing into AveragedPerceptronTrain
        
        # get vocabulary list
        vocab = []
        for book in self.rawfeatures['train']:
            vocab += book.vocabulary.keys()
        
        # TODO remove all stop words
        for wd in ["a", "an", "the"]:
            vocab.remove(wd)
        
        for n, books in self.rawfeatures.iteritems():
            if VERBOSE: print "calculating %sing features..."%n,
            
            # self.data = {'train': [[[x0,x1,...,xn], y], [...]], 'test':...}
            self.data[n] = []
            
            for book in books: # book = BookInfo object
                # calculate some stats about lengths
                # min, max, average, stddev
                bdata = []
                for feat, vals in book.features.iteritems():    # sentence, par, etc. lengths
                    bdata.append(min(vals))
                    bdata.append(max(vals))
                    
                    avg = sum(vals) / float(len(vals))
                    stddev =  ( sum([(i-avg)**2 for i in vals]) / (len(vals)-1) ) ** (0.5)
                    bdata.append(avg)
                    bdata.append(stddev)
                
                # now add vocabulary
                for wd in vocab:
                    bdata.append(book.vocabulary[wd])
                
                # now add punctuation
                for _,p in book.punctuation.iteritems():
                    bdata.append(p)
                
                # now add bdata to data
                self.data[n].append(bdata)
                self.authors[n].append(book.author)
                self.books[n].append(book.title)
            
            if VERBOSE: print "done."
            
        if VERBOSE:
            print "Training:",len(self.data['train'][0])
            print "Testing: ",len(self.data['test'][0]), "\n"
    
    def printStats(self):
        print "stats"
        # actually do things like vocab histogram or s/t

if __name__ == "__main__":
    c = Classifier()
    c.loadFeatures()
    #c.supervisedLearn()
    c.loadClassifiers()
    c.printClassifiers()
    c.testOVA()
    c.printStats()