import csv, json, nltk, string, sys
from math import log10, sqrt
from nltk import WordNetLemmatizer
nltk.download('wordnet')


def error(name):
    '''
    Print out the error and exit the program with -1
    input: name is the name of the error
    '''
    print(name, file=sys.stderr)
    exit(-1)


# Tokenize the list value
def tokenize(value):
    words = []
    for word in value:
        # Lemmatize the word
        word = word.translate(str.maketrans('', '', string.punctuation)).lower()
        word = nltk.WordNetLemmatizer().lemmatize(word)
        # Remove punctuations and make all words lower case
        words.append(word)
    return words


# Create the dictionary where the keys are the words
# and the values are [tf, A dictionary where the keys are the doc ID and
# the values are the the list of the positions]
def indexConstruction(dictionary, ID, value):
    for index in range(len(value)):
        if value[index] in dictionary.keys():
            if ID not in dictionary[value[index]][1].keys():
                dictionary[value[index]][0] += 1
                dictionary[value[index]][1][ID] = [index]
            else:
                dictionary[value[index]][0] += 1
                dictionary[value[index]][1][ID].append(index)
        else:
            dictionary[value[index]] = [1, {ID: [index]}]

    return dictionary


# Create the dictionary to store the normalized tf for each document
def normConstruction(normalized, ID, value):
    corpus = {}
    for word in value:
        if word not in corpus.keys():
            corpus[word] = 1
        else:
            corpus[word] += 1

    cos = 0
    for word in corpus.keys():
        cos += (1 + log10(corpus[word])) * (1 + log10(corpus[word]))
    normalized[ID] = sqrt(cos)

    return normalized


def dictionaryConstruction(document, ID, dictionary, normalized):
    # Loop through each zone in the documents and save all content into a string
    corpus = ''
    for zone in document.keys():
        # Validate zone ID
        if zone != 'doc_id':
            if zone not in dictionary.keys():
                for c in zone:
                    if c in string.punctuation or c.isspace():
                        error("Invalid zone ID" + zone)
            if list(document.keys()).count(zone) != 1:
                error("Repeated zone ID" + zone)

            if corpus == '':
                corpus += document[zone]
            else:
                corpus = corpus + ' ' + document[zone]

    # Save the tokenized value into dictionary contents
    dictionary = indexConstruction(dictionary, ID, tokenize(corpus.split()))
    # {id: w^2, id: w^2, id: w^2}
    normalized = normConstruction(normalized, ID, tokenize(corpus.split()))

    return dictionary, normalized


# Create the TSV file and write the inverted index in it
def writeTSVfile(dictionary, normalized, directory):
    # Create tsv file for write with name index.tsv
    file = open(directory+'index.tsv', 'w', newline='')
    theWriter = csv.writer(file, delimiter='\t')
    theWriter.writerow(['Word', 'tf', 'tf-weight', 'df', 'idf', 'Posting list'])
    # Loop through each item in the dictionary
    for item in sorted(dictionary.items()):
        if item[0] != 'doc_id' and len(item[0]) != 0:
            # Calculate the square of tf-weight and the idf
            # item[1][0] is the tf, len(item[1][1].keys()) is df
            tfWeight = (1 + log10(item[1][0]))
            idf = log10(len(dictionary['doc_id']) / len(item[1][1].keys()))

            # Write each word's inverted index as a row
            theWriter.writerow([item[0], item[1][0], tfWeight, len(item[1][1].keys()), idf, sorted(item[1][1].items())])

    # Create tsv file for write with name normalized.tsv
    file = open(directory+'normalized.tsv', 'w', newline='')
    theWriter = csv.writer(file, delimiter='\t')
    theWriter.writerow(['ID', 'normalized weight'])
    # Loop through each item in the dictionary
    for item in sorted(normalized.items()):
        # Write each word's inverted index as a row
        theWriter.writerow([item[0], item[1]])


if __name__ == "__main__":
    # Get the arguments and validate the number of arguments
    arguments = sys.argv
    if len(arguments) != 3:
        error("Invalid arguents")
    directory = arguments[2]

    # Open the input json file for read
    try:
        inputFile = open(arguments[1], 'r')
    except IOError:
        error('Invalid file arguments')

    # Load and parse json data
    inputData = json.load(inputFile)
    dictionary = {'doc_id' : []}
    normalized = {}
    for document in inputData:
        # Validate doc_id and it is unique
        try:
            ID = int(document['doc_id'])
        except ValueError:
            error('Invalid Document ID')
        if ID in dictionary['doc_id']:
            error('Invalid Repeated Document ID')
        dictionary['doc_id'].append(ID)

        # Validate document has at least one zone
        if len(document.keys()) < 2:
            error("Invalid Document zone")

        # Create dictionary where the keys are the term
        # The value of each dictionary is a list
        # The first item it the tf and
        # the second item is subdictionary where the key are doc ID and
        # the value is a list the positionss which it appears in that doc ID
        dictionary, normalized = dictionaryConstruction(document, ID, dictionary, normalized)

    writeTSVfile(dictionary, normalized, directory)

    print('\nDone\n')
