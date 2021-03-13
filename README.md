
# TODOs

1. **SUBMIT** the URL of this repository on eClass. 
2. List the CCID(s) of student(s) working on the project.
3. List all sources consulted while completing the assignment.

|Student name|  CCID  |
|------------|--------|
|student 1   |xinjian |
|student 2   |skavalin|


# Videos

* Link to xinjian's video: https://drive.google.com/file/d/1L7slZIFUthgKS-0rZl4P4NDxKZI9qxyL/view?usp=sharing
* Link to skavalin's video:https://drive.google.com/drive/folders/1XZ2PkShNyPDaBNwmXQyNIbRANw_18dNJ?usp=sharing

Run the program invertedIndex.py to create inverted index: In command line, go to src folder. type python3 invertedIndex.py [Path to json file] [Path to directory where the index will be stored
The tsv files will be genreated in the src/ folder and each file is names according to json file name.
For example, we use data/dr_seuss_lines.json as input and the output file directory is in current directory,
type "python3 invertedIndex.py ../data/dr_seuss_lines.json ./" in command line

If we use data/movie_plots.json as input and the output file directory is the current directory
type "python3 invertedIndex.py ../data/movie_plots.json ./" in command line.

Run the program query.py to run the query. In Command line, go to src/ folder.
python3 query.py [path to the tsv files are stored] [the number k of ranked documents to be returned] "query"
For example, if the tsv files are in the current folder, the number of ranked documents to be returned is 50 and the query is ":get better: going :like you: lot"
type python3 query.py ./ 50 ":get better: going :like you: lot"

Source:
To find All occurrences for colon:
* https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring

csv field larger than field limit:
* https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

Nested Array sorting:
* https://www.geeksforgeeks.org/python-sort-list-according-second-element-sublist/
