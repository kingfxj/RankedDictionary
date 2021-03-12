import csv, re, sys
from invertedIndex import tokenize
from math import log


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
    # ['tf', 'tf-weight^2', 'df', 'idf', 'Posting list']
    try:
        inputFile = open(fileName, 'r')
    except IOError:
        error("Invalid file names")
    csv.field_size_limit(sys.maxsize)
    csvReader = csv.reader(inputFile, delimiter='\t')
    next(csvReader)

    # Load thetsv file into a list of lists
    # the sublists are [term, tf, tf-weight squared, df, idf, posting list dictionary{doc_id: [positions]}]
    data = {}
    for row in csvReader:
        data[row[0]] = [int(row[1]), float(row[2]), int(row[3]), float(row[4]), row[5]]
    # data = {row[0]: [int(row[1]), float(row[2]), int(row[3]), float(row[4]), row[5]]} for row in csvReader

    # Update the doc ID to int in each posting list
    for key in data.keys():
        dictionary = {}
        postings = data[key][-1][1:-2].split('), ')
        for doc in postings:
            dictionary[int(doc[1:doc.index(',')])] = []
            position = doc[doc.index('[')+1: -1].split(', ')
            for position in doc[doc.index('[')+1: -1].split(', '):
                dictionary[int(doc[1:doc.index(',')])].append(int(position))
        data[key][-1] = dictionary

    # for i in range(len(data)):
    #     dictionary = {}
    #     postings = data[i][-1][1:-2].split('), ')
    #     for doc in postings:
    #         dictionary[int(doc[1:doc.index(',')])] = []
    #         position = doc[doc.index('[')+1: -1].split(', ')
    #         for position in doc[doc.index('[')+1: -1].split(', '):
    #             dictionary[int(doc[1:doc.index(',')])].append(int(position))
    #     data[i][-1] = dictionary

    return data


# Find all occurences of s inside sting query
def find_all(query, s):
    start = 0
    while True:
        start = query.find(s, start)
        if start == -1: return
        yield start
        start += len(s) # use start += 1 to find overlapping matches


# Get the keyword queries and the phrase queries
def getSubquery(query):
    colon = list(find_all(query, ':'))
    if len(colon) % 2 != 0:
        error('Invalid query')

    keywordQueries = []
    phraseQueries = []

    # If there are phrase queries
    if len(colon) > 0:
        if colon[0] > 0:
            # There are keywords before the first phrase
            for item in query[0 : colon[0]].split(' '):
                if len(item) > 0:
                    keywordQueries.append(item)
        for i in range(0, int(len(colon)), 2):
            phraseQueries.append(query[colon[i]+1 : colon[i + 1]])
            if i != 0:
                # Add keywords one by one
                for item in query[colon[i-1]+2 : colon[i]-1].split(' '):
                    if len(item) > 0:
                        keywordQueries.append(item)
        if colon[-1]+2 < len(query):
            # There are keyword at the end of the queries
            for item in query[colon[-1]+2 : ].split(' '):
                if len(item) > 0:
                    keywordQueries.append(item)
    else:
        # Only keywords in the queries
        keywordQueries = query.split(' ')

    return keywordQueries, phraseQueries


def cosineScore(keywordQuery, data):
    # {term: [tf, tf-weightSquared, df, idf, posting list]}
    # lnc.btn
    scores = []
    lengths = []
    for i in range(len(keywordQuery)):
        term = keywordQuery[i]
        score = {}
        length = {}
        if term in data.keys():
            for ID in data[term][4].keys():
                documentWeight = 1 + log(data[term][0])
                queryWeight = data[term][3]
                score[ID] = documentWeight * queryWeight
                length[ID] = []
            # print(score, length)
            scores.append(score)
            lengths.append(length)
    return scores, lengths


# Make postings objects for comparisons
class Posting:
	def __init__(self,data,target):
		self.target = target
		self.data = data
		self.word = ''
		self.ids = ''

    # Retrieve posting with word (word and posting list will be returned)
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

                # scores.append(weightedZone(pointer_1,pointer_2,g))
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
            scores.append(['doc',0])
            length.append(0)
        for term in query:
            weight_t =0
            # postings_list = self.fetch(term)
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
            # boolean = Query(postings[i-1],postings[i+1])
            # if postings[i] == 'AND':
            #     #find intersection
            #     postings[i+1] = boolean.getAnd()
            # elif postings[i] == 'OR':
            #     #find union
            #     postings[i+1] = boolean.getOr()
            # elif postings[i] == 'AND NOT':
            #     #find the AND NOT
            #     postings[i+1] = boolean.getAndNot()
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
        print(data[i])

    keywordQueries, phraseQueries = getSubquery(query)
    print('phrase:', phraseQueries)
    print('keyword:', keywordQueries)

    scores, lengths = cosineScore(keywordQueries, data)
    # for i in scores:
    #     for j in sorted(i.items()):
    #         print(j)
    #     print()

    # print('\n\n')
    # for i in lengths:
    #     for j in sorted(i.items()):
    #         print(j)

    # # Put NOT and AND together to use AND NOT
    # segments = []
    # for i in range(len(segmentsCopy)):
    #     if segmentsCopy[i] == ['AND']:
    #         if i+1 < len(segmentsCopy) and segmentsCopy[i+1] == ['NOT']:
    #             segments.append(['AND NOT'])
    #         else:
    #             segments.append(segmentsCopy[i])
    #     elif segmentsCopy[i] != ['NOT']:
    #         segments.append(segmentsCopy[i])
    # print('query segments:', segments)

    # # dictionary, title = dictionaryStore(fileNames)
    # postings = createPosting(dictionary, segments)
    # print('postings:', postings)

    # postings = getPostings(postings)

    # print(postings[-1][1])
    print('\nDone\n')
