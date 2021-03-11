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
    phaseQueries = []
    if len(colon) > 0:
        if colon[0] > 0:
            for item in query[0 : colon[0]].split(' '):
                if len(item) > 0:
                    phaseQueries.append(item)
        for i in range(0, int(len(colon)), 2):
            keywordQueries.append(query[colon[i]+1 : colon[i + 1]])
            if i != 0:
                for item in query[colon[i-1]+2 : colon[i]-1].split(' '):
                    if len(item) > 0:
                        phaseQueries.append(item)
        if colon[-1]+2 < len(query):
            for item in query[colon[-1]+2 : ].split(' '):
                if len(item) > 0:
                    phaseQueries.append(item)
    else:
        phaseQueries = query.split(' ')

    return keywordQueries, phaseQueries

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
class Boolean:
	def __init__(self,posting_1,posting_2):
		self.posting_1 = posting_1
		self.posting_2 = posting_2
		self.p1_length = len(posting_1[1]) 
		self.p2_length = len(posting_2[1]) 

#  From text
	def getAnd(self):
		pointer_1 = 0
		pointer_2 = 0
		answer = ['', []]
		while pointer_1< self.p1_length and pointer_2 < self.p2_length:
			if self.posting_1[1][pointer_1] ==self.posting_2[1][pointer_2]:
				answer[1].append(self.posting_1[1][pointer_1])
				pointer_1 +=1
				pointer_2 +=1
			elif self.posting_1[1][pointer_1] <self.posting_2[1][pointer_2]:
				pointer_1 +=1
			else:
				pointer_2 +=1
		return answer

# From text
	def getOr(self):
		pointer_1 = 0
		pointer_2 = 0
		answer = ['', []]
		while pointer_1<self.p1_length and pointer_2 < self.p2_length:
			if self.posting_1[1][pointer_1] ==self.posting_2[1][pointer_2]:
				answer[1].append(self.posting_1[1][pointer_1])
				pointer_1 +=1
				pointer_2 +=1
			elif self.posting_1[1][pointer_1] < self.posting_2[1][pointer_2]:
				answer[1].append(self.posting_1[1][pointer_1])
				pointer_1 +=1
			else:
				answer[1].append(self.posting_2[1][pointer_2])
				pointer_2 +=1
		#find postings for size mis-matches
		while pointer_1<self.p1_length:
			answer[1].append(self.posting_1[1][pointer_1])
			pointer_1 +=1
		while pointer_2<self.p2_length:
			answer[1].append(self.posting_2[1][pointer_2])
			pointer_2 +=1
		return answer

# From text
	def getAndNot(self):
		pointer_1 = 0
		pointer_2 = 0
		answer = ['', []]
		while pointer_1< self.p1_length and pointer_2 < self.p2_length:
			if self.posting_1[1][pointer_1] ==self.posting_2[1][pointer_2]:
				pointer_1 +=1
				pointer_2 +=1
			elif self.posting_1[1][pointer_1] <self.posting_2[1][pointer_2]:
				answer[1].append(self.posting_1[1][pointer_1])
				pointer_1 +=1
			else:
				pointer_2 +=1

		return answer

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

    phaseQueries, keywordQueries = getSubquery(query)
    print('phase:', phaseQueries)
    print('keyword:', keywordQueries)
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
