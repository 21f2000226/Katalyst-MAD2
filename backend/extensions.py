from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
#shared extensions for easier importas

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# called flask_cache so it doesn't clash with backend/cache.py helpers
flask_cache = Cache()
