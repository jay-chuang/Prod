from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from flask_ldap3_login.forms import LDAPLoginForm


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={'autofocus': True, 'placeholder': 'Enter User'})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={'autofocus': True, 'placeholder': 'Enter Password'})
    remember_me = BooleanField('Rememeber Me')
    submit = SubmitField('Sign In')
#
#
# @ldap_manager.save_user
# def save_user(dn, username, data, memberships):
#     """
#     Function to save authenticated user details.
#     :param dn:
#     :param username:
#     :param data:
#     :param memberships:
#     :return:
#     """
#     return {
#         'dn': dn,
#         'username': username,
#         'data': data,
#         'memberships': memberships,
#     }


class UploadBoll(FlaskForm):
    # file = FileField('送货单', validators=[FileField(), FileAllowed(['xls','xlsx'])])
    file = FileField('送货单', validators=[FileAllowed(['xls','xlsx'])])


class Search_Fystboll(FlaskForm):
    pallet_num = StringField('Pallet Number', validators=[DataRequired()])
    submit = SubmitField('Search')