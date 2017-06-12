import falcon
import json
from dbConn.db import Connect
from autoAnswer.nlp import TextMining, RakeTags, WordNet

class GetRecommendation:
	def on_get(self, req, res):
		tm = TextMining()
		rt = RakeTags()
		wn = WordNet()
		# text = input('Enter question: ')
		text = 'There is hardware erroneously regard the headset as attached at all times jack port. Make calls without headset or speaker mode.'
		tmResult = tm.generate(text)
		rtResult = rt.generate(text, True)

		db = Connect().dbOpen()
		sql = db.cursor()
		case = ''
		like = ''
		i = 0
		for tag in rtResult:
			if i != 0:
				case += ' + '
				like += ' or '
			case += 'case when tags like "%%%s%%" then 1 else 0 end' % tag
			like += 'tags like "%%%s%%"' % tag
			i += 1
		sql.execute("SELECT id, score, content, tags," + case + " as priority FROM question WHERE " + like + " order by priority desc limit 10")
		
		result = []
		for id, score, content, tags, priority in sql.fetchall():
			content = content.replace('\n', "")
			result.append({
				'priority': priority, 
				'similarity': wn.similarity(text, content),
				'content': tm.stripTags(content),
			})

		result = sorted(result, key = lambda x: x['similarity'], reverse = True)
	
		question = {
			'target': text,
			'result': result
		}

		res.body = json.dumps(question)
 
api = falcon.API()
api.add_route('/', GetRecommendation())
# waitress-serve --port=8080 similarityMeasures:api