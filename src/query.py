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

    # Load the tsv file into a dictionary
    # the sublists are {term: tf, tf-weight squared, df, idf, posting list dictionary{doc_id: [positions]}]
    data = {}
    for row in csvReader:
        data[row[0]] = [int(row[1]), float(row[2]), int(row[3]), float(row[4]), row[5]]

    # Update the doc ID to int in each posting list
    for key in sorted(data.keys()):
        dictionary = {}
        postings = data[key][-1][1:-2].split('), ')
        for doc in postings:
            dictionary[int(doc[1:doc.index(',')])] = []
            position = doc[doc.index('[')+1: -1].split(', ')
            for position in doc[doc.index('[')+1: -1].split(', '):
                dictionary[int(doc[1:doc.index(',')])].append(int(position))
        data[key][-1] = dictionary

    return data


def normalizedStore(fileName):
    # ['id', 'score']
    try:
        inputFile = open(fileName, 'r')
    except IOError:
        error("Invalid file names")
    csv.field_size_limit(sys.maxsize)
    csvReader = csv.reader(inputFile, delimiter='\t')
    next(csvReader)

    # Load thetsv file into a list of lists
    # the sublists are [term, tf, tf-weight squared, df, idf, posting list dictionary{doc_id: [positions]}]
    normalized = {}
    for row in csvReader:
        normalized[int(row[0])] = float(row[1])

    return normalized


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


def cosineScore(keywordQuery, pool, data, normalized):
    # data: {term: [tf, 1 + log(tf), df, idf, posting list{id: [positions]}]}
    # normalized: {ID: score}
    # lnc.btn
    scores = []
    # Loop through each keyword in the keywordQuery
    for i in range(len(keywordQuery)):
        term = keywordQuery[i]
        score = {}
        if term in data.keys():
            # Loop through each doc id
            for ID in sorted(data[term][4].keys()):
                if pool != []: 
                    if ID in pool:
                        # Score of that document is (1 + log(tf)) * idf / sqrt(sume of all term in that doc weight squared)
                        score[ID] = data[term][1] * data[term][3] / normalized[ID]
                else:
                    score[ID] = data[term][1] * data[term][3] / normalized[ID]
            scores.append(score)
    return scores


def biword(phraseQueries):
    # print(phraseQueries)
    for i in range(len(phraseQueries)):
        phrases = phraseQueries[i].split(' ')
        pair = []
        for j in range(len(phrases)-1):
            pair.append([phrases[j], phrases[j+1]])
        # print(pair, phraseQueries)
        phraseQueries[i] = pair
        # print(phraseQueries)
    return phraseQueries


def sortPhrase(phrases):
    phrases = phrases
    phrases.sort(key = lambda phrase: phrase[1])
    return phrases


def getIntersection(phraseQueries, data, normalized, number):
    pool = []
    for query in phraseQueries:
        for pairs in query:
            if pairs[0] in data.keys():
                posting1 = data[pairs[0]][-1]
            else:
                posting1 = {}
            if pairs[1] in data.keys():
                posting2 = data[pairs[1]][-1]
            else:
                posting2 = {}
            # print(pairs[0], posting1, '\n')
            # print(pairs[1], posting2, '\n\n')
            i = 0; j = 0
            posting12 = list(set(posting1.keys()).intersection(posting2.keys()))
            for ID in posting12:
                position1 = posting1[ID]
                position2 = posting2[ID]
                while i < len(position1) and j < len(position2):
                    if position1[i] + 1 == position2[j]:
                        if ID not in pool:
                            pool.append(ID)
                        break
                    elif position1[i] + 1 > position2[j]:
                        j += 1
                    else:
                        i += 1

    print('pool:', pool)
    if len(pool) < 5 * number and len(pool) > 0:
        minimum = 2
        biword = []
        for query in phraseQueries:
            for i in range(len(query)):
                print([query[i][0], query[i][1]])
                score = cosineScore([query[i][0], query[i][1]], pool, data, normalized)
                scoreSum = 0
                for j in score:
                    for item in j.items():
                        scoreSum += item[1]
                if scoreSum < minimum:
                    minimum = scoreSum
                    biword = [query[i][0], query[i][1]]
        print(phraseQueries, biword)
        for i in range(len(phraseQueries)):
            if biword in phraseQueries[i]:
                phraseQueries[i].remove(biword)

        pool = getIntersection(phraseQueries, data, normalized, number)

    return pool


def main():
    # Get the arguments and validate the number
    arguments = sys.argv
    if len(arguments) != 4:
        error("Invalid arguents")

    directory = arguments[1]
    number = int(arguments[2])
    query = arguments[3]

    data = dictionaryStore(directory+'index.tsv')
    # print(data)
    # for i in sorted(data.keys()):
    #     print(data[i])

    normalized = normalizedStore(directory + 'normalized.tsv')

    keywordQueries, phraseQueries = getSubquery(query)
    # print('phrase:', phraseQueries)
    # print('keyword:', keywordQueries)

    scores = cosineScore(keywordQueries, [],data, normalized)
    #     for j in sorted(i.items()):
    #         print(j)
    #     print()
    biword(phraseQueries)
    # print('number:', number, 'phraseQueries:', phraseQueries)

    pool = getIntersection(phraseQueries, data, normalized, number)
    # for _ in pool:
    #     pass
    # print('\n\npool:', pool)

    query = keywordQueries
    for i in phraseQueries:
        for j in i:
            query.append(j[0])
            query.append(j[1])
    scores = cosineScore(query, pool, data, normalized)
    for item in scores[0].keys():
        print(item, scores[0][item])


if __name__ == "__main__":
    main()

    print('\nDone\n')
