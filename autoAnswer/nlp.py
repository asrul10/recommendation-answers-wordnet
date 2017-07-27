import re
from rake_nltk import Rake
from nltk import pos_tag, word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from html.parser import HTMLParser

class TagsStripper(HTMLParser): # Strip HTML Tags
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class RakeTags(): # Rapid Automatic Keyword Extraction
	def generate(self, text, array = False):
		rake = Rake()
		# tm = TextMining()
		# text = tm.tokenizing(tm.stripTags(text))
		# text = tm.stem(text)
		# rake.extract_keywords_from_text(' '.join(text))
		rake.extract_keywords_from_text(text)
		if array:
			return rake.get_ranked_phrases()[:10]
		else:
			return ', '.join(rake.get_ranked_phrases()[:10])

class TextMining(): # Text Mining
	def stripTags(self, text):
		strip = TagsStripper()
		text = text.replace('&', ' ')
		text = text.replace('"', "'")
		strip.feed(text)
		return strip.get_data()
	def tokenizing(self, text):
		tokenizer = RegexpTokenizer(r'\w+')
		text = self.stripTags(text)
		text = re.sub(r"http\S+", "", text)
		return tokenizer.tokenize(text)
	def filtering(self, text):
		stop = set(stopwords.words('english'))
		new_text = []
		for word in text:
			word = word.lower()
			if word not in stop:
				new_text.append(word)
		return new_text
	def stem(self, text):
		wnl = WordNetLemmatizer()
		new_text = [];
		for word in text:
			new_text.append(wnl.lemmatize(word))
		return new_text
	def generate(self, text):
		rToken = self.tokenizing(text)
		# rFiltering = self.filtering(rToken)
		return self.stem(rToken)

class WordNet():
	def penn_to_wn(self, tag):
		""" Convert between a Penn Treebank tag to a simplified Wordnet tag """
		if tag.startswith('N'):
			return 'n'
		if tag.startswith('V'):
			return 'v'
		if tag.startswith('J'):
			return 'a'
		if tag.startswith('R'):
			return 'r'
		return None

	def tagged_to_synset(self, word, tag):
		wn_tag = self.penn_to_wn(tag)
		if wn_tag is None:
			return None
		try:
			return wordnet.synsets(word, wn_tag)[0]
		except:
			return None
	
	def similarity(self, sentence1, sentence2):
		""" compute the sentence similarity using Wordnet """
		tm = TextMining()
		# Tokenize and tag
		sentence1 = pos_tag(tm.generate(sentence1))
		sentence2 = pos_tag(tm.generate(sentence2))
		# Get the synsets for the tagged words
		synsets1 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence1]
		synsets2 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence2]
		# Filter out the Nones
		synsets1 = [ss for ss in synsets1 if ss]
		synsets2 = [ss for ss in synsets2 if ss]
		score, count = 0.0, 0
		# For each word in the first sentence
		for synset in synsets1:
			# Get the similarity value of the most similar word in the other sentence
			best_score = []
			for ss in synsets2:
				if synset.path_similarity(ss) is not None:
					best_score.append(synset.path_similarity(ss))
			if best_score:
				best_score = max(best_score)
			else:
				best_score = None
			# Check that the similarity could have been computed
			if best_score is not None:
				score += best_score
				count += 1
		# Average the values
		if count:
			score /= count
		else:
			score = 0
		return score