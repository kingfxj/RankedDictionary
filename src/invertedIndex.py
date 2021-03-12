import csv, json, nltk, string, sys
from math import log
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

# Create the subdictionary where the keys are the words
# and the values are [df, tf, the lists of Document IDs that they appear]
def indexConstruction(dictionary, ID, value):
    # D
    for word in value:
        if word in dictionary.keys():
            if ID not in dictionary[word][1]:
                dictionary[word][0] += 1
                dictionary[word][1].append(ID)
            else:
                dictionary[word][0] += 1
        else:
            dictionary[word] = [1, [ID]]
    return dictionary

def dictionaryConstruction(document, ID, dictionary):
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

    return dictionary

# Create the TSV file and write the inverted index in it
def writeTSVfile(dictionary, directory):
    # Create tsv file for write with document name
    file = open(directory+'index.tsv', 'w', newline='')
    theWriter = csv.writer(file, delimiter='\t')
    theWriter.writerow(['Word', 'tf', 'tf-weight^2', 'df', 'idf', 'Posting list'])
    # Loop through each item in the dictionary
    for item in sorted(dictionary.items()):
        if item[0] != 'doc_id' and len(item[0]) != 0:
            # Write each word's inverted index as a row
            tfWeight2 = (1 + log(item[1][0])) * (1 + log(item[1][0]))
            idf = log(sorted(dictionary['doc_id'])[-1]/ len(item[1][1]))
            theWriter.writerow([item[0], item[1][0], tfWeight2, len(item[1][1]), idf, item[1][1]])


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

        # The value of each dictionary is a subdictionary
        #  which is the inverted index
        # The key for the the subdictionary are the words
        #  and the value is a list of the document ID which they appear
        dictionary = dictionaryConstruction(document, ID, dictionary)

    writeTSVfile(dictionary, directory)
    print('\nDone\n')
