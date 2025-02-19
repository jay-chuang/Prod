from barcode import get_barcode_class, Code128
from barcode.writer import ImageWriter
from flask import send_file
from io import BytesIO
from PIL import Image
import base64
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError
import config
from config import Config
from flask import redirect, url_for
from app import db, login_manager, ldap_manager
from app.models import Users


def generate_code128(barcode_data):
    buffer = BytesIO()
    Code128(barcode_data, writer=ImageWriter()).write(buffer)
    barcode_image = Image.open(buffer)
    buffered = BytesIO()
    barcode_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f'<img  src="data:image/png;base64,{img_str}" alt="Barcode"   />'
    # # get code 128 class
    # code128 = get_barcode_class('code128')
    # # create code 128 object
    # barcode = code128(data, writer=ImageWriter())
    # # generate picture and save to the temp file
    # buffer = BytesIO()
    #
    # # filename = f'{data}.png'
    # barcode.save(buffer)
    # buffer.seek(0)
    # return buffer
    # # return picture file
    # # return send_file(filename, mimetype='image/png')


users = {}


# declare a user loader for flask-login
# Simply returns the user if it exists in our database, otherwise returns None
@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return users[user_id]
    return None


# declare the user saver for flask-ldap3-login
# this method is called whenever a LDAPLoginForm() successfully validates.
# Here you have to save the user, and return it so it can be used in the login controller.
@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    id=int(data.get("uidNumber"))
    user=Users.query.filter_by(id=id).first()
    if not user:
        user=Users(
            id=int(id),
            dn=dn,
            username=username,
            email=data['mail'],
            firstname=data['givenName'],
            lastname=data['sn']
        )

        db.session.add(user)
        db.session.commit(0)
    return user


def ldap_authenticate(username, password):
    try:
        # create server object
        server = Server(Config.LDAP_HOST, port=Config.LDAP_PORT, get_info=ALL)
        # 1st step, bind the administrator user to search users' DN
        with Connection(server, user=Config.LDAP_BIND_DN, password=Config.LDAP_BIND_USER_PASSWORD) as conn:
            search_filter = f'({Config.LDAP_USER_SEARCH_ATTR}={username})'
            conn.search(search_base=Config.LDAP_BASE_DN,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=['*'])   # get all attributes
            if len(conn.entries) == 0:
                return None, None  # the user is not exist

            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn

        # the 2nd step, use username and password to authenticate user information
        with Connection(server, user=user_dn, password=password) as conn:
            if conn.bind():
                # get user information
                user_info = {
                    'dn': user_dn,
                    'username': username,
                    'display_name': user_entry.displayName.value,
                    'email': user_entry.mail.value,
                    'groups': user_entry.memeberOf.value if 'memberOf' in user_entry else []
                }
                return user_dn, user_info
            else:
                return None, None
    except Exception as e:
        print(f"LDAP Error: {e}")
        return None, None


def global_ldap_authentication(user_name, user_pwd):
    """
    Function: global LDAP authentication
    Purpose: Make a connection to encrypted LDAP server.

    :param ** Manadatory Positional Parameters
    user_name: LDAP user name
    :param user_pwd:  LDAP user password
    :return: None
    """

    # fetch the username and password
    ldap_user_name = user_name.strip()
    ldap_user_pwd = user_pwd.strip()

    # ldap server host name and port
    ldap_server = Config.LDAP_HOST

    #DN
    root_dn = Config.LDAP_USER_DN

    # User
    user = f'cn={ldap_user_name},{root_dn}'

    print(user)
    server = Server(ldap_server, get_info=ALL)

    connection = Connection(server,
                            user=user,
                            password=ldap_user_pwd)
    if not connection.bind():
        print(f"*** Cannot bind to ldap server: {connection.last_error}")
        l_success_msg = f'** Faild Authentication: {connection.last_error}'
    else:
        print(f" *** Successful bind to ldap server")
        l_success_msg = 'Success'
    return redirect(url_for('/upload_boll'))
