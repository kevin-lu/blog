"""
Site Setting Model
"""
from datetime import datetime
from app.extensions import db


class SiteSetting(db.Model):
    """Site setting model"""
    
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_name = db.Column(db.String(100), unique=True, nullable=False)
    key_value = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'key_name': self.key_name,
            'key_value': self.key_value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def get_settings_dict(cls):
        """Get all settings as a dictionary with key_name as key"""
        settings = cls.query.all()
        return {setting.key_name: setting.key_value for setting in settings}
    
    @classmethod
    def get_value(cls, key_name, default=None):
        """Get a single setting value by key_name"""
        setting = cls.query.filter_by(key_name=key_name).first()
        return setting.key_value if setting else default
    
    @classmethod
    def set_value(cls, key_name, key_value, description=None):
        """Set or update a setting value"""
        setting = cls.query.filter_by(key_name=key_name).first()
        
        if setting:
            setting.key_value = key_value
            if description:
                setting.description = description
        else:
            setting = cls(
                key_name=key_name,
                key_value=key_value,
                description=description
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<SiteSetting {self.key_name}>'
