from .admin import admin_bp
from .auth import auth_bp
from .user import user_bp

def init_routes(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')