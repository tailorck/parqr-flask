
from app.auth import bp
from app.models import User

# defining routes in a blueprint
@bp.route('/login', methods=['GET', 'POST'])
def login():
    return None