import falcon
import json
from dbConn.db import Connect
from autoAnswer.nlp import TextMining, RakeTags, WordNet

ALLOWED_ORIGINS = ['http://localhost:4200']

class CorsMiddleware(object):
    def process_request(self, request, response):
        origin = request.get_header('Origin')
        if origin in ALLOWED_ORIGINS:
            response.set_header('Access-Control-Allow-Origin', origin)
            response.set_header('Access-Control-Allow-Headers', "Origin, X-Requested-With, Content-Type, Accept")

class Greeting:
	def on_get(self, req, res):
		res.body = json.dumps({'status': True, 'message': 'Welcome to auto answering'})

class GetRecommendation:
	def on_post(self, req, res):
		tm = TextMining()
		rt = RakeTags()
		wn = WordNet()
		body = json.loads(req.stream.read())
		text = body['question']
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
		sql.execute("SELECT id, id_answer, score, content, tags," + case + " as priority FROM question WHERE " + like + " order by priority desc limit 10")
		
		result = []
		for id, id_answer, score, content, tags, priority in sql.fetchall():
			sql.execute("SELECT content FROM answer WHERE id = '%s'", (id_answer,))
			content = content.replace('\n', "")
			answer = sql.fetchone()
			if answer is None:
				answer = 'Belum terjawab'
			else:
				answer = answer[0].replace('\n', ' ')

			result.append({
				'id': id,
				'priority': priority, 
				'similarity': wn.similarity(text, content),
				'content': tm.stripTags(content),
				'id_answer': id_answer,
				'answer': tm.stripTags(answer)
			})

		result = sorted(result, key = lambda x: x['similarity'], reverse = True)
		question = {
			'target': text,
			'result': result,
		}

		res.body = json.dumps(result[:5])
 
api = falcon.API(middleware=[CorsMiddleware()])
api.add_route('/', Greeting())
api.add_route('/getRecommendation', GetRecommendation())
# waitress-serve --port=8080 similarityMeasures:api