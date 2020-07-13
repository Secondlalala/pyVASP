### kill -HUP masterpid
### gunicorn -D -b www.nano.kmitl.ac.th:9000 -w 5 --threads=4 app:app --timeout 600 --worker-class gevent --worker-tmp-dir /home/kittiphong/instrument/tmp/ --max-requests 500 &
### https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
### gthread

import calendar
from datetime import datetime
import pandas as pd
import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from zipfile import ZipFile
from config import Config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendmail(receiver_address, subject, mail_content):
    sender_address = 'nano@kmitl.ac.th'
    sender_pass = 'nanoKMITL10520'

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = subject
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()


app = Flask(__name__)
app.config.from_object(Config)


def now():
    now = datetime.now()
    now_month = int(now.strftime('%-m'))
    now_year = int(now.strftime('%Y'))
    now_date = int(now.strftime('%d'))
    return now_year, now_month, now_date


#### Instrument Database
conn = pymysql.connect('www.nano.kmitl.ac.th', 'kaswat', '00bird00', 'instrument')


def set_password(self, password):
    self.password_hash = generate_password_hash(password)


def check_password(self, password):
    return check_password_hash(self.password_hash, password)


@app.route('/')
@app.route('/index')
def home():
    if 'username' in session:
        username = session['username']
    else:
        username = None

    now = datetime.now()
    now_month = int(now.strftime('%-m'))
    now_year = int(now.strftime('%Y'))
    now_date = int(now.strftime('%d'))

    return render_template('index.html', user=username, year=now_year, month=now_month)


@app.route('/xrd/<string:year>-<string:month>', methods=['GET'])
def xrd(year, month):
    if 'username' in session:
        username = session['username']
    else:
        username = None

    text = year + '-' + month + '-01'
    display_year_month = datetime.strptime(text, "%Y-%m-%d")
    display_month = int(display_year_month.strftime('%-m'))
    display_month_text = display_year_month.strftime('%B')
    display_year = int(display_year_month.strftime('%Y'))

    with conn:
        cur = conn.cursor()
        sql = " SELECT * FROM booking " \
              " INNER JOIN Users " \
              " ON booking.username = Users.username " \
              " WHERE booking.instrument = %s " \
              " AND EXTRACT(MONTH FROM booking.instru_date) = %s " \
              " AND EXTRACT(YEAR FROM booking.instru_date) = %s " \
              " AND (booking.status = 'Pending' OR booking.status = 'Approve') " \
              " ORDER BY booking.instru_date "
        cur.execute(sql, ('XRD', display_month, display_year))
        db_all = cur.fetchall()
        cur.close()
    db_pd = pd.DataFrame.from_dict(db_all)
    date_booked = []
    book_09 = []
    book_10 = []
    book_11 = []
    book_13 = []
    book_14 = []
    book_15 = []
    for i in range(len(db_pd)):
        dd = datetime.strptime(str(db_pd.iloc[i, 6]), '%Y-%m-%d')
        temp = int(dd.strftime('%d'))
        if temp in date_booked:
            if book_09.pop() == 1:
                book_09.append(1)
            else:
                book_09.append(int(db_pd.iloc[i, 7]))
            if book_10.pop() == 1:
                book_10.append(1)
            else:
                book_10.append(int(db_pd.iloc[i, 8]))
            if book_11.pop() == 1:
                book_11.append(1)
            else:
                book_11.append(int(db_pd.iloc[i, 9]))
            if book_13.pop() == 1:
                book_13.append(1)
            else:
                book_13.append(int(db_pd.iloc[i, 10]))
            if book_14.pop() == 1:
                book_14.append(1)
            else:
                book_14.append(int(db_pd.iloc[i, 11]))
            if book_15.pop() == 1:
                book_15.append(1)
            else:
                book_15.append(int(db_pd.iloc[i, 12]))
        else:
            date_booked.append(int(dd.strftime('%d')))
            book_09.append(int(db_pd.iloc[i, 7]))
            book_10.append(int(db_pd.iloc[i, 8]))
            book_11.append(int(db_pd.iloc[i, 9]))
            book_13.append(int(db_pd.iloc[i, 10]))
            book_14.append(int(db_pd.iloc[i, 11]))
            book_15.append(int(db_pd.iloc[i, 12]))

    status = []
    cal = calendar.TextCalendar(calendar.SUNDAY)
    for i in cal.itermonthdays(display_year, display_month):
        temp = []
        temp.append(i)
        if int(i) == 0:
            temp.append('noday')
            temp.append(' ')
        else:
            if calendar.weekday(display_year, display_month, i) == 5 or calendar.weekday(display_year, display_month,
                                                                                         i) == 6:
                temp.append('weekend')
            elif i in date_booked:
                index = date_booked.index(i)
                temp.append(str(
                    book_09[index] + book_10[index] + book_11[index] + book_13[index] + book_14[index] + book_15[
                        index]))
                free = " "
                if book_09[index] == 0:
                    free = free + '9 '
                if book_10[index] == 0:
                    free = free + '10 '
                if book_11[index] == 0:
                    free = free + '11 '
                if book_13[index] == 0:
                    free = free + '13 '
                if book_14[index] == 0:
                    free = free + '14 '
                if book_15[index] == 0:
                    free = free + '15 '
                temp.append(free)
            else:
                temp.append(' ')
                temp.append(' ')
        status.append(temp)
    total_week = len(status) / 7

    action = []
    now = datetime.now()
    for i in range(len(db_all)):
        instru_date = db_pd.iloc[i, 6]
        diff = instru_date - now.date()
        action.append(int(diff.days))

    return render_template('xrd.html', data=db_all, user=username, month=display_month, month_text=display_month_text,
                           year=display_year, status=status, total=int(total_week), action=action)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    now_year, now_month, now_date = now()
    with conn:
        cur = conn.cursor()
        try:
            _username = request.form['inputUsername']
            _password = request.form['inputPassword']
            cur.execute("SELECT * FROM `Users` WHERE username = %s", (_username))
            data = cur.fetchall()

            if len(data) > 0:
                if str(data[0][3]) == _password:
                    session['username'] = str(data[0][1])
                    return redirect(url_for('user', year=now_year, month=now_month))
                else:
                    return render_template('login.html', title='Sign In')
            else:
                return render_template('login.html', title='Sign In')

        except Exception as e:
            return render_template('login.html', title='Sign In')
        finally:
            cur.close()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/user/<string:year>-<string:month>', methods=['GET'])
