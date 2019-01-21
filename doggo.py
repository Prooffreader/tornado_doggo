"""Tornado server that implements requirements at
https://gist.github.com/aparrish/691b0301f6737d65b01db9920a60a0a5

usage:
python api.py <port>

Note that the Amazon Linux 2 ECS instance this is running on only
has one port open, which I'm not revealing in a git repo!
"""
import logging
import os
import re
import sys
from urllib import parse

import tornado.ioloop
import tornado.web
from tornado.web import url
import motor.motor_tornado
from pymongo import MongoClient

# define port
port = int(sys.argv[1])

# set up logging
# TODO: Tornado has its own logging feature but I haven't had time
# to explore it yet (I've had two days to learn it)

# create logging directory if it does not exist
if not os.path.isdir('logs'):
    os.mkdir('logs')

def create_logger():
    """Boilerplate imperative style simple logging.
    TODO: Consider using RotatingFileHandler if heavy use expected"""
    logger = logging.getLogger('tornadodoggo')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('logs/tornadodoggo.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = create_logger()
logger.info('=== logging session started ===')


# helper function

def make_regex(query):
    """Changes query string into a re.compile()'d regex that
    will match query exactly but also be insensitive to case"""
    return re.compile('^' + re.escape(query) + '$', re.IGNORECASE)


# define Handlers

class DefaultHandler(tornado.web.RequestHandler):
    """Bare endpoint just in case someone queries the URL without specifying /count"""
    def get(self):
        logger.warning('New query to bare url / endpoint')
        self.write('Usage: GET <this url>/count?field1=value1[&field2=value2...]')


class CountHandler(tornado.web.RequestHandler):
    """Class for /count endpoint. Follows instructions in link in module docstring"""

    def initialize(self, db_fields):
        """Set valid fields for MongoDB collection passed from Application object on launch
        Set MongoDB database"""
        self.db_fields = db_fields

    def _get_valid_queries(self):
        """Return a dict of {field: value} pairs where value has been modified by the make_regex()
        function, above. This dict will be passed to the motor/MongoDB query.
        Since instructions did not indicate what to do with duplicate queries, if there
        are any, only the final value is kept.

        Returns:
            dict as described above in this docstring
        """
        valid_queries = {}
        for field in self.db_fields:
            arguments = self.get_query_arguments(field)
            if arguments:
                valid_queries[field] = make_regex(arguments[-1])  # keep only final value
        self.valid_queries = valid_queries

    def _get_invalid_fields(self, actual_request):
        """Returns a list of fields in the query that do not exist in the MongoDB collection
       
        Args:
            actual_request: a dict of {field: value} pairs coming from the actual request
                            sent to this endpoint.

        Returns:
            list of invalid field names
        """
        invalid_fields = []
        for field in actual_request.keys():
            if field not in self.db_fields:
                invalid_fields.append(field)
        self.invalid_fields = sorted(invalid_fields)

    def prepare(self):
        """No need to make this a coroutine as it is CPU-bound"""
        # note that variable actual_request is a dict with lists as values, which can be of length
        # greater than one if its key appears more than once in the query.
        # See the note in the docstring to CountHandler._get_valid_queries() for how this is handled.
        logger.info('New query to /count: %s', self.request.query)
        actual_request = parse.parse_qs(self.request.query)
        self._get_invalid_fields(actual_request)
        # no need to spend time getting valid queries if there are any invalid fields
        if not self.invalid_fields:
            self._get_valid_queries()

    async def get(self):
        """This is a coroutine because it is I/O bound, if there are no invalid fields"""
        if self.invalid_fields:
            self.set_status(400, reason="invalid field(s) in query")
            error_message = {'unknown fields': self.invalid_fields}
            logger.error('STATUS 400: %s', error_message)
            self.write(error_message)
            self.set_header('Content-Type', 'application/json')
            self.finish()
        else:
            # motor/Mongo counter awaited
            number = await db.nyc.count_documents(self.valid_queries)
            response = dict(count=number)
            logger.info('STATUS 200: %s' % str(response))
            self.write(response)
            self.set_header('Content-Type', 'application/json')
            self.finish()

if __name__ == "__main__":

    # create motor connection to MongoDB.dogs database
    db = motor.motor_tornado.MotorClient('mongodb://localhost:27017').dogs
  
    # use pymongo once to get a list of fields in one document in the collection
    # it is assumed that all documents in the collection have the same fields
    # TODO: figure out how to do this in motor, so pymongo will no longer be a dependency
    # Note: it's more of a parsimony thing than a timing thing, this only runs once
    # at startup so it's not critical in terms of response
    pymongoclient = MongoClient('mongodb://localhost:27017/')
    one_document = pymongoclient.dogs.nyc.find_one()
    db_fields = {x for x in one_document.keys() if x != '_id'}

    app_settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"),
                    "db": db}

    #define routes/endpoints
    handlers = [
        url(r'/', DefaultHandler),  # if someone hits the bare url without the /count query path
        url(r'/count', CountHandler, dict(db_fields=db_fields)),  # for sole endpoint
        url(r"(.+\.png)", tornado.web.StaticFileHandler, dict(path=app_settings['static_path']))
            # for static path to doggo favicon
    ]

    app = tornado.web.Application(handlers, **app_settings)
    app.listen(port)
    logger.info('app listening on port %d', port)
    print(f'app running on port {port}')  # nice to have visual confirmation in the terminal
    tornado.ioloop.IOLoop.current().start()
