"""Application configuration and environment settings."""

APP_NAME = "CarShowRoom API"
APP_VERSION = "1.0.0"
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/car_showroom"
JWT_SECRET_KEY = "change-me-in-production"
JWT_ALGORITHM = "HS256"
HTTPS_REQUIRED = True
