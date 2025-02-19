from app import app, db, ldap_manager, login_manager
from flask import render_template, flash, redirect, request, url_for, jsonify, send_file, Blueprint, session
from app.forms import LoginForm, UploadBoll, Search_Fystboll
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required
import os
from io import BytesIO
import pandas as pd
from werkzeug.utils import secure_filename
from app.models import Fystboll, Users
# from app.tasks import generate_code128
import barcode
from barcode.writer import ImageWriter
from flask_paginate import Pagination, get_page_parameter
from config import Config
import xlsxwriter
from reportlab.pdfgen import canvas
# 导入颜色供能
from reportlab.lib import colors
from reportlab.lib.units import inch
# 导入reportlab.lib.pagesizes 纸张类型：A4纸 纸张方向：横向
from reportlab.lib.pagesizes import A4, landscape
# 导入reportlab.platypus的表格形式
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Image, PageBreak, Paragraph, Frame
from app.tasks import ldap_authenticate


@login_manager.user_loader
def load_user(dn):
    # 通过DN加载用户
    return Users(dn=dn, username=dn, data={})


@app.route('/')
@app.route('/index')
# @login_required
def index():
    # Redirect users who are not logged in.
    if 'username' in session:
        return render_template('index.html', title='铭传八中上派初级中学', user=session['username'])
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # if form.validate_on_submit():
    #     # Successfully logged in, we can now access teh saved user object via form.user
    #     login_user(user)  # tell flask-login to log them in.
    #     return redirect('/index')
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # authenticate the user
        user = ldap_manager.authenticate(username, password)
        if user:
            session['username'] = username # save the username to session
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html', title='Sign In', form=form)


def get_user_info(username):
    user = ldap_manager.get_user_info_for_username(username)
    if user:
        return {
            'full_name': user.cn,
            'email': user.mail
        }
    return None
#
#
# @app.route('/profile/<username>')
# @login_required
# def profile(username):
#     # 显示用户信息
#     user_info = get_user_info(username)
#     # user_info = {
#     #     'username': current_user.username,
#     #     'email': current_user.data.get('mail', ''),
#     #     'display_name': current_user.data.get('displayname', '')
#     # }
#
#     return render_template('profile.html', username=username, user_info=user_info)


@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')


@app.route('/upload_boll', methods=['GET', 'POST'])
@login_required
def upload_boll():
    upload_form = UploadBoll()
    if upload_form.validate_on_submit():
        filename = upload_form.file.data.filename

        file_path = os.path.join(os.getenv('UPLOAD_FOLDER'), filename)
        # upload_form.file.data.save(os.path.join(save_path, filename))
        upload_form.file.data.save(file_path)
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        # Select specific columns and trim to the first 10 digits if needed
        try:
            df['Pallet'] = df['Pallet']
            df['Item code'] = df['Item code']
            df['Item description'] = df['Item description']
            df['Width'] = df['Width']
            df['Length'] = df['Length']
            df['Quantity'] = df['Quantity']
            df['Coil'] = df['Coil'].astype(str).str[:10]  # Trim to first to 10 characters
            df['Customer'] = df['Customer']
            df['Customer firm name'] = df['Customer firm name']
            df['Date'] = df['Doc. date']
            df['Doc. number'] = df['Doc. number']
            df['Ord. number'] = df['Ord. number']
            df['Ord. date'] = df['Ord. date']

            # Add more columns as needed and apply the same transformation if necessary

            # Convert the data to a list of dictionaries for easy insertion into the database
            records = df[['Pallet', 'Item code', 'Item description', 'Width', 'Length', 'Quantity', 'Coil'
            , 'Customer', 'Customer firm name', 'Doc. date', 'Doc. number', 'Ord. number', 'Ord. date']].to_dict(
                orient='records')

            for record in records:
                db_record = Fystboll(pallet=record['Pallet'], item_code=record['Item code'],
                                     item_description=record['Item description'], width=record['Width'],
                                     length=record['Length'], quantity=record['Quantity'], coil=record['Coil'],
                                     customer=record['Customer'], customer_firm_name=record['Customer firm name'],
                                     date=record['Doc. date'], doc_number=record['Doc. number'],
                                     ord_number=record['Ord. number'],
                                     ord_date=record['Ord. date'])
                db.session.add(db_record)
            db.session.commit()

        except KeyError as e:
            return jsonify({"error": f"Column not found: {str(e)}"}), 400

        return jsonify({"message": "Data successfully uploaded"}), 200
        # return '提交成功！'
    return render_template('upload_boll.html', upload_form=upload_form)


