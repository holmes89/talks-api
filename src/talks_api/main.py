#!/usr/bin/env python

import json
import os

import motor.motor_tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from bson.objectid import ObjectId
from jsonschema import validate

define("port", default=8888, help="run on the given port", type=int)

MONGO_CONN = os.getenv('MONGO_DB', 'mongodb://localhost:27017')

schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "display_name": {"type": "string"},
        "url": {"type": "string"},
    },
    "required": ["url"]
}

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/talks/([0-9a-z]*)", MainHandler),
        ]

        client = motor.motor_tornado.MotorClient(MONGO_CONN)
        db = client['general']
        settings = dict(
            autoescape=None,
            db=db
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class MainHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.body:
            self.args = json.loads(self.request.body)

    async def get(self, path):
        db = self.settings['db']
        collection = db['talks']
        id = None
        if path:
            print(path)
            document = await collection.find_one({'_id': ObjectId(path)})
            if document is None:
                self.clear()
                self.set_status(404)
                self.finish({"error": "entity not found"})
            document['id'] = str(document['_id'])
            del document['_id']
            self.write(document)
        else:
            cursor = collection.find(id)
            talks = []
            for document in await cursor.to_list(length=100):
                document['id'] = str(document['_id'])
                del document['_id']
                talks.append(document)
            self.write({'results': talks})
        
    async def post(self, path):
        db = self.settings['db']
        collection = db['talks']
        document = self.args
        try:
            validate(instance=document, schema=schema)
        except:
            self.clear()
            self.set_status(400)
            self.write({"error": "invalid format"})
            return
        
        if 'display_name' not in document:
            document['display_name'] = ''
        result = await collection.insert_one(document)
        document['id'] = str(document['_id'])
        del document['_id']
        self.set_status(201)
        self.write(document)
 

    async def patch(self, path):
        db = self.settings['db']
        collection = db['talks']
        document = self.args
        try:
            validate(instance=document, schema=schema)
        except:
            self.clear()
            self.set_status(400)
            self.write({"error": "invalid format"})
            return
        if 'display_name' not in document:
            document['display_name'] = ''

        await collection.update_one({'_id': ObjectId(path)}, {'$set': {'url': document['url'], 'display_name': document['display_name']}}, upsert=False)
        document['id'] = path
        self.set_status(200)
        self.write(document)
       

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()