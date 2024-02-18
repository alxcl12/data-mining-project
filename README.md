### Requirements
- Python 3.10 or above (due to a switch case being used)
- whoosh library
- nltk library

### Configuration
Before running, some variables need to be set to the correct paths:
- dataset_path - path to the directory containing the wikipedia pages
- index_path - path to the directory where the index will be stored
- question_path - path to the questions.txt file

### Usage
Firstly, you need to create the index:
```
python3 main.py --make-index
```

Afterwards, just run the program and the P@1 metric will be displayed
```
python3 main.py --solve
```