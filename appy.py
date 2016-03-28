#pip install flask
#pip install flask-restful
#

from flask import Flask, send_from_directory
from flask import jsonify
from flask import request
from flask.ext.restful import Api, Resource
from flask.ext.restful import reqparse
from server import docManager
import copy


import traceback


import os

import logging
from logging.handlers import RotatingFileHandler
formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)


logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)s %(message)s',
					filename='app.log',
					filemode='w')


static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
app = Flask(__name__, static_folder='ui')
app.logger.addHandler(handler)

log = logging.getLogger('main')




##########################################################################################

"""
load the initial graph
"""

class Hello(object):

	def init(self):
		self.sg = docManager.NetX("hello")
		self.sg.load_from_json('server/force2.json')

	def get_hello_world(self):
		return self.sg



hello = Hello()
hello.init()

#########################################################################################
"""
a sample message

{ "From" : {
	"EmailAddress": "username@corp.com",
	"Username" : "username"
  },
  "Message": {
    "Subject": "Meet for lunch?",
    "Body": {
      "ContentType": "Text",
      "Content": "The new cafeteria is open."
    },
    "ToRecipients": [
      {
        "EmailAddress": {
          "Address": "garthf@a830edad9050849NDA1.onmicrosoft.com",
          "Username" : "username"
        }
      }
    ],
    "Attachments": [
      {
        "@odata.type": "#Microsoft.OutlookServices.FileAttachment",
        "Name": "menu.txt",
        "ContentBytes": "bWFjIGFuZCBjaGVlc2UgdG9kYXk="
      }
    ]
  }
}
"""

class EmailProcessingUtil(object):
	def __init__(self):
		pass

	@staticmethod
	def process_email_address(emailAddress):
		(username, emaildomain) = emailAddress.split("@")
		#(corp, domain) = emaildomain.split(".")
		return (username, emaildomain, "NA")

	@staticmethod
	def process_From_parameters(fromItem):
		"""There can be exceptions here that we dont want to handle here."""	
		d = {}
		email_address = fromItem['EmailAddress']
		(emailUserId, emaildomain, corp) = EmailProcessingUtil.process_email_address(email_address)
		d['EmailAddress'] = fromItem['EmailAddress']
		d['Username'] = fromItem['Username']
		d['Corp'] = corp
		d['EmailDomain'] = emaildomain
		d['EmailUserId'] = emailUserId
		return d



	@staticmethod
	def process_To_parameters(toItem):
		"""There can be exceptions here that we dont want to handle here."""	
		
		to_email_list = []
		for item in toItem:
			to_email = item['EmailAddress']['Address']
			(emailUserId, emaildomain, corp) = EmailProcessingUtil.process_email_address(to_email)
			d = {}
			d['EmailAddress'] = to_email
			d['Username'] = item['EmailAddress']['Username']
			d['Corp'] = corp
			d['EmailDomain'] = emaildomain
			d['EmailUserId'] = emailUserId
			to_email_list.append(to_email)


		return to_email_list


class HelloEmailMessageAPI(Resource):

	def __init__(self):
		self.postParser = reqparse.RequestParser()
		self.postParser.add_argument('From', type = dict,  required=True, help="From user is missing", location = 'json')
		self.postParser.add_argument('Message', type = dict,  required=True, help="to user is missing", location = 'json')		
		super(HelloEmailMessageAPI, self).__init__()


	def post(self):
		args = self.postParser.parse_args()
		sg = hello.get_hello_world()
		try:
			fromItem = args['From']
			toItem = args['Message']['ToRecipients']
			message = args['Message']

			# now extract the details from the from item
			fromParams = EmailProcessingUtil.process_From_parameters(fromItem)
			toParams   = EmailProcessingUtil.process_To_parameters(toItem)
			messageSubject = message['Subject']
			messageBody = message['Body']['Content']
					
			return jsonify( { 'status': "ok", 'From' : fromParams,
			'To' : toParams, 'Subject' : messageSubject, 'Body' : messageBody} )
		except Exception as ex:
			tb = traceback.format_exc()
			log.error("trace: {}".format(tb))
			return jsonify( { 'status': "error", 'payload' : ex.message } )

class HelloPathAPI(Resource):

	def __init__(self):
		self.postParser = reqparse.RequestParser()
		self.postParser.add_argument('from', type = str,  required=True, help="from user is missing", location = 'json')
		self.postParser.add_argument('to', type = str,  required=True, help="to user is missing", location = 'json')		
		self.postParser.add_argument('length', type = int,  default=6, location='json')
		
		self.getParser = reqparse.RequestParser()
		self.getParser.add_argument('from', type = str,  required=True, help="from user is missing", location = 'args')
		self.getParser.add_argument('to', type = str,  required=True, help="to user is missing", location = 'args')		
		self.getParser.add_argument('length', type = int,  default=6, location='args')
		

		super(HelloPathAPI, self).__init__()

	def get(self):
		args = self.getParser.parse_args()
		sg = hello.get_hello_world()
		fromId = args['from']
		toId = args['to']
		length = args['length']

		try:
			paths = sg.k_shortest_path(fromId, toId, length, weight='weight')		
			return jsonify( { 'status': "ok", 'payload' : paths } )
		except Exception as ex:
			return jsonify( { 'status': "error", 'payload' : ex.message } )

	def post(self):
		args = self.postParser.parse_args()
		sg = hello.get_hello_world()
		fromId = args['from']
		toId = args['to']
		length = args['length']

		try:
			paths = sg.k_shortest_path(fromId, toId, length, weight='weight')		
			return jsonify( { 'status': "done", 'payload' : paths } )
		except Exception as ex:
			tb = traceback.format_exc()
			log.error("trace: {}".format(tb))
			return jsonify( { 'status': "error", 'payload' : ex.message } )


