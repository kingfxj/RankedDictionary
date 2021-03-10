import csv, json, nltk, string, sys
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
# and the values the lists of Document IDs that they appear
def indexConstruction(dictionary, ID, value):
    for word in value:
        if word in dictionary.keys():
            if ID not in dictionary[word]:
                dictionary[word].append(ID)
        else:
            dictionary[word] = [ID]
    return dictionary

def dictionaryConstruction(document, ID, dictionary):
    # Loop through each zone in the document
    for zone in document.keys():
        # Validate zone ID
        if zone != 'doc_id':
            if zone not in dictionary.keys():
                for c in zone:
                    if c in string.punctuation or c.isspace():
                        error("Invalid zone ID" + zone)
            if list(document.keys()).count(zone) != 1:
                error("Repeated zone ID" + zone)

            # Save the tokenized value into dictionary contents
            if zone in dictionary.keys():
                dictionary[zone] = indexConstruction(dictionary[zone], ID, tokenize(document[zone].split()))
            else:
                dictionary[zone] = indexConstruction({}, ID, tokenize(document[zone].split()))
    return dictionary

# Create the TSV file and write the inverted index in it
def writeTSVfile(dictionary, directory):
    # Loop through each zone in the dictionary
    for zone in dictionary.keys():
        if zone != 'doc_id':
            # Create tsv file for write with zone name
            file = open(directory+zone+'.tsv', 'w', newline='')
            theWriter = csv.writer(file, delimiter='\t')
            theWriter.writerow(['Word', 'Frequency', 'Posting list'])
            # Write each word's inverted index as a row
            for key in sorted(dictionary[zone]):
                if len(key) != 0:
                    theWriter.writerow([key, len(dictionary[zone][key]), sorted(dictionary[zone][key])])

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

        # Create dictionary where the keys are the zone ID
        # The value of each dictionary is a subdictionary
        #  which is the inverted index
        # The key for the the subdictionary are the words
        #  and the value is a list of the document ID which they appear
        dictionary = dictionaryConstruction(document, ID, dictionary)

    writeTSVfile(dictionary, directory)
