import os

from dotenv import load_dotenv

load_dotenv()


def _build_mysql_uri(
    default_host: str = 'localhost',
    default_port: str = '3306',
    default_name: str = 'orange_portfolio',
    default_user: str = 'root',
    default_password: str = '',
) -> str:
    return (
        f'mysql+pymysql://{os.environ.get("DB_USER", default_user)}:'
        f'{os.environ.get("DB_PASSWORD", default_password)}@'
        f'{os.environ.get("DB_HOST", default_host)}:'
        f'{os.environ.get("DB_PORT", default_port)}/'
        f'{os.environ.get("DB_NAME", default_name)}'
    )


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', 'http://localhost:5173')

    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_BASE_URL = os.environ.get('ALPHA_VANTAGE_BASE_URL', 'https://www.alphavantage.co/query')

    COGNITO_REGION = os.environ.get('COGNITO_REGION')
    COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
    COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    CACHE_TYPE = 'SimpleCache'
    COGNITO_REGION = 'us-east-1'
    COGNITO_USER_POOL_ID = 'us-east-1_testpool'
    COGNITO_APP_CLIENT_ID = 'test-client-id'
    ALPHA_VANTAGE_API_KEY = 'test-api-key'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _build_mysql_uri()
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _build_mysql_uri(
        default_host='',
        default_port='3306',
        default_name='',
        default_user='',
        default_password='',
    )
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
}


def get_config(env: str):
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)