def user(year, month):
    if 'username' in session:
        username = session['username']

        text = year + '-' + month + '-01'
        display_year_month = datetime.strptime(text, "%Y-%m-%d")
        display_month = int(display_year_month.strftime('%-m'))
        display_month_text = display_year_month.strftime('%B')
        display_year = int(display_year_month.strftime('%Y'))

        now = datetime.now()
        now_date = int(now.strftime('%d'))

        if username == 'admin':
            with conn:
                cur = conn.cursor()
                sql = " SELECT * FROM booking " \
                      " INNER JOIN Users " \
                      " ON booking.username = Users.username " \
                      " INNER JOIN Instrument_rate " \
                      " ON booking.instrument = Instrument_rate.instrument " \
                      " AND booking.option = Instrument_rate.option " \
                      " WHERE EXTRACT(MONTH FROM booking.instru_date) = %s " \
                      " AND EXTRACT(YEAR FROM booking.instru_date) = %s " \
                      " ORDER BY booking.instru_date "
                cur.execute(sql, (display_month, display_year))
                db_all = cur.fetchall()
                cur.close()
                action = []
            return render_template('admin.html', data=db_all, user=username, month_text=display_month_text,
                                   month=display_month, year=display_year, date=now_date)

        else:
            with conn:
                cur = conn.cursor()
                sql = "SELECT `credit` FROM `Users` WHERE `username` = %s"
                cur.execute(sql, (username))
                temp = cur.fetchone()
                credit = int(temp[0])
            with conn:
                cur = conn.cursor()
                sql = " SELECT * FROM booking " \
                      " INNER JOIN Instrument_rate " \
                      " ON booking.instrument = Instrument_rate.instrument " \
                      " AND booking.option = Instrument_rate.option " \
                      " WHERE EXTRACT(MONTH FROM booking.instru_date) = %s " \
                      " AND EXTRACT(YEAR FROM booking.instru_date) = %s " \
                      " AND booking.username = %s " \
                      " ORDER BY booking.instru_date "
                cur.execute(sql, (display_month, display_year, username))
                db_all = cur.fetchall()
                cur.close()
            db_pd = pd.DataFrame.from_dict(db_all)

            action = []
            now = datetime.now()
            for i in range(len(db_all)):
                instru_date = db_pd.iloc[i, 6]
                diff = instru_date - now.date()
                action.append(int(diff.days))

            return render_template('user.html', data=db_all, user=username, action=action,
                                   month_text=display_month_text, month=display_month, year=display_year, credit=credit,
                                   date=now_date)

    else:
        username = None
        return render_template('denie.html')


@app.route('/add')
def add_form():
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        with conn:
            cur = conn.cursor()
            sql = "SELECT credit FROM Users WHERE username = %s"
            cur.execute(sql, (user))
            num = cur.fetchone()
            credit = num[0]
            cur.close()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT `text` FROM `Instrument_rate` ")
            instru = cur.fetchall()
            cur.close()

            return render_template('add.html', user=user, year=now_year, month=now_month, instru=instru, credit=credit)
    else:
        user = None
        return render_template('denie.html')


@app.route('/edit/<string:id>', methods=['GET'])
def edit(id):
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        with conn:
            cur = conn.cursor()
            sql = " SELECT * FROM booking " \
                  " INNER JOIN Users " \
                  " ON booking.username = Users.username " \
                  " INNER JOIN Instrument_rate " \
                  " ON booking.instrument = Instrument_rate.instrument " \
                  " AND booking.option = Instrument_rate.option " \
                  " WHERE booking.id = %s "
            cur.execute(sql, (id))
            db = cur.fetchall()
            cur.close()
        return render_template('edit.html', user=user, data=db, year=now_year, month=now_month)
    else:
        user = None
        return render_template('denie.html')


@app.route('/insert', methods=['POST'])
def insert():
    user = session['username']
    if request.method == 'POST':
        id = request.form['id']
        if int(id) > 0:
            instrument = request.form['instrument']
            option = request.form['option']
        else:
            instrument = request.form['instrument']
            option = 0
            if instrument == 'XRD-1':
                instrument = 'XRD'
                option = 0
            elif instrument == 'XRD-2':
                instrument = 'XRD'
                option = 1
            elif instrument == 'XRD-3':
                instrument = 'XRD'
                option = 2
            elif instrument == 'XRD-4':
                instrument = 'XRD'
                option = 3

        name = request.form['name']
        phone = request.form['phone']
        material = request.form['material']
        comment = request.form['comment']
        instru_date = request.form['instru_date']
        time_09 = request.form['time_09']
        time_10 = request.form['time_10']
        time_11 = request.form['time_11']
        time_13 = request.form['time_13']
        time_14 = request.form['time_14']
        time_15 = request.form['time_15']
        time = request.form.getlist('time')

        with conn:
            cur = conn.cursor()
            if int(id) > 0:
                sql = " UPDATE `booking` " \
                      " SET name = %s, " \
                      " phone = %s, " \
                      " material = %s, " \
                      " comment = %s " \
                      " book_date = CURRENT_TIMESTAMP " \
                      " WHERE id = %s "
                cur.execute(sql, (name, phone, material, comment, id))
            else:
                sql = " INSERT INTO `booking` " \
                      " (`username`,`name`,`phone`,`material`,`instru_date`," \
                      " `book_09`,`book_10`,`book_11`,`book_13`,`book_14`,`book_15`," \
                      " `book_date`,`status`,`instrument`,`cost`,`option`,`comment`) " \
                      " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,%s,%s,%s,%s,%s) "
                cur.execute(sql, (user, name, phone, material, instru_date, time_09, time_10, time_11, time_13, time_14, time_15, 'Pending', instrument, '0', option, comment))
            conn.commit()
            cur.close()

        with conn:
            cur = conn.cursor()
            cur.execute(" SELECT MAX(id) FROM booking ")
            num = cur.fetchone()
            id = int(num[0])
            cur.close()
        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM `Users` WHERE `username` = %s"
            cur.execute(sql, (user))
            num = cur.fetchone()
            fullname = num[4]
            email = num[2]
            credit = int(num[5])
            cur.close()
        with conn:
            cur = conn.cursor()
            sql = "SELECT `text` FROM `Instrument_rate` WHERE `instrument` = %s AND `option` = %s "
            cur.execute(sql, (instrument, option))
            text = cur.fetchone()
            text = text[0]
            cur.close()


        receiver_address = email
        subject = f'''ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Booking [{id}]'''
        mail_content = f'''เรียน {fullname},

        รายการจองใช้เครื่องมือ {text}

        หมายเลขการจอง : {id}
        ผู้ใช้งานเครื่องมือ : {name}
        สารที่ทดสอบ : {material}
        วันที่ใช้เครื่องมือ : {instru_date}
        บันทึกถึงนักวิทยาศาสตร์ : {comment}

        ขณะนี้คุณมีเครดิตคงเหลือ {credit} บาท

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)

    return redirect(url_for('home'))


@app.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM `booking` where id = %s", (id))
        conn.commit()
        cur.close()
    return redirect(url_for('home'))


@app.route('/cancel/<string:id>', methods=['GET'])
def cancel(id):
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            with conn:
                cur = conn.cursor()
                sql = "UPDATE `booking` SET status = %s, book_date=CURRENT_TIMESTAMP  WHERE id = %s"
                cur.execute(sql, ('Cancel by admin', id))
                conn.commit()
                cur.close()
            with conn:
                cur = conn.cursor()
                sql = "SELECT `username` FROM `booking` WHERE `id` = %s"
                cur.execute(sql, (id))
                temp = cur.fetchone()
                user_booking = temp[0]
                cur.close()
        else:
            with conn:
                cur = conn.cursor()
                sql = "UPDATE `booking` SET status = %s, book_date=CURRENT_TIMESTAMP  WHERE id = %s"
                cur.execute(sql, ('Cancel by user', id))
                conn.commit()
                cur.close()
            user_booking = user

        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM `Users` WHERE `username` = %s"
            cur.execute(sql, (user_booking))
            db = cur.fetchone()
            cur.close()
            email = db[2]
            fullname = db[4]
            credit = int(db[5])
        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM `booking` WHERE `id` = %s"
            cur.execute(sql, (id))
            temp = cur.fetchone()
            cur.close()

        receiver_address = email[0]
        subject = f'''ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Booking cancel [{temp[0]}]'''
        mail_content = f'''เรียน {fullname},

        รายการจองใช้เครื่องมือ {temp[14]} ได้ยกเลิกแล้ว

        หมายเลขการจอง : {temp[0]}
        ผู้ใช้งานเครื่องมือ : {temp[2]}
        วันที่ใช้เครื่องมือ : {temp[6]}

        ค่าใช้จ่าย : {temp[15]}
        ขณะนี้คุณมีเครดิตคงเหลือ {credit} บาท

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        return redirect(url_for('home'))
    else:
        user = None
        return render_template('denie.html')


