app = Flask(__name__)
from flaskext.auth import Auth
auth = Auth(app)