@app.route('/search_fystboll', methods=['GET', 'POST'])
@login_required
def search_fystboll():
    search_fystboll_form = Search_Fystboll()
    if search_fystboll_form.validate_on_submit():

        pallet_number = search_fystboll_form.pallet_num.data
        session['pallet_number'] = pallet_number
        # transfer the data of form to display function
        return redirect(url_for('display_fystboll', pallet_number=pallet_number))
    return render_template('fystboll_search.html', search_fystboll_form=search_fystboll_form)


# search all pallet via pallet number(the number after slash
# @app.route('/display_fystboll/<pallet_number>', methods=['GET', 'POST'])
# def display_fystboll(pallet_number):
@app.route('/display_fystboll', methods=['GET', 'POST'])
@login_required
def display_fystboll():
    # import search form
    # search_fystboll_form = Search_Fystboll()
    # if search_fystboll_form.validate_on_submit():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['PER_PAGE']
    pallet_number = session.get('pallet_number')
        # get the data of pallet
    # pallet_number = search_fystboll_form.pallet_num.data
        # get all data the pallet number like as pallet_number

    fystboll_data = Fystboll.query.filter(Fystboll.pallet.like(f'%{pallet_number}%')).paginate(page=page,
                                                                                                   per_page=per_page,
                                                                                                   error_out=False)
        # transfer the data to fystboll_display.html
    for item in fystboll_data:
        # barcode_path = os.path.join(os.getenv('BARCODE_FOLDER'), f"{item.coil}.png")
        barcode_path = os.path.join(os.getenv('BARCODE_FOLDER'), f"{item.coil}")
        if not os.path.exists(barcode_path): # generate barcode only if it doesn't exist
            ean = barcode.get("code128", str(item.coil), writer=ImageWriter())
            ean.save(barcode_path)
        # return redirect(url_for('print_fystboll', pallet_number=pallet_number))
    return render_template('fystboll_display.html',
                               fystboll_data=fystboll_data, pallet_number=pallet_number)


@app.route('/print_fystboll')
@login_required
def print_fystboll():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['PER_PAGE']
    # pallet_number = request.args.get('pallet_number')
    pallet_number = session.get('pallet_number')
    print_fystboll_data = Fystboll.query.filter(Fystboll.pallet.like(f'%{pallet_number}%')).paginate(page=page,
                                                                                                per_page=per_page,
                                                                                                error_out=False)
    return render_template('print_fystboll.html', print_fystboll_data=print_fystboll_data,
                           pallet_number=pallet_number)


