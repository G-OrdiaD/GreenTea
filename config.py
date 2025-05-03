import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////Users/echobravo/greenhouse-monitoring/instance/greenhouse.db?check_same_thread=False')
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    SESSION_PROTECTION = "strong"
    TWILIO_SID = os.getenv('TWILIO_SID')
    TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
    TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
    WTF_CSRF_ENABLED = False