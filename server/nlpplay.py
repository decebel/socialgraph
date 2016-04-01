from collections import defaultdict
from heapq import nlargest
import nltk
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords 
from string import punctuation
from nltk.corpus import sentiwordnet as swn
from nltk.stem.porter import PorterStemmer
from collections import deque, defaultdict
from Queue import Queue, Full, Empty # thread-safe queue
import threading

#preprocessed
training_data = [
			(['go', 'for', 'lunch', 'for', 'fun'], 'pos'),
			(['go', 'for', 'drinks', 'for', 'fun'], 'pos'),
			(['go', 'to', 'work'], 'obj'),						
			(['go', 'for', 'meeting'], 'obj'),
			]

test_data = [
			(['go', 'out', 'lunch', 'for', 'fun'], 'pos'),
			(['go', 'for', 'drinks', 'for', 'fun'], 'pos'),
			(['finish', 'the', 'work'], 'obj'),						
			(['meet', 'after', 'task'], 'obj'),
			]

all_words = []



def vocab_builder(training_data):
	for (words, label) in training_data:
			all_words.extend(words)

	words_fd = nltk.FreqDist(all_words)
	return words_fd.keys()

def vocab(self):
	return words_fd.keys()


def extract_features_model_one(doc):
	print "doc: {}".format(doc)
	doc_words = set(doc)
	features = {}
	for w in all_words:
		features['contains(%s)' % w] = (w in doc_words)
	return features



def main():

	all_words = vocab_builder(training_data)
	training_features = nltk.classify.apply_features(extract_features_model_one, training_data)
	classifier = nltk.NaiveBayesClassifier.train(training_features)

	test1, ignore = test_data[0]
	test2, ignore = test_data[1]

	result_label = classifier.classify(extract_features_model_one(test1))
	print "result_label: {}".format(result_label)




if __name__ == '__main__':
	main()