@app.route('/export/excel')
@login_required
def fystboll_excel():
    pallet_number = request.args.get('pallet_number', '')

    fystboll_data = Fystboll.query.filter(Fystboll.pallet.like(f'%{pallet_number}%')).all()

    # create excel in memory
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_meomory': True})
    worksheet = workbook.add_worksheet()

    # add headers
    worksheet.write(0, 0, "Pallet")
    worksheet.write(0, 1, "ItemCode")
    worksheet.write(0, 2, "Item Description")
    worksheet.write(0, 3, "Width")
    worksheet.write(0, 4, "Length")
    worksheet.write(0, 5, "Quantity")
    worksheet.write(0, 6, "Coil")
    worksheet.write(0, 7, "Coil Barcode")

    # add rows
    for row_num, item in enumerate(fystboll_data, start=1):
        image_path = os.path.join(os.getenv('BARCODE_FOLDER'), f"{ item.coil }.png")
        worksheet.write(row_num, 0, item.pallet)
        worksheet.write(row_num, 1, item.item_code)
        worksheet.write(row_num, 2, item.item_description)
        worksheet.write(row_num, 3, item.width)
        worksheet.write(row_num, 4, item.length)
        worksheet.write(row_num, 5, item.quantity)
        worksheet.write(row_num, 6, item.coil)
        # insert image with variable name into the cell
        worksheet.insert_image(row_num, 8, image_path)

    workbook.close()
    output.seek(0)

    return send_file(output, as_attachment=True, download_name=f"{ pallet_number }.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/export/pdf')
@login_required
def fystboll_pdf():
    """从数据库查询数据"""
    pallet_number = request.args.get('pallet_number')
    fystboll_data = db.session.query(Fystboll).filter(Fystboll.pallet.like(f"%{pallet_number}%"))
    data = [(row.pallet, row.item_code, row.item_description, row.width, row.length, row.quantity, row.coil)
            for row in fystboll_data.all()]
    buffer = BytesIO()
    # response = Response(content_type='application/pdf')
    # response.headers['Content-Disposition'] = 'inline; filename="output.pdf"'
    # 创建PDF，并将pdf放入buffer缓存中
    #  pagesize=landscape(A4), 设置纸张类型A4并且为横向（landscape)
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=0.2*inch, bottomMargin=0.2*inch)
    elements = []
    # split pdf to 8 lines per page
    rows_per_page = 9
    page_data = [data[i:i + rows_per_page] for i in range(0, len(data), rows_per_page)]

    company_name = "Ritrama(Hefei) Presure Sensitive Coated Materials Co., Limited"
    company_phone = "T +86 551 63879747| F +86 551 63879737"
    company_address = "No. 33-35, Qingluan Rd, Economic and Technological Development Area"
    company_address_1 = "230601 Hefei Anhui Province, China"
    company_name_ch = "雷特玛（合肥）感压粘合涂层材料有限公司"
    company_phone_ch = "电话：+86 551 63879747 | 传真: +86 551 63879737"
    company_address_ch = "中国 安徽省合肥市经济技术开发区青鸾路33-35号"
    company_logo_path = os.path.join(os.getenv("COMPANY_LOGO_PATH"), "company_logo_FS.png")
    try:
        logo_fs = Image(company_logo_path, width=140, height=40)
    except ImportError:
        logo_fs = Paragraph("No Logo")
    header_table = Table([[logo_fs], [company_name], [company_address], [company_address_1], [company_phone]],
                         colWidths=850)
    elements.append(header_table)
    header_table.setStyle((TableStyle([
        # ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # 表头背景
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # 表头文字颜色
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # 文本居中
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # 表头顶部对齐
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # 表头字体
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),  # 表头底部填充
        # ('SPAN', (0, 0), (1, 1)),
        ('BACKUGROUND', (0, 1), (-1, -1), colors.beige),  # 数据背景色
        # ('GRID', (0, 0), (-1, -1), 1, colors.black),  # 添加网格线
    ])))
    for page in page_data:
        table_data = [["Pallet", "Item Code", "Item Description", "Width", "Length",
                       "Quantity", "Coil", "Coil Barcode"]]
        for row in page:
            image_path = os.path.join(os.getenv('BARCODE_FOLDER'), f"{row[6]}.png")
            pallet, item_code, item_description, width, length, quantity, coil = row

            if os.path.exists(image_path):
                img = Image(image_path, width=100, height=40)
            else:
                img = f"{ row[6] }.png Not Found"

            table_data.append([pallet, item_code, item_description, width, length, quantity, coil, img])

        # 创建表格
        table = Table(table_data, colWidths=[100, 100, 200, 50, 50, 50, 100, 200])

        table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # 表头背景
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # 表头文字颜色
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 文本居中
                    ('VALIGN', (0, 0), (-1, 0), 'TOP'),  # 表头顶部对齐
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # 表头字体
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 5),  # 表头底部填充
                    ('BACKUGROUND', (0, 1), (-1, -1), colors.beige),  # 数据背景色
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),  # 添加网格线

                ]))
        elements.append(table)
        elements.append(PageBreak())

    # 生成PDF
    pdf.build(elements)
    buffer.seek(0)
    # return buffer
    return send_file(buffer, as_attachment=True, download_name=f"{pallet_number}.pdf", mimetype="application/pdf")