@app.route('/check', methods=['POST'])
def check():
    now = datetime.now()
    now_month = int(now.strftime('%m'))
    now_year = int(now.strftime('%Y'))

    if 'username' in session:
        user = session['username']
        if request.method == 'POST':
            edit = request.form['edit']
            id = -1
            if edit == '1':
                id = request.form['id']

            instrument = request.form['instrument']
            option = 0
            if instrument == 'XRD-1' :
                instrument = 'XRD'
                option = 0
            elif instrument == 'XRD-2' :
                instrument = 'XRD'
                option = 1
            elif instrument == 'XRD-3' :
                instrument = 'XRD'
                option = 2
            elif instrument == 'XRD-4' :
                instrument = 'XRD'
                option = 3

            with conn:
                cur = conn.cursor()
                sql = "SELECT `text` FROM `Instrument_rate` WHERE `instrument` = %s AND `option` = %s "
                cur.execute(sql, (instrument, option))
                text = cur.fetchone()
                text = text[0]
                cur.close()

            name = request.form['name']
            phone = request.form['phone']
            material = request.form['material']
            comment = request.form['comment']
            ins_date = request.form['instru_date']
            instru_date = datetime.strptime(ins_date, '%Y-%m-%d').date()
            time = request.form.getlist('time')
            if 'time_09' in time or 'time_0912' in time or 'time_0916' in time:
                time_09 = 1
            else:
                time_09 = 0
            if 'time_10' in time or 'time_0912' in time or 'time_0916' in time:
                time_10 = 1
            else:
                time_10 = 0
            if 'time_11' in time or 'time_0912' in time or 'time_0916' in time:
                time_11 = 1
            else:
                time_11 = 0
            if 'time_13' in time or 'time_1316' in time or 'time_0916' in time:
                time_13 = 1
            else:
                time_13 = 0
            if 'time_14' in time or 'time_1316' in time or 'time_0916' in time:
                time_14 = 1
            else:
                time_14 = 0
            if 'time_15' in time or 'time_1316' in time or 'time_0916' in time:
                time_15 = 1
            else:
                time_15 = 0

            time = [time_09, time_10, time_11, time_13, time_14, time_15]
            if time_09 == 0 and time_10 == 0 and time_11 == 0 and time_13 == 0 and time_14 == 0 and time_15 == 0:
                text = 'กรุณาระบุเวลาที่ต้องการใช้เครื่องมือ'
                return render_template('booking_error.html', message=text, user=user, year=now_year, month=now_month)

            now = datetime.now()
            diff = instru_date - now.date()
            if diff.days <= 0:
                text = "ไม่สามารถทำการจองเครื่องมือย้อนหลังได้"
                return render_template('booking_error.html', message=text, user=user, year=now_year, month=now_month)

            with conn:
                cur = conn.cursor()
                sql = "SELECT * FROM `Users` WHERE `username` = %s"
                cur.execute(sql, (user))
                fullname = cur.fetchone()
                fullname = fullname[4]
                credit = fullname[5]
                cur.close()
            if credit <= 0:
                text = "Credit ไม่เพียงพอสำหรับทำการจองเครื่องมือ"
                return render_template('booking_error.html', message=text, user=user, year=now_year, month=now_month)

            with conn:
                cur = conn.cursor()
                sql = " SELECT COUNT(*) FROM `booking` " \
                      " WHERE instrument = %s " \
                      " AND `instru_date` = %s " \
                      " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                      " AND `id` <> %s "
                cur.execute(sql, (instrument, instru_date, id))
                all = cur.fetchone()
                cur.close()
                if 0 in all:  # ไม่เจอ = ว่าง
                    return render_template('booking_confirm.html', id=id, user=user, name=name, phone=phone,
                                           material=material, instru_date=instru_date, time=time, instrument=instrument,
                                           year=now_year, month=now_month, text=text, fullname=fullname, comment=comment)
                else:
                    if time_09 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM `booking` " \
                              " WHERE  instrument = %s " \
                              " AND `instru_date` = %s " \
                              " AND `book_09` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instrument, instru_date, time_09, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('booking_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    if time_10 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM `booking` " \
                              " WHERE  instrument = %s " \
                              " AND `instru_date` = %s " \
                              " AND `book_10` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instrument, instru_date, time_10, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('booking_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    if time_11 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM `booking` " \
                              " WHERE  instrument = %s " \
                              " AND `instru_date` = %s " \
                              " AND `book_11` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instrument, instru_date, time_11, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('booking_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    if time_13 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM `booking` " \
                              " WHERE  instrument = %s " \
                              " AND `instru_date` = %s " \
                              " AND `book_13` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instrument, instru_date, time_13, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('booking_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    if time_14 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM `booking` " \
                              " WHERE  instrument = %s " \
                              " AND `instru_date` = %s " \
                              " AND `book_14` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instrument, instru_date, time_14, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('booking_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    if time_15 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM `booking` " \
                              " WHERE  instrument = %s " \
                              " AND `instru_date` = %s " \
                              " AND `book_15` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instrument, instru_date, time_15, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('booking_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    return render_template('booking_confirm.html', id=id, user=user, name=name, phone=phone,
                                           material=material, instru_date=instru_date, time=time, instrument=instrument,
                                           year=now_year, month=now_month, text=text, fullname=fullname, comment=comment)

    else:
        user = None
        return render_template('denie.html')


@app.route('/today/<string:year>-<string:month>-<string:date>', methods=['GET'])
def today(year, month, date):
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            text = year + '-' + month + '-' + date
            display = datetime.strptime(text, "%Y-%m-%d")
            display_month = int(display.strftime('%-m'))
            display_month_text = display.strftime('%B')
            display_year = int(display.strftime('%Y'))
            display_date = int(display.strftime('%d'))

            now = datetime.now()
            now_date = int(now.strftime('%d'))

            with conn:
                cur = conn.cursor()
                sql = " SELECT * FROM booking " \
                      " INNER JOIN Users " \
                      " ON booking.username = Users.username " \
                      " INNER JOIN Instrument_rate " \
                      " ON booking.instrument = Instrument_rate.instrument " \
                      " AND booking.option = Instrument_rate.option " \
                      " WHERE EXTRACT(MONTH FROM booking.instru_date) = %s " \
                      " AND EXTRACT(YEAR FROM booking.instru_date) = %s " \
                      " AND EXTRACT(DAY FROM booking.instru_date) = %s " \
                      " ORDER BY booking.instrument "
                cur.execute(sql, (display_month, display_year, display_date))
                db_all = cur.fetchall()
                cur.close()
            return render_template('today.html', data=db_all, user=user, month_text=display_month_text,
                                   month=display_month, year=display_year, date=display_date)
        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')


@app.route('/pending')
def pending():
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            now_year, now_month, now_date = now()
            with conn:
                cur = conn.cursor()
                sql = " SELECT * FROM booking " \
                      " INNER JOIN Users " \
                      " ON booking.username = Users.username " \
                      " INNER JOIN Instrument_rate " \
                      " ON booking.instrument = Instrument_rate.instrument " \
                      " AND booking.option = Instrument_rate.option " \
                      " WHERE status = %s " \
                      " ORDER BY booking.instru_date "
                cur.execute(sql, ("Pending"))
                db_all = cur.fetchall()
                cur.close()
            return render_template('pending.html', data=db_all, user=user, year=now_year, month=now_month,
                                   date=now_date)
        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')


@app.route('/topup')
def topup():
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            return render_template('topup.html', user=user, year=now_year, month=now_month, date=now_date)
        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')


@app.route('/top_up', methods=['POST'])
def top_up():
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            if request.method == 'POST':
                user_topup = request.form['username']
                credit_topup = request.form['credit']
                with conn:
                    cur = conn.cursor()
                    sql = "SELECT count(*) FROM `Users` WHERE `username` = %s"
                    cur.execute(sql, (user_topup))
                    temp = cur.fetchone()
                    cur.close()
                if temp[0] == 1:
                    with conn:
                        cur = conn.cursor()
                        sql = "SELECT * FROM `Users` WHERE `username` = %s"
                        cur.execute(sql, (user_topup))
                        temp = cur.fetchone()
                        cur.close()
                        email = temp[2]
                        fullname = temp[4]
                        credit = int(temp[5])
                    credit = credit + int(credit_topup)
                    with conn:
                        cur = conn.cursor()
                        sql = "INSERT INTO `booking` (`username`,`name`,`instru_date`,`book_date`,`status`,`instrument`,`cost`,`option`) values(%s,%s,%s,CURRENT_TIMESTAMP,%s,%s,%s,%s)"
                        cur.execute(sql, (user_topup, user_topup, datetime.now(), 'Approve', 'Top up', credit_topup,'0'))
                        conn.commit()
                        cur.close()
                    with conn:
                        cur = conn.cursor()
                        sql = "UPDATE `Users` SET credit = %s WHERE username = %s"
                        cur.execute(sql, (credit, user_topup))
                        conn.commit()
                        cur.close()
                    receiver_address = email
                    subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Top up successfully"
                    mail_content = f'''เรียน {fullname},
                    
                    รายการเติมเครดิต ({credit_topup} บาท) เสร็จสมบูรณ์
                    ขณะนี้คุณมีเครดิตคงเหลือ {credit:d} บาท
                    
                    ----
                    ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
                    วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
                    '''
                    sendmail(receiver_address, subject, mail_content)
                    return redirect(url_for('today', year=now_year, month=now_month, date=now_date))
                else:
                    text = "ไม่พบ username ในระบบ"
                    return render_template('booking_error.html', message=text, user=user, year=now_year,
                                           month=now_month)

        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')


@app.route('/approve/<string:id>', methods=['GET'])
def approve(id):
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            with conn:
                cur = conn.cursor()
                sql = "SELECT `rating` FROM `Instrument_rate` WHERE `instrument` = %s"
                cur.execute(sql, ('XRD'))
                temp = cur.fetchone()
                rate = int(temp[0])
                cur.close()
            with conn:
                cur = conn.cursor()
                sql = "SELECT * FROM `booking` WHERE `id` = %s"
                cur.execute(sql, (id))
                temp = cur.fetchone()
                cur.close()
                user_booking = temp[1]
                hour = 0
                if temp[7] == 1:
                    hour = hour + 1
                if temp[8] == 1:
                    hour = hour + 1
                if temp[9] == 1:
                    hour = hour + 1
                if temp[10] == 1:
                    hour = hour + 1
                if temp[11] == 1:
                    hour = hour + 1
                if temp[12] == 1:
                    hour = hour + 1
            with conn:
                cur = conn.cursor()
                sql = "SELECT * FROM `Users` WHERE `username` = %s"
                cur.execute(sql, (user_booking))
                num = cur.fetchone()
                cur.close()
                email = num[2]
                fullname = num[4]
                credit = int(num[5])
            credit = credit - (rate * hour)
            with conn:
                cur = conn.cursor()
                sql = "UPDATE `booking` SET `status` = %s, `cost` = %s WHERE id = %s"
                cur.execute(sql, ('Approve', str(-1 * (rate * hour)), id))
                conn.commit()
                cur.close()
            with conn:
                cur = conn.cursor()
                sql = "UPDATE `Users` SET credit = %s WHERE username = %s"
                cur.execute(sql, (credit, user_booking))
                conn.commit()
                cur.close()
            receiver_address = email
            subject = f'''ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Booking approve [{temp[0]}]'''
            mail_content = f'''เรียน {fullname},

            รายการจองใช้เครื่องมือ {temp[14]} ได้รับอนุมัติแล้ว
            
            หมายเลขการจอง : {temp[0]}
            ผู้ใช้งานเครื่องมือ : {temp[2]}
            วันที่ใช้เครื่องมือ : {temp[6]}
            
            ค่าใช้จ่าย : {int(-1 * rate * hour)}
            ขณะนี้คุณมีเครดิตคงเหลือ {credit} บาท

            ----
            ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
            วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
            '''
            sendmail(receiver_address, subject, mail_content)
            return redirect(url_for('pending'))
        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')



@app.route('/creatuser')
def creatuser():
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            return render_template('createuser.html', user=user, year=now_year, month=now_month, date=now_date)
        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')


@app.route('/create_user', methods=['POST'])
def create_user():
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            if request.method == 'POST':
                user_create = request.form['username']
                fullname_create = request.form['fullname']
                email_create = request.form['email']
                phone_create = request.form['phone']
                credit_create = request.form['credit']

                with conn:
                    cur = conn.cursor()
                    sql = "SELECT count(*) FROM `Users` WHERE `username` = %s"
                    cur.execute(sql, (user_create))
                    temp = cur.fetchone()
                    cur.close()
                if temp[0] != 0:
                    text = "username มีอยู่แล้วในระบบ"
                    return render_template('booking_error.html', message=text, user=user, year=now_year,
                                           month=now_month)

                import secrets
                import string
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for i in range(8))

                with conn:
                    cur = conn.cursor()
                    sql = "INSERT INTO `Users` (`username`,`password`,`email`,`credit`,`fullname`,`phone`) values(%s,%s,%s,%s,%s,%s)"
                    cur.execute(sql, (user_create, password, email_create, credit_create, fullname_create, phone_create))
                    conn.commit()
                    cur.close()
                with conn:
                    cur = conn.cursor()
                    sql = "INSERT INTO `booking` (`username`,`name`,`instru_date`,`book_date`,`status`,`instrument`,`cost`,`option`) values(%s,%s,%s,CURRENT_TIMESTAMP,%s,%s,%s,%s)"
                    cur.execute(sql, (user_create, user_create, datetime.now(), 'Approve', 'Top up', credit_create,'0'))
                    conn.commit()
                    cur.close()
                receiver_address = email_create
                subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Create user"
                mail_content = f'''เรียน {fullname_create},

                ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี ได้ทำการสร้างผู้ใช้งานเรียบร้อยแล้ว

                กรุณาใช้ Secret password ต่อไปนี้ในการเปลี่ยน password
                Secret password : {password}

                ----
                ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
                วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
                '''
                sendmail(receiver_address, subject, mail_content)
                return render_template('password.html', username=user_create, email=email_create, year=now_year, month=now_month)
        else:
            user = None
            return render_template('denie.html')
    else:
        user = None
        return render_template('denie.html')


@app.route('/reset')
def reset():
    now_year, now_month, now_date = now()
    return render_template('reset.html', year=now_year, month=now_month)


@app.route('/reset_password', methods=['POST'])
def reset_password():
    now_year, now_month, now_date = now()
    if request.method == 'POST':
        user_create = request.form['username']
        email_create = request.form['email']
        phone_create = request.form['phone']

        with conn:
            cur = conn.cursor()
            sql = "SELECT count(*) FROM Users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] == 0:
            text = "ไม่พบ username ในระบบ"
            return render_template('error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = "SELECT email FROM Users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != email_create:
            text = "email ไม่ตรงกับ username ในระบบ"
            return render_template('error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = "SELECT phone FROM Users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != phone_create:
            text = "หมายเลขโทรศัพท์ ไม่ตรงกับ username ในระบบ"
            return render_template('error.html', message=text, user=user, year=now_year, month=now_month)

        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))

        with conn:
            cur = conn.cursor()
            sql = " UPDATE Users " \
                  " SET password = %s " \
                  " WHERE username = %s "
            cur.execute(sql, (password, user_create))
            conn.commit()
            cur.close()
        receiver_address = email_create
        subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Reset Password"
        mail_content = f'''เรียน {user_create},

        กรุณาใช้ Secret password ต่อไปนี้ในการเปลี่ยน password

        Secret password : {password}

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        return render_template('password.html', username=user_create, email=email_create, phone=phone_create, year=now_year, month=now_month)


@app.route('/password', methods=['POST'])
def password():
    now_year, now_month, now_date = now()
    if request.method == 'POST':
        user_create = request.form['username']
        pass_create = request.form['password1']
        pass_re = request.form['password2']
        secret = request.form['secret']
        email_create = request.form['email']

        if pass_create != pass_re:
            text = "password ไม่ตรงกัน"
            return render_template('error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = "SELECT password FROM Users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != secret:
            text = "Secret password ไม่ตรงกัน"
            return render_template('error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = " UPDATE Users " \
                  " SET password = %s " \
                  " WHERE username = %s "
            cur.execute(sql, (pass_create, user_create))
            conn.commit()
            cur.close()
        receiver_address = email_create
        subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Create user"
        mail_content = f'''เรียน {user_create},

        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี ได้ทำการเปลี่ยนรหัสผ่านแล้ว

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        text = "ระบบได้ทำการเปลี่ยน password เรียบร้อยแล้ว"
        return render_template('ok.html', message=text, user=user, year=now_year, month=now_month)


@app.route('/export')
def export():
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM `Users` ")
                users = cur.fetchall()
                cur.close()
                users_db = pd.DataFrame.from_dict(users)
                users_db.to_excel('users.xlsx')
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM `booking` ")
                booking = cur.fetchall()
                cur.close()
                booking_db = pd.DataFrame.from_dict(booking)
                booking_db.to_excel('booking.xlsx')
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM `Instrument_rate` ")
                booking = cur.fetchall()
                cur.close()
                rating_db = pd.DataFrame.from_dict(booking)
                rating_db.to_excel('rating.xlsx')
            with ZipFile('nanokmitl_instrument.zip', 'w') as zipObj:
                zipObj.write('users.xlsx')
                zipObj.write('booking.xlsx')
                zipObj.write('rating.xlsx')
            path = "nanokmitl_instrument.zip"
            return send_file(path, as_attachment=True)
        else:
            user = None
            return render_template('error.html')
    else:
        user = None
        return render_template('error.html')




#######################################################################################
######################################   FESEM   ######################################
#######################################################################################
@app.route('/fesem/<string:year>-<string:month>', methods=['GET'])
def fesem(year, month):
    if 'username' in session:
        username = session['username']
    else:
        username = None

    now = datetime.now()
    now_month = int(now.strftime('%-m'))
    now_year = int(now.strftime('%Y'))
    now_date = int(now.strftime('%d'))

    text = year + '-' + month + '-01'
    display_year_month = datetime.strptime(text, "%Y-%m-%d")
    display_month = int(display_year_month.strftime('%-m'))
    display_month_text = display_year_month.strftime('%B')
    display_year = int(display_year_month.strftime('%Y'))

    with conn:
        cur = conn.cursor()
        sql = " SELECT * FROM fesem_booking " \
              " INNER JOIN fesem_users " \
              " ON fesem_booking.username = fesem_users.username " \
              " WHERE (fesem_booking.status = 'Pending' OR fesem_booking.status = 'Approve') " \
              " AND EXTRACT(MONTH FROM fesem_booking.instru_date) = %s " \
              " AND EXTRACT(YEAR FROM fesem_booking.instru_date) = %s " \
              " ORDER BY fesem_booking.instru_date "
        cur.execute(sql, (display_month, display_year))
        db_all = cur.fetchall()
        cur.close()
    db_pd = pd.DataFrame.from_dict(db_all)
    date_booked = []
    book_09 = []
    book_13 = []

    for i in range(len(db_pd)):
        dd = datetime.strptime(str(db_pd.iloc[i, 10]), '%Y-%m-%d')
        temp = int(dd.strftime('%d'))
        if temp in date_booked:
            if book_09.pop() == 1:
                book_09.append(1)
            else:
                book_09.append(int(db_pd.iloc[i, 11]))
            if book_13.pop() == 1:
                book_13.append(1)
            else:
                book_13.append(int(db_pd.iloc[i, 12]))
        else:
            date_booked.append(int(dd.strftime('%d')))
            book_09.append(int(db_pd.iloc[i, 11]))
            book_13.append(int(db_pd.iloc[i, 12]))

    status = []
    cal = calendar.TextCalendar(calendar.SUNDAY)
    for i in cal.itermonthdays(display_year, display_month):
        temp = []
        temp.append(i)
        if int(i) == 0:
            temp.append('noday')
            temp.append(' ')
        else:
            if calendar.weekday(display_year,display_month,i) == 5 or calendar.weekday(display_year,display_month,i) == 6:
                temp.append('weekend')
            elif i in date_booked:
                index = date_booked.index(i)
                temp.append(str( book_09[index] + book_13[index] ))
                free = " "
                if book_09[index] == 0:
                    free = free + '9 '
                if book_13[index] == 0:
                    free = free + '13 '
                temp.append(free)
            else:
                temp.append(' ')
                temp.append(' ')
        status.append(temp)
    total_week = len(status) / 7

    action = []
    now = datetime.now()
    for i in range(len(db_all)):
        instru_date = db_pd.iloc[i, 10]
        diff = instru_date - now.date()
        action.append(int(diff.days))

    return render_template('fesem.html', data=db_all, user=username, month=display_month, month_text=display_month_text,
                           year=display_year, status=status, total=int(total_week), action=action)


@app.route('/fesem_login')
def fesem_login():
    return render_template('fesem_login.html')


@app.route('/fesem_validateLogin', methods=['POST'])
def fesem_validateLogin():
    now_year, now_month, now_date = now()
    with conn:
        cur = conn.cursor()
        try:
            _username = request.form['inputUsername']
            _password = request.form['inputPassword']
            cur.execute("SELECT * FROM `fesem_users` WHERE username = %s", (_username))
            data = cur.fetchall()
            cur.close()

            if len(data) > 0:
                if str(data[0][3]) == _password:
                    session['username'] = str(data[0][1])
                    return redirect(url_for('fesem_user', year=now_year, month=now_month))
                else:
                    return render_template('fesem_login.html', title='Sign In')
            else:
                return render_template('fesem_login.html', title='Sign In')

        except Exception as e:
            return render_template('fesem_login.html', title='Sign In')
        finally:
            cur.close()


@app.route('/fesem_logout')
def fesem_logout():
    now_year, now_month, now_date = now()
    session.clear()
    return redirect(url_for('fesem', year=now_year, month=now_month))


@app.route('/fesem_createuser')
def fesem_createuser():
    now_year, now_month, now_date = now()
    return render_template('fesem_createuser.html', year=now_year, month=now_month)


@app.route('/fesem_create_user', methods=['POST'])
def fesem_create_user():
    now_year, now_month, now_date = now()
    if request.method == 'POST':
        user_create = request.form['username']
        fullname_create = request.form['fullname']
        email_create = request.form['email']
        affiliation_create = request.form['affiliation']
        phone_create = request.form['phone']

        with conn:
            cur = conn.cursor()
            sql = "SELECT count(*) FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != 0:
            text = "username มีอยู่แล้วในระบบ"
            return render_template('fesem_error.html', message=text, user=user, year=now_year,
                                   month=now_month)

        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))

        with conn:
            cur = conn.cursor()
            sql = "INSERT INTO fesem_users (`username`,`password`,`fullname`,`email`,`affiliation`,`phone`) values(%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (user_create, password, fullname_create, email_create, affiliation_create, phone_create))
            conn.commit()
            cur.close()
        receiver_address = email_create
        subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Create user"
        mail_content = f'''เรียน {fullname_create},

        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี ได้ทำการสร้างผู้ใช้งานเรียบร้อยแล้ว

        กรุณาใช้ Secret password ต่อไปนี้ในการเปลี่ยน password

        Secret password : {password}

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        return render_template('fesem_password.html', user=user_create, email=email_create, phone=phone_create, year=now_year, month=now_month)


@app.route('/fesem_reset')
def fesem_reset():
    now_year, now_month, now_date = now()
    return render_template('fesem_reset.html', year=now_year, month=now_month)


@app.route('/fesem_reset_password', methods=['POST'])
def fesem_reset_password():
    now_year, now_month, now_date = now()
    if request.method == 'POST':
        user_create = request.form['username']
        email_create = request.form['email']
        phone_create = request.form['phone']

        with conn:
            cur = conn.cursor()
            sql = "SELECT count(*) FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] == 0:
            text = "ไม่พบ username ในระบบ"
            return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = "SELECT email FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != email_create:
            text = "email ไม่ตรงกับ username ในระบบ"
            return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = "SELECT phone FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != phone_create:
            text = "หมายเลขโทรศัพท์ ไม่ตรงกับ username ในระบบ"
            return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))

        with conn:
            cur = conn.cursor()
            sql = " UPDATE fesem_users " \
                  " SET password = %s " \
                  " WHERE username = %s "
            cur.execute(sql, (password, user_create))
            conn.commit()
            cur.close()
        receiver_address = email_create
        subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Reset Password"
        mail_content = f'''เรียน {user_create},

        กรุณาใช้ Secret password ต่อไปนี้ในการเปลี่ยน password

        Secret password : {password}

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        return render_template('fesem_password.html', user=user_create, email=email_create, phone=phone_create, year=now_year, month=now_month)


