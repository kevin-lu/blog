"""
Donation Setting Model
"""
from datetime import datetime
from app.extensions import db


class DonationSetting(db.Model):
    """Donation setting model"""
    
    __tablename__ = 'donation_settings'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), default='支持博主', nullable=False)
    description = db.Column(db.Text, comment='描述文案')
    wechat_qr = db.Column(db.String(500), comment='微信收款码 URL')
    alipay_qr = db.Column(db.String(500), comment='支付宝收款码 URL')
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'wechat_qr': self.wechat_qr,
            'alipay_qr': self.alipay_qr,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def get_current(cls):
        """Get current donation setting"""
        return cls.query.filter_by(enabled=True).first()
