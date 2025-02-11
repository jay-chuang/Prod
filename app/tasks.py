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