"""
post data:

{"from" : "as", "to" : "go", "info" : {"type" : "official", "frequency" : 100}}
{"from" : "as", "to" : "go", "info" : {}}
"""

class HelloPathScoreAPI(Resource):

	def __init__(self):
		self.postParser = reqparse.RequestParser()
		self.postParser.add_argument('from', type = str,  required=True, help="from user is missing", location = 'json')
		self.postParser.add_argument('to', type = str,  required=True, help="to user is missing", location = 'json')		
		self.postParser.add_argument('info', type = dict,  default={}, location='json')
		
		self.getParser = reqparse.RequestParser()
		self.getParser.add_argument('from', type = str,  required=True, help="from user is missing", location = 'args')
		self.getParser.add_argument('to', type = str,  required=True, help="to user is missing", location = 'args')		
		self.getParser.add_argument('info', type = dict,  default={}, location='args')
		
		super(HelloPathScoreAPI, self).__init__()

	def get(self):
		args = self.getParser.parse_args()
		sg = hello.get_hello_world()
		result = self._process(args, sg)
		return result

	def post(self):
		args = self.postParser.parse_args()
		sg = hello.get_hello_world()
		result = self._process(args, sg)		
		return result

	def _process(self, args, sg):

		fromId = args['from']
		toId = args['to']
		info = args['info']

		try:
			d = {}
			if info is dict:
				d = info
			else:				
				for k in info:
					d[k] = info[k]

			log.info("from: {} to: {} data: {}".format(fromId, toId, d))

			edgeInfo = docManager.Edge(d)
			before = sg.get_edge_info(fromId, toId)
			before = copy.deepcopy(before)
			log.info("from: {} to: {} dataBefore: {}".format(fromId, toId, before))

			# what if either from or to user is not present?
			sg.update_edge_info(fromId, toId, edgeInfo)
			after = sg.get_edge_info(fromId, toId)
			log.info("from: {} to: {} dataAfter: {}".format(fromId, toId, after))

			return jsonify( { 'status': "ok", 'payload' : {'before' : before, 'after' : after} } )
		except Exception as ex:
			tb = traceback.format_exc()
			log.error("trace: {}".format(tb))
			return jsonify( { 'status': "error", 'payload' : ex.message } )



"""
returns the list of users in the system (user=all)
returns info for a specific user (user=<username>)
"""
class HelloListAPI(Resource):

	def __init__(self):
		
		self.getParser = reqparse.RequestParser()
		self.getParser.add_argument('user', type = str,  required=True, help="user is missing. If set to all returns a list of all users. Otherwise returns info for a specific user", location = 'args')
		self.getParser.add_argument('length', type = int,  default=6, location='args')		
		super(HelloListAPI, self).__init__()

	def get(self):
		args = self.getParser.parse_args()
		sg = hello.get_hello_world()
		user = args['user']
		length = args['length']

		try:
			if user == "all":
				listofusers = sg.get_node_names()
				return jsonify( { 'status': "ok", 'payload' : listofusers } )				
			else:
				log.info("requesting info for user: {}".format(user))
				userinfo = sg.get_node_data(user)
				log.info("Found info for user: {}".format(userinfo))

				return jsonify( { 'status': "ok", 'payload' : userinfo } )				
		except Exception as ex:
			tb = traceback.format_exc()
			log.error("trace: {}".format(tb))
			return jsonify( { 'status': "error", 'payload' : ex.message } )			


"""
returns a serialized view of the world
"""
class HelloWorldViewAPI(Resource):

	def __init__(self):		
		super(HelloWorldViewAPI, self).__init__()

	def get(self):
		try:
			sg = hello.get_hello_world()
			serialized = sg.get_as_json()
			return serialized				
		except Exception as ex:
			tb = traceback.format_exc()
			log.error("trace: {}".format(tb))
			return jsonify( { 'status': "error", 'payload' : ex.message } )	



api = Api(app)
api.add_resource(HelloPathAPI, '/hello', endpoint = 'helloWorld')
api.add_resource(HelloListAPI, '/list', endpoint = 'hellolist')
api.add_resource(HelloWorldViewAPI, '/worldview', endpoint = 'helloworldview')
api.add_resource(HelloPathScoreAPI, '/degree', endpoint = 'updateinfo')
api.add_resource(HelloEmailMessageAPI, '/mail', endpoint = 'emailinfo')




def  main():	
	print "folder: {}".format(static_folder_root)
	app.run(debug=False)
	pass

	
if __name__ == '__main__':
	log.info("starting app")
	main()

