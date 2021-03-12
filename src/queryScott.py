import csv, re, sys
from invertedIndex import tokenize

def error(name):
    '''
    Print out the error and exit the program with -1
    input: name is the name of the error
    '''
    print(name, file=sys.stderr)
    exit(-1)

# Key is the file name and
# the value is the posting lists for that file
def dictionaryStore(fileName):
    # ['Word', 'tf', 'tf-weight^2', 'df', 'idf', 'Posting list']
    try:
        inputFile = open(fileName, 'r')
    except IOError:
        error("Invalid file names")
    csvReader = csv.reader(inputFile, delimiter='\t')
    next(csvReader)

    data = [[row[0], int(row[1]), float(row[2]), int(row[3]), float(row[4]), row[5]] for row in csvReader]
    for i in range(len(data)):
        data[i][-1] = data[i][-1][1:-1].split(', ')
        posting = []
        for j in data[i][-1]:
            posting.append(int(j))
        data[i][-1] = posting

    return data

def find_all(query, s):
    start = 0
    while True:
        start = query.find(s, start)
        if start == -1: return
        yield start
        start += len(s) # use start += 1 to find overlapping matches

def getSubquery(query):
    colon = list(find_all(query, ':'))
    keywordQueries = []
    phraseQueries = []
    if len(colon) > 0:
        if colon[0] > 0:
            for item in query[0 : colon[0]].split(' '):
                if len(item) > 0:
                    phraseQueries.append(item)
        for i in range(0, int(len(colon)), 2):
            keywordQueries.append(query[colon[i]+1 : colon[i + 1]])
            if i != 0:
                for item in query[colon[i-1]+2 : colon[i]-1].split(' '):
                    if len(item) > 0:
                        phraseQueries.append(item)
        if colon[-1]+2 < len(query):
            for item in query[colon[-1]+2 : ].split(' '):
                if len(item) > 0:
                    phraseQueries.append(item)
    else:
        phraseQueries = query.split(' ')

    return keywordQueries, phraseQueries

#make postings objects for comparisons
class Posting:
	def __init__(self,data,target):
		self.target = target
		self.data = data
		self.word = ''
		self.ids = ''
#retrieve posting with word (word and posting list will be returned)
	def lookUp(self):
		for index in self.data:
			if index[0] ==self.target:
				self.word = index[0]
				self.ids = index[2]

	def getPosting(self):
		return [self.word,self.ids]

# Recursively create postings
def createPosting(dictionary, segments):
    postings = []
    for segment in segments:
        if len(segment) != 1:
            if type(segment[0]) == list:
                # Recursive
                postings.append(createPosting(dictionary, segment))
            else:
                posting = Posting(dictionary[segment[0]], tokenize([segment[1]])[0])
                #look up the word
                posting.lookUp()
                #retrieve the posting
                posting = posting.getPosting()
                postings.append(posting)
        else:
            # AND OR NOT words
            postings.append(segment[0])
    return postings

# Make comparisons on postings objects
class Query:
    def __init__(self,posting_1,posting_2):
        self.posting_1 = posting_1
        self.posting_2 = posting_2
        self.p1_length = len(posting_1[1]) 
        self.p2_length = len(posting_2[1]) 


    def fetch(self,term):
        term=term
        return []
    #  From text
    def zoneScore(self):
        scores = [] #entry for each document
        g = 1
        pointer_1 = 0
        pointer_2 = 0
        while pointer_1< self.p1_length and pointer_2 < self.p2_length:
            #case for 2 postings that match
            if self.posting_1[1][pointer_1] ==self.posting_2[1][pointer_2]:

                scores.append(weightedZone(pointer_1,pointer_2,g))
                pointer_1 +=1
                pointer_2 +=1
            else:
                pointer_1 +=1
                pointer_2 +=1
        return scores

    def cosineScore(self,query,N,k):
        length = []
        scores = []
        topK = []
        for i in N:
            score.append(['doc',0])
            length.append(0)
        for term in query:
            weight_t =0
            postings_list =fetch(term)
            scores[term]= scores[term][1]+ weight_t
        for doc in length:
            scores[doc] = scores[doc][1]/length[doc][1]
            scores = scores.sort()
        for i in range(k):
            topK.append(scores[i])
        return topK



# Recursively do the booleans
def getPostings(postings):
    for i in range(len(postings)-1):
        if type(postings[i]) == str:
            # If the left side is not finalized, recursively do it
            if type(postings[i-1][0]) == list:
                postings[i-1] = getPostings(postings[i-1])[-1]

            # If the right side is not finalized, recursively do it
            if type(postings[i+1][0]) == list:
                postings[i+1] = getPostings(postings[i+1])[-1]
            boolean = Boolean(postings[i-1],postings[i+1])
            if postings[i] == 'AND':
                #find intersection
                postings[i+1] = boolean.getAnd()
            elif postings[i] == 'OR':
                #find union
                postings[i+1] = boolean.getOr()
            elif postings[i] == 'AND NOT':
                #find the AND NOT
                postings[i+1] = boolean.getAndNot()
    return postings

if __name__ == "__main__":
    # Get the arguments and validate the number
    arguments = sys.argv
    if len(arguments) != 4:
        error("Invalid arguents")

    directory = arguments[1]
    number = int(arguments[2])
    query = arguments[3]

    data = dictionaryStore(directory+'index.tsv')
    for i in data:
        print(i)
        print('!')

    phraseQueries, keywordQueries = getSubquery(query)
    print('phrase:', phraseQueries)
    print('keyword:', keywordQueries)

    print('\nDone\n')