@app.route('/fesem_password', methods=['POST'])
def fesem_password():
    now_year, now_month, now_date = now()
    if request.method == 'POST':
        user_create = request.form['username']
        pass_create = request.form['password1']
        pass_re = request.form['password2']
        secret = request.form['secret']
        email_create = request.form['email']

        if pass_create != pass_re:
            text = "password ไม่ตรงกัน"
            return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = "SELECT password FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user_create))
            temp = cur.fetchone()
            cur.close()
        if temp[0] != secret:
            text = "Secret password ไม่ตรงกัน"
            return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

        with conn:
            cur = conn.cursor()
            sql = " UPDATE fesem_users " \
                  " SET password = %s " \
                  " WHERE username = %s "
            cur.execute(sql, (pass_create, user_create))
            conn.commit()
            cur.close()
        receiver_address = email_create
        subject = "ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Create user"
        mail_content = f'''เรียน {user_create},

        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี ได้ทำการเปลี่ยนรหัสผ่านแล้ว

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        text = "ระบบได้ทำการเปลี่ยน password เรียบร้อยแล้ว"
        return render_template('fesem_ok.html', message=text, user=user, year=now_year, month=now_month)


@app.route('/fesem_user/<string:year>-<string:month>', methods=['GET'])
def fesem_user(year, month):
    if 'username' in session:
        username = session['username']

        text = year + '-' + month + '-01'
        display_year_month = datetime.strptime(text, "%Y-%m-%d")
        display_month = int(display_year_month.strftime('%-m'))
        display_month_text = display_year_month.strftime('%B')
        display_year = int(display_year_month.strftime('%Y'))

        now = datetime.now()
        now_date = int(now.strftime('%d'))

        if username == 'admin':
            with conn:
                cur = conn.cursor()
                sql = " SELECT * FROM fesem_booking " \
                      " INNER JOIN fesem_users " \
                      " ON fesem_booking.username = fesem_users.username " \
                      " WHERE EXTRACT(MONTH FROM fesem_booking.instru_date) = %s " \
                      " AND EXTRACT(YEAR FROM fesem_booking.instru_date) = %s " \
                      " ORDER BY fesem_booking.instru_date "
                cur.execute(sql, (display_month, display_year))
                db_all = cur.fetchall()
                cur.close()
            return render_template('fesem_admin.html', data=db_all, user=username, month_text=display_month_text,
                                   month=display_month, year=display_year, date=now_date)

        else:
            with conn:
                cur = conn.cursor()
                sql = " SELECT * FROM fesem_booking " \
                      " WHERE EXTRACT(MONTH FROM fesem_booking.instru_date) = %s " \
                      " AND EXTRACT(YEAR FROM fesem_booking.instru_date) = %s " \
                      " AND fesem_booking.username = %s " \
                      " ORDER BY fesem_booking.instru_date "
                cur.execute(sql, (display_month, display_year, username))
                db_all = cur.fetchall()
                cur.close()
            db_pd = pd.DataFrame.from_dict(db_all)

            action = []
            now = datetime.now()
            for i in range(len(db_all)):
                instru_date = db_pd.iloc[i, 10]
                diff = instru_date - now.date()
                action.append(int(diff.days))

            return render_template('fesem_user.html', data=db_all, user=username, action=action,
                                   month_text=display_month_text, month=display_month, year=display_year,
                                   date=now_date)

    else:
        username = None
        return render_template('error.html')


@app.route('/fesem_add')
def fesem_add():
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        return render_template('fesem_add.html', user=user, year=now_year, month=now_month)
    else:
        user = None
        return render_template('error.html')


@app.route('/fesm_check', methods=['POST'])
def fesem_check():
    now = datetime.now()
    now_month = int(now.strftime('%m'))
    now_year = int(now.strftime('%Y'))

    if 'username' in session:
        user = session['username']
        if request.method == 'POST':
            edit = request.form['edit']
            id = -1
            if edit == '1':
                id = request.form['id']

            instrument = request.form['instrument']
            material = request.form['material']
            size = request.form['size']
            examine = request.form['examine']
            number = request.form['number']
            coating = request.form['coating']
            comment = request.form['comment']
            ins_date = request.form['instru_date']
            instru_date = datetime.strptime(ins_date, '%Y-%m-%d').date()
            time = request.form.getlist('time')
            if 'time_0912' in time :
                time_09 = 1
            else:
                time_09 = 0
            if 'time_1316' in time :
                time_13 = 1
            else:
                time_13 = 0

            time = [time_09, time_13]
            if time_09 == 0 and time_13 == 0 :
                text = 'กรุณาระบุเวลาที่ต้องการใช้เครื่องมือ'
                return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

            now = datetime.now()
            diff = instru_date - now.date()
            if diff.days <= 0:
                text = "ไม่สามารถทำการจองเครื่องมือย้อนหลังได้"
                return render_template('fesem_error.html', message=text, user=user, year=now_year, month=now_month)

            with conn:
                cur = conn.cursor()
                sql = "SELECT `fullname` FROM `fesem_users` WHERE `username` = %s"
                cur.execute(sql, (user))
                fullname = cur.fetchone()
                fullname = fullname[0]
                cur.close()

            with conn:
                cur = conn.cursor()
                sql = " SELECT COUNT(*) FROM fesem_booking " \
                      " WHERE instru_date = %s " \
                      " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                      " AND `id` <> %s "
                cur.execute(sql, (instru_date, id))
                all = cur.fetchone()
                cur.close()
                if 0 in all:  # ไม่เจอ = ว่าง
                    return render_template('fesem_confirm.html', id=id, user=user, size=size, examine=examine, coating=coating,
                                           material=material, instru_date=instru_date, time=time, instrument=instrument,
                                           year=now_year, month=now_month, number=number, fullname=fullname, comment=comment)
                else:
                    if time_09 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM fesem_booking " \
                              " WHERE `instru_date` = %s " \
                              " AND `book_09` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instru_date, time_09, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('fesem_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)
                    if time_13 == 1:
                        cur = conn.cursor()
                        sql = " SELECT COUNT(*) FROM fesem_booking " \
                              " WHERE `instru_date` = %s " \
                              " AND `book_13` = %s " \
                              " AND (`status` = 'Pending' OR `status` = 'Approve') " \
                              " AND `id` <> %s "
                        cur.execute(sql, (instru_date, time_13, id))
                        all = cur.fetchone()
                        cur.close()
                        if 0 not in all:  # เจอ = ไม่ว่าง
                            text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                            return render_template('fesem_error.html', message=text, user=user, year=now_year,
                                                   month=now_month)

                    return render_template('fesem_confirm.html', id=id, user=user, size=size, examine=examine, coating=coating,
                                           material=material, instru_date=instru_date, time=time, instrument=instrument,
                                           year=now_year, month=now_month, number=number, fullname=fullname, comment=comment)

    else:
        user = None
        return render_template('error.html')


@app.route('/fesem_insert', methods=['POST'])
def fesem_insert():
    now_year, now_month, now_date = now()
    user = session['username']
    if request.method == 'POST':
        id = request.form['id']
        instrument = request.form['instrument']
        material = request.form['material']
        size = request.form['size']
        examine = request.form['examine']
        number = request.form['number']
        coating = request.form['coating']
        comment = request.form['comment']
        instru_date = request.form['instru_date']
        time_09 = request.form['time_09']
        time_13 = request.form['time_13']

        with conn:
            cur = conn.cursor()
            if int(id) > 0:
                sql = " UPDATE fesem_booking " \
                      " SET material = %s, " \
                      " size = %s, " \
                      " examine = %s, " \
                      " number = %s, " \
                      " coating = %s, " \
                      " comment = %s, " \
                      " book_date = CURRENT_TIMESTAMP " \
                      " WHERE id = %s "
                cur.execute(sql, (material, size, examine, number, coating, comment, id))
            else:
                print(coating)
                sql = " INSERT INTO fesem_booking " \
                      " (`username`,`instrument`,`material`,`size`,`examine`,`number`,`coating`, " \
                      " `comment`,`instru_date`,`book_09`,`book_13`, " \
                      " `book_date`,`status`) " \
                      " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,%s) "
                cur.execute(sql, (user,instrument,material,size,examine,number,coating,comment,instru_date,time_09,time_13,'Pending'))
            conn.commit()
            cur.close()

        with conn:
            cur = conn.cursor()
            cur.execute(" SELECT MAX(id) FROM fesem_booking ")
            num = cur.fetchone()
            id = int(num[0])
            cur.close()
        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user))
            num = cur.fetchone()
            fullname = num[4]
            email = num[2]
            cur.close()


        receiver_address = email
        subject = f'''ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Booking [{id}]'''
        mail_content = f'''เรียน {fullname},

        รายการจองใช้เครื่องมือ {instrument}

        หมายเลขการจอง : {id}
        ผู้ทำการจอง : {fullname}
        สารที่ทดสอบ : {material}
        ขนาดของชิ้นงาน : {size}
        สิ่งที่ต้องการทดสอบ : {examine}
        บันทึกถึงนักวิทยาศาสตร์ : {comment}
        วันที่ใช้เครื่องมือ : {instru_date}

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)

    return redirect(url_for('fesem_user', year=now_year, month=now_month))


