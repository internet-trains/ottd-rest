import logging

logging.basicConfig(level=logging.DEBUG)
from app import init_app

app = init_app()
