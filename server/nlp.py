from collections import defaultdict
from heapq import nlargest
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords 
from string import punctuation
from nltk.corpus import sentiwordnet as swn
from nltk.stem.porter import PorterStemmer
from collections import deque, defaultdict
from Queue import Queue, Full, Empty # thread-safe queue
import threading
import time

import logging
log = logging.getLogger('nlp')


class CommandInfo(object):

	"""Commands posted to the DataServer.

	All commands are processed sequentially by the server
	"""

	def __init__(self, name, args):
		self.name = name		
		self.args = args

	def get_command(self):
		return self.name

	def get_val(self, arg):

		if arg in self.args:
			return self.args[arg]

	def get_payload(self):
		return self.args


###TODO. to be implemented by Hello
class Listener(object):
	def onScore(self):
		pass


class DegreesManager(threading.Thread):

	def __init__(self, engine_name, hello_world_graph, command_queue = None):
		threading.Thread.__init__(self, name = engine_name)

		self.isRunning = False

		if not command_queue:
			self.command_queue = Queue()
		else:
			self.command_queue = command_queue


		self.engine_name = engine_name
		self.graph = hello_world_graph

	def get_path(fromId, toId, length, weight='weight'):
		pass

	



	def onEmailMessage(self, message):
		self.command_queue.put(CommandInfo("EM", message ))		

	def onIMMessage(self, message):
		self.command_queue.put(CommandInfo("IM", message ))		
		

	def post_message(self, tableId, schema):
		print "posting to queue.."

	def shutdown(self):
		self.isRunning = False

	def run(self):
		
		if not self.isRunning:
			self.isRunning = True
			self._process_queued_messages()

		print "\nrun method completed"

	def _process_queued_messages(self):

		while self.isRunning:
			print "inside command processor. waiting for commands"			
			workFound = False

			try:				

				commandInfo = self.command_queue.get(True, 5) #should block until someone has posted some command on the queue
				workFound = True #hack to avoid exception within finally block

				#todo: should we do a dispatch table. they seem to be static methods ?
				if commandInfo.get_command() == "EM":
					self._process_em(commandInfo)

				elif commandInfo.get_command() == "IM":
					self._process_im(commandInfo)


			except Empty as timeout:
				logging.debug("Timeout..no input commands")

			except Exception as e:
				import traceback, os.path
				top = traceback.extract_stack()[-1]
				logging.error(', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])]))					
				logging.error("error processing command %s", str(e))

			finally:
				if workFound:
					self.command_queue.task_done()

	def _process_em(self, commandInfo):
		log.info("processing EM command. message: {}".format(commandInfo.get_payload()))
		

		
	def _process_im(self, commandInfo):
		pass


class NLPEngine(threading.Thread):

	def __init__(self, engine_name, hello_world_graph, command_queue = None):
		threading.Thread.__init__(self, name = engine_name)

		self.isRunning = False

		if not command_queue:
			self.command_queue = Queue()
		else:
			self.command_queue = command_queue


		self.engine_name = engine_name
		self.graph = hello_world_graph


	def onEmailMessage(self, message):
		self.command_queue.put(CommandInfo("EM", message ))		

	def onIMMessage(self, message):
		self.command_queue.put(CommandInfo("IM", message ))		
		

	def post_message(self, tableId, schema):
		print "posting to queue.."

	def shutdown(self):
		self.isRunning = False

	def run(self):
		
		if not self.isRunning:
			self.isRunning = True
			self._process_queued_messages()

		print "\nrun method completed"

	def _process_queued_messages(self):

		while self.isRunning:
			print "inside command processor. waiting for commands"			
			workFound = False

			try:				

				commandInfo = self.command_queue.get(True, 5) #should block until someone has posted some command on the queue
				workFound = True #hack to avoid exception within finally block

				#todo: should we do a dispatch table. they seem to be static methods ?
				if commandInfo.get_command() == "EM":
					self._process_em(commandInfo)

				elif commandInfo.get_command() == "IM":
					self._process_im(commandInfo)


			except Empty as timeout:
				logging.debug("Timeout..no input commands")

			except Exception as e:
				import traceback, os.path
				top = traceback.extract_stack()[-1]
				logging.error(', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])]))					
				logging.error("error processing command %s", str(e))

			finally:
				if workFound:
					self.command_queue.task_done()

	def _process_em(self, commandInfo):
		log.info("processing EM command. message: {}".format(commandInfo.get_payload()))


		
	def _process_im(self, commandInfo):
		pass



def default_nlp_engine():
	return NLPEngine('default', None, None)		

MODELS = {
	'default' : default_nlp_engine(),
} 

SERVERS = {
	
}




class EnginePool(threading.Thread):

	def __init__(self, models = ['default']):
		threading.Thread.__init__(self)
		self.models = models
		self.isRunning = False

	def start_engines(self):			
		for model in self.models:
			if model not in SERVERS:
				SERVERS[model] = nlp_service = MODELS.get(model)				
			if not nlp_service.isRunning:
				nlp_service.setDaemon(True)
				nlp_service.start()


	def stop_engines(self):		
		"""Not a forceful shutdown. """
		for model in self.models:
			m = SERVERS[model]
			m.shutdown()

	def stop_driver(self):
		self.isRunning = False

	def run(self):
		self.isRunning = True

		while self.isRunning:
			time.sleep(2)
			self.post_message_email('test message')
			# for model in self.models:
			# 	log.info("posting message to the nlp engine: {}".format(model))
			# SERVERS[model].onEmailMessage('test message')
			logging.debug('running')



	def post_message_email(self, message, dest_models = None):
		if dest_models is None:
			dest_models_to_post = self.models
		else:
			dest_models_to_post = dest_models

		for model in dest_models_to_post:
			if model in SERVERS:
				SERVERS[model].onEmailMessage(message)
			else:
				log.error("model name is not valid: {}".format(model))



def engine_pool_tester():
	ep = EnginePool()
	ep.start_engines()

	try:
		ep.start()
		log.info("started pool..")

	except Exception as ex:		
		log.warn("received exception: {}".format(ex.message))
		ep._Thread__stop() #not sure
		ep.stop_engines()

		sys.exit(1)



class FrequencySummarizr(object):

	def __init__(self, mincut=0.0, maxcut=1.0):
		self._mincut = mincut
		self._maxcut = maxcut
		self._stopwords = set(stopwords.words('english')).union(list(punctuation))
	
	
	def word_freq(self, words, customStopWords = None):        
		stopwords = self._stopwords

		if customStopWords:
			stopwords = self._stopwords.union(customStopWords)
		
		print words
		
		#print stopwords
		freq = defaultdict(int)
		for w in words:
			if w not in stopwords:                  
				freq[w] += 1
		
		#get max
		countmax = float(max(freq.values()))
		
		for w in freq.keys():
			word_freq = freq[w] / countmax
			if word_freq < self._mincut or word_freq > self._maxcut:
				del freq[w]
			else:
				freq[w] = word_freq
		
		return freq
	
	def summarize(self, doc, n):
		
		#sentences_tokenized = []
		#for s in doc:
		#    sentences_tokenized.append(word_tokenize(s))

		sentences = sent_tokenize(doc)
		words = [word_tokenize(s.lower()) for s in sentences]
	   
		wordlist = []
		for w in words:
			wordlist.extend(w)
		
		#print "word list"
		#print wordlist
		#return
		
		
		#print words
		
		freq = self.word_freq(wordlist)   
		#print "word freq: {}".format(freq)
		
		score = defaultdict(int)
		for i,line in enumerate(sentences):
			#print "processing line# : {} line: {}".format(i, line)
			for w in word_tokenize(line.lower()):
				if w in freq:
					#print "line#: {} word: {} found with freq: {}".format(i, w, freq[w])
					score[i] += freq[w]
				else:                    
					#print "word: {} not found in line#: {}".format(w, i)
					pass
	
		
		
		print "top: {} from scores: {}".format(n, score)
		
		ntop = nlargest(n, score, key = score.get)
		#print "ntop : {}".format(ntop)
		#print ntop
		return ntop




"""

porter_stemmer = PorterStemmer()
porter_stemmer.stem('maximum')

swn.senti_synsets('happy')
swn.senti_synsets('slow', 'v')
slow= swn.senti_synset('slow.v.03')
slow.pos_score()
slow.neg_score()
slow.obj_score()



from nltk.collocations import *
text = "I do not like green eggs and ham, I do not like them Sam I am!"
tokens = nltk.wordpunct_tokenize(text)
finder = BigramCollocationFinder.from_words(tokens)
bigram_measures = nltk.collocations.BigramAssocMeasures()
scored = finder.score_ngrams(bigram_measures.raw_freq)
sorted(bigram for bigram, score in scored)


trigram_measures = nltk.collocations.TrigramAssocMeasures()
finder = TrigramCollocationFinder.from_words(tokens)
scored = finder.score_ngrams(trigram_measures.raw_freq)
sorted(trigram for trigram, score in scored)

#frequency distribution of words
fd = nltk.FreqDist(['hello', 'this', 'is', 'now', 'interesting', 'hello', 'now'])
fd.keys()


lunch = swn.senti_synsets('lunch')
print lunch[0]
lunch[0].obj_score()
"""

def  main():
	engine_pool_tester()



if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )	
	main()