@app.route('/fesem_edit/<string:id>', methods=['GET'])
def fesem_edit(id):
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        with conn:
            cur = conn.cursor()
            sql = " SELECT * FROM fesem_booking " \
                  " INNER JOIN fesem_users " \
                  " ON fesem_booking.username = fesem_users.username " \
                  " WHERE fesem_booking.id = %s "
            cur.execute(sql, (id))
            db = cur.fetchall()
            cur.close()
        return render_template('fesem_edit.html', user=user, data=db, year=now_year, month=now_month)
    else:
        user = None
        return render_template('error.html')


@app.route('/fesem_cancel/<string:id>', methods=['GET'])
def fesem_cancel(id):
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            with conn:
                cur = conn.cursor()
                sql = "UPDATE `booking` SET status = %s, book_date=CURRENT_TIMESTAMP  WHERE id = %s"
                cur.execute(sql, ('Cancel by admin', id))
                conn.commit()
                cur.close()
            with conn:
                cur = conn.cursor()
                sql = "SELECT `username` FROM `booking` WHERE `id` = %s"
                cur.execute(sql, (id))
                temp = cur.fetchone()
                user_booking = temp[0]
                cur.close()
        else:
            with conn:
                cur = conn.cursor()
                sql = "UPDATE fesem_booking SET status = %s, book_date=CURRENT_TIMESTAMP  WHERE id = %s"
                cur.execute(sql, ('Cancel by user', id))
                conn.commit()
                cur.close()
            user_booking = user

        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM fesem_users WHERE `username` = %s"
            cur.execute(sql, (user_booking))
            db = cur.fetchone()
            cur.close()
            email = db[2]
            fullname = db[4]
        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM fesem_booking WHERE `id` = %s"
            cur.execute(sql, (id))
            temp = cur.fetchone()
            cur.close()

        receiver_address = email
        subject = f'''ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Booking cancel [{temp[0]}]'''
        mail_content = f'''เรียน {fullname},

        รายการจองใช้เครื่องมือ {temp[2]} ได้ยกเลิกแล้ว

        หมายเลขการจอง : {temp[0]}
        ผู้ใช้งานเครื่องมือ : {fullname}
        วันที่ใช้เครื่องมือ : {temp[10]}

        ----
        ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
        วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
        '''
        sendmail(receiver_address, subject, mail_content)
        return redirect(url_for('fesem_user', year=now_year, month=now_month))
    else:
        user = None
        return render_template('error.html')


