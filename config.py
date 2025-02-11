import os
import psycopg2
from dotenv import load_dotenv
from flask_ldap3_login import LDAP3LoginManager
from flask_ldap3_login.forms import LDAPLoginForm
# from flask_login import FloginManager, login_user, UserMixin, logout_user, current_user

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Jay-will-Never-Right1'
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    PER_PAGE = 8
    # SQLALCHEMY_DATABASE =  'psycopg2' + \
    #     '://' + os.getenv('DB_USER') + \
    #     ':' + os.getenv('DB_PASSWORD') + \
    #     '@' + os.getenv('DB_HOST')  + \
    #     ':' + os.getenv('DB_PORT')+ \
    #      "\\" + os.getenv('DB_NAME')
    # SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
    # DATABASE_USER = os.environ.get('DATABASE_USER')
    # DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
    # DATABASE_HOST = os.environ.get('DATABASE_HOST')
    # DATABASE_PORT = os.environ.get('DATABASE_PORT')
    # DATABASE_NAME = os.environ.get('DATABASE_NAME')
    # SQLALCHEMY_DATABASE_URI = psycopg2.connect(host=os.getenv('B_HOST'), dbname=os.getenv('DB_NAME'),
    #                         user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
    #                         port=os.getenv('DB_PORT'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Configuration of LDAP
    # Hostname of your LDAP server
    LDAP_HOST = 'ldap://192.168.80.13:389'
    # Base DN of your directory
    LDAP_BASE_DN = 'dc=ritramagroup, dc=local'
    # Users DN to be prepended t the Base DN
    LDAP_USER_DN = 'ou=Users Account'
    # Goups DN to be prepended to the Base DN
    LDAP_GROUP_DN = 'ou=groups'

    # The Username to bind to LDAP
    LDAP_BIND_USER_DN = None  # set if binding requires a user

    # The password of Username to bind to LDAP
    LDAP_BIND_USER_PASSWORD = None


    # The RDN attribute for your user schema on LDAP
    LDAP_USER_RDN_ATTR = 'uid'

    # The Attribute you want users to authenticate to LDAP with.
    LDAP_USER_LOGIN_ATTR = 'uid'
    # LDAP bind authenticatication type
    LDAP_BIND_AUTHENTICATION_TYPE = 'SIMPLE'

    #
    LDAP_BIND_DIRECT_CREDENTIALS = True
    LDAP_USER = 'au-zhangjay'
    LDAP_USER_PASSWORD = 'LoveChina.2024'
    LDAP_USER_SEARCH_BASE = 'ou=users,dc=ritramagroup,dc=local'
    LDAP_USER_SEARCH_FILTER = '(uid=%s)'

    # ldap_manager = LDAP3LoginManager(app)
    # ldap_manager = LoginManager(app)
    # login_manager.login_view = 'login'
    # login_mananger.session_protection = 'strong'
