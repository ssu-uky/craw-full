import os
from app import create_app, scrape_and_store_data

app = create_app()

with app.app_context():
    scrape_and_store_data()