@app.route('/fesem_approve/<string:id>', methods=['GET'])
def fesem_approve(id):
    now_year, now_month, now_date = now()
    if 'username' in session:
        user = session['username']
        if user == 'admin':
            with conn:
                cur = conn.cursor()
                sql = "SELECT * FROM fesem_booking WHERE `id` = %s"
                cur.execute(sql, (id))
                temp = cur.fetchone()
                cur.close()
                user_booking = temp[1]
            with conn:
                cur = conn.cursor()
                sql = "SELECT * FROM fesem_users WHERE `username` = %s"
                cur.execute(sql, (user_booking))
                num = cur.fetchone()
                cur.close()
                email = num[2]
                fullname = num[4]
            with conn:
                cur = conn.cursor()
                sql = "UPDATE fesem_booking SET `status` = %s WHERE id = %s"
                cur.execute(sql, ('Approve', id))
                conn.commit()
                cur.close()

            receiver_address = email
            subject = f'''ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี - Booking approve [{temp[0]}]'''
            mail_content = f'''เรียน {fullname},

            รายการจองใช้เครื่องมือ {temp[2]} ได้รับอนุมัติแล้ว

            หมายเลขการจอง : {temp[0]}
            ผู้ใช้งานเครื่องมือ : {fullname}
            วันที่ใช้เครื่องมือ : {temp[10]}

            ----
            ศูนย์บริการเครื่องมือวิเคราะห์วัสดุและนาโนเทคโนโลยี
            วิทยาลัยนาโนเทคโนโลยีพระจอมเกล้าลาดกระบัง
            '''
            sendmail(receiver_address, subject, mail_content)
            return redirect(url_for('fesem_user', year=now_year, month=now_month))
        else:
            user = None
            return render_template('error.html')
    else:
        user = None
        return render_template('error.html')


if __name__ == "__main__":
    app.run(debug=True)