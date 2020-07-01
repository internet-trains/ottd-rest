import logging

logging.basicConfig(level=logging.INFO)
from app import init_app

app = init_app()
