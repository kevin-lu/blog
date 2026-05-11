"""
Admin User Model
"""
from datetime import datetime
from werkzeug.security import check_password_hash
from app.extensions import db
from app.utils.password import hash_password, verify_password


BCRYPT_PREFIXES = ('$2a$', '$2b$', '$2y$')


class Admin(db.Model):
    """Admin user model"""
    
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    avatar = db.Column(db.String(255))
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    operation_logs = db.relationship('OperationLog', backref='admin', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify password"""
        if not self.password_hash:
            return False

        if self.password_hash.startswith(BCRYPT_PREFIXES):
            try:
                return verify_password(password, self.password_hash)
            except (TypeError, ValueError):
                return False

        try:
            return check_password_hash(self.password_hash, password)
        except (TypeError, ValueError):
            return False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Admin {self.username}>'
