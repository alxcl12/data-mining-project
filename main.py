import os
import re
import nltk
import argparse

from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.query import Or

schema = Schema(
    title = TEXT(stored=True),
    wikipage = TEXT(stored=True)
)

dataset_path = "C:\\Facultate\\New\\Master1reloaded\\Sem1\\DataMining\\DataMiningProject\\wiki-subset-20140602"
index_path = "my_index"
question_path = "C:\\Facultate\\New\\Master1reloaded\\Sem1\\DataMining\\DataMiningProject\\questions.txt"
def process_wikipedia_page(file):
    with open(file, "r", encoding='utf-8') as f:
        input = f.read()

    split_input = re.split(r'\n*\[\[(.*?)\]\]\n', input)

    titles = []
    content = []
    split_input.pop(0) # first element is garbage
    # titles on even indexes and content on odd indexes
    for index, value in enumerate(split_input):
        if index % 2 == 0:
            titles.append(value)
        else:
            content.append(value)

    output = []
    stemmer = nltk.PorterStemmer()
    stop_wrds = set(nltk.corpus.stopwords.words("english"))
    for line in content:
        tokens = nltk.word_tokenize(line)
        stemmed_tks = [stemmer.stem(word) for word in tokens if word.lower() not in stop_wrds and word.isalnum()]
        output.append(stemmed_tks)

    return titles, output

def make_index():
    ind = index.create_in(index_path, schema)
    with ind.writer(limitmb=2048, procs=3, multisegment=True) as writer:
        for name in os.listdir(dataset_path):
            path = os.path.join(dataset_path, name)
            print(f"Currently on file: {path}")
            title, output = process_wikipedia_page(path)
            if title and output:
                for i in range(len(title)):
                    content = ' '.join(output[i])
                    writer.add_document(title=title[i], wikipage=content)
    ind.close()

def read_questions():
    with open(question_path, "r") as f:
        lines = f.readlines()

    # categories every %4 = 1
    # clues every %4 = 2
    # answer every %4 = 3
    categories = []
    clues = []
    answers = []
    for no, line in enumerate(lines):
        match no % 4:
            case 0:
                categories.append(line.strip())
            case 1:
                clues.append(line.strip())
            case 2:
                answers.append(line.strip())

    return categories, clues, answers

def tokenize_text(content):
    stemmer = nltk.PorterStemmer()
    stops = set(nltk.corpus.stopwords.words("english"))
    tokens = nltk.word_tokenize(content)
    return [stemmer.stem(word) for word in tokens if word.lower() not in stops and word.isalnum()]

def answer_questions():
    cat, clues, answers = read_questions()
    ind = index.open_dir(index_path)
    parser = QueryParser("wikipage", ind.schema)

    right_answers = 0
    wrong_results = []
    correct_results = []
    for i in range(len(cat)):
        print(f"Trying to answer question number {i+1}...")
        print(f"Correct answers so far: {right_answers}")
        categ_queries = [parser.parse(word) for word in tokenize_text(cat[i])]
        clue_queries = [parser.parse(word) for word in tokenize_text(clues[i])]
        final_queries = Or(clue_queries + categ_queries)

        with ind.searcher() as searcher:
            results = searcher.search(final_queries)

            if len(results) > 0 and results[0]['title'] == answers[i]:
                right_answers += 1
                correct_results.append({"category": cat[i],
                                      "clue": clues[i],
                                      "answer": answers[i],
                                      "hits": results
                                      })
            else:
                wrong_results.append({"category": cat[i],
                                      "clue": clues[i],
                                      "answer": answers[i],
                                      "hits": results
                                      })

    print(f"Got {right_answers} right answers out of {len(cat)} questions")
    accuracy = right_answers / len(cat)
    print(f"P@1: {accuracy}")


if __name__ == "__main__":
    nltk.download('stopwords')
    nltk.download('punkt')

    parser = argparse.ArgumentParser(description='Data mining project')
    parser.add_argument('--make-index', help='create the index', action="store_true")
    parser.add_argument('--solve', help='try to answer the questions and provide metrics', action="store_true")

    args = parser.parse_args()
    if args.make_index:
        make_index()

    if args.solve:
        answer_questions()