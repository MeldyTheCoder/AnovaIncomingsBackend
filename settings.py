import os


BASE_DIR = os.path.dirname(__file__)

SECRET = os.getenv('SECRET', 'eriogheruitghoijghgbufhjg')

HOST = os.getenv('HOST', '0.0.0.0')

PORT = int(os.getenv('PORT', 8080))

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://kirill:1234@localhost:5433/garant')

