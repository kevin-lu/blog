#!/usr/bin/env python3
"""Test donation settings"""
from app import create_app
from app.models.donation import DonationSetting

app = create_app()

with app.app_context():
    settings = DonationSetting.query.all()
    print(f"Total records: {len(settings)}")
    for s in settings:
        print(f"ID: {s.id}, Title: {s.title}, Enabled: {s.enabled}")
