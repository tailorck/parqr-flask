import os
from app.utils.utils import create_app


app = create_app(os.environ['FLASK_CONF'])
# parqr = Parqr()
# parser = Parser()
# schema = JsonSchema(app)
#
# logger = logging.getLogger('app')
#
# redis_host = app.config['REDIS_HOST']
# redis_port = app.config['REDIS_PORT']
# redis = Redis(host=redis_host, port=redis_port, db=0)
# scheduler = Scheduler(connection=redis)
# auth = HTTPBasicAuth()
#
# logger.info('Ready to serve requests')
#
# with open('related_courses.json') as f:
#     related_courses = json.load(f)
# CORS(app)