import MySQLdb

class Connect():
	def dbOpen(self):
		return MySQLdb.connect("localhost", "root", "password", "auto-answer")