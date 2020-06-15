### gunicorn -b localhost:8000 -w 4 microblog:app
### https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world



from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from datetime import datetime
import calendar
import pandas as pd

app = Flask(__name__)
app.config.from_object(Config)

#### Instrument Database
conn = pymysql.connect('www.nano.kmitl.ac.th', 'kaswat', '00bird00', 'test')


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
    current_month = int(now.strftime('%m'))
    current_month_text = now.strftime('%B')
    current_year = int(now.strftime('%Y'))
    current_date = now.strftime('%d')

    with conn:
        cur = conn.cursor()
        sql = "SELECT * FROM SEM WHERE EXTRACT(MONTH FROM `instru_date`) = %s AND EXTRACT(YEAR FROM `instru_date`) = %s"
        cur.execute(sql, (current_month, current_year))
        db_all = cur.fetchall()
    db_pd = pd.DataFrame.from_dict(db_all)
    date_booked = []
    morning_booked = []
    afternoon_booked = []
    for i in range(len(db_pd)):
        dd = datetime.strptime(str(db_pd.iloc[i, 7]), '%Y-%m-%d')
        date_booked.append(int(dd.strftime('%d')))
        morning_booked.append(int(db_pd.iloc[i, 8]))
        afternoon_booked.append(int(db_pd.iloc[i, 9]))

    status = []
    cal = calendar.TextCalendar(calendar.SUNDAY)
    for i in cal.itermonthdays(current_year, current_month):
        temp = []
        temp.append(i)
        if int(i) == 0:
            temp.append('noday')
        else:
            if calendar.weekday(current_year, current_month, i) == 5 or calendar.weekday(current_year, current_month,
                                                                                         i) == 6:
                temp.append('weekend')
            elif i in date_booked:
                index = date_booked.index(i)
                if morning_booked[index] == 1 and afternoon_booked[index] == 1:
                    temp.append('Full')
                if morning_booked[index] == 1 and afternoon_booked[index] == 0:
                    temp.append('Morning')
                if morning_booked[index] == 0 and afternoon_booked[index] == 1:
                    temp.append('Afternoon')
            else:
                temp.append(' ')
        status.append(temp)

    total_week = len(status) / 7

    return render_template('index.html', data=db_all, user=username, month=current_month_text, mon=current_month,
                           year=current_year, status=status, total=int(total_week))


@app.route('/show/<string:year>-<string:month>', methods=['GET'])
def show_next(year,month):
    if 'username' in session:
        username = session['username']
    else:
        username = None

    text = year+'-'+month+'-01'
    now = datetime.strptime(text,"%Y-%m-%d")
    current_month = int(now.strftime('%m'))
    current_month_text = now.strftime('%B')
    current_year = int(now.strftime('%Y'))

    with conn:
        cur = conn.cursor()
        sql = "SELECT * FROM SEM WHERE EXTRACT(MONTH FROM `instru_date`) = %s AND EXTRACT(YEAR FROM `instru_date`) = %s"
        cur.execute(sql, (current_month, current_year))
        db_all = cur.fetchall()
    db_pd = pd.DataFrame.from_dict(db_all)
    date_booked = []
    morning_booked = []
    afternoon_booked = []
    for i in range(len(db_pd)):
        dd = datetime.strptime(str(db_pd.iloc[i, 7]), '%Y-%m-%d')
        date_booked.append(int(dd.strftime('%d')))
        morning_booked.append(int(db_pd.iloc[i, 8]))
        afternoon_booked.append(int(db_pd.iloc[i, 9]))

    status = []
    cal = calendar.TextCalendar(calendar.SUNDAY)
    for i in cal.itermonthdays(current_year, current_month):
        temp = []
        temp.append(i)
        if int(i) == 0:
            temp.append('noday')
        else:
            if calendar.weekday(current_year, current_month, i) == 5 or calendar.weekday(current_year, current_month,
                                                                                         i) == 6:
                temp.append('weekend')
            elif i in date_booked:
                index = date_booked.index(i)
                if morning_booked[index] == 1 and afternoon_booked[index] == 1:
                    temp.append('Full')
                if morning_booked[index] == 1 and afternoon_booked[index] == 0:
                    temp.append('Morning')
                if morning_booked[index] == 0 and afternoon_booked[index] == 1:
                    temp.append('Afternoon')
            else:
                temp.append(' ')
        status.append(temp)

    total_week = len(status) / 7

    return render_template('index.html', data=db_all, user=username, month=current_month_text, mon=current_month,
                           year=current_year, status=status, total=int(total_week))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
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
                    return redirect(url_for('home'))
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


@app.route('/user')
def user():
    if 'username' in session:
        username = session['username']

        now = datetime.now()
        current_month = int(now.strftime('%m'))
        current_month_text = now.strftime('%B')
        current_year = int(now.strftime('%Y'))
        current_date = now.strftime('%d')

        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM SEM WHERE EXTRACT(MONTH FROM `instru_date`) = %s AND EXTRACT(YEAR FROM `instru_date`) = %s AND username = %s "
            cur.execute(sql, (current_month, current_year, username))
            db_all = cur.fetchall()
        db_pd = pd.DataFrame.from_dict(db_all)
        date_booked = []
        morning_booked = []
        afternoon_booked = []
        for i in range(len(db_pd)):
            dd = datetime.strptime(str(db_pd.iloc[i, 7]), '%Y-%m-%d')
            date_booked.append(int(dd.strftime('%d')))
            morning_booked.append(int(db_pd.iloc[i, 8]))
            afternoon_booked.append(int(db_pd.iloc[i, 9]))

        status = []
        cal = calendar.TextCalendar(calendar.SUNDAY)
        for i in cal.itermonthdays(current_year, current_month):
            temp = []
            temp.append(i)
            if int(i) == 0:
                temp.append('noday')
            else:
                if calendar.weekday(current_year, current_month, i) == 5 or calendar.weekday(current_year,
                                                                                             current_month,
                                                                                             i) == 6:
                    temp.append('weekend')
                elif i in date_booked:
                    index = date_booked.index(i)
                    if morning_booked[index] == 1 and afternoon_booked[index] == 1:
                        temp.append('Full')
                    if morning_booked[index] == 1 and afternoon_booked[index] == 0:
                        temp.append('Morning')
                    if morning_booked[index] == 0 and afternoon_booked[index] == 1:
                        temp.append('Afternoon')
                else:
                    temp.append(' ')
            status.append(temp)

        total_week = len(status) / 7

        return render_template('user.html', data=db_all, user=username, month=current_month_text, mon=current_month,
                               year=current_year, status=status, total=int(total_week))

    else:
        username = None
        return render_template('error.html')


@app.route('/user/<string:year>-<string:month>', methods=['GET'])
def user_next(year,month):
    if 'username' in session:
        username = session['username']

        text = year + '-' + month + '-01'
        now = datetime.strptime(text, "%Y-%m-%d")
        current_month = int(now.strftime('%m'))
        current_month_text = now.strftime('%B')
        current_year = int(now.strftime('%Y'))

        with conn:
            cur = conn.cursor()
            sql = "SELECT * FROM SEM WHERE EXTRACT(MONTH FROM `instru_date`) = %s AND EXTRACT(YEAR FROM `instru_date`) = %s AND username = %s "
            cur.execute(sql, (current_month, current_year, username))
            db_all = cur.fetchall()
        db_pd = pd.DataFrame.from_dict(db_all)
        date_booked = []
        morning_booked = []
        afternoon_booked = []
        for i in range(len(db_pd)):
            dd = datetime.strptime(str(db_pd.iloc[i, 7]), '%Y-%m-%d')
            date_booked.append(int(dd.strftime('%d')))
            morning_booked.append(int(db_pd.iloc[i, 8]))
            afternoon_booked.append(int(db_pd.iloc[i, 9]))

        status = []
        cal = calendar.TextCalendar(calendar.SUNDAY)
        for i in cal.itermonthdays(current_year, current_month):
            temp = []
            temp.append(i)
            if int(i) == 0:
                temp.append('noday')
            else:
                if calendar.weekday(current_year, current_month, i) == 5 or calendar.weekday(current_year,
                                                                                             current_month,
                                                                                             i) == 6:
                    temp.append('weekend')
                elif i in date_booked:
                    index = date_booked.index(i)
                    if morning_booked[index] == 1 and afternoon_booked[index] == 1:
                        temp.append('Full')
                    if morning_booked[index] == 1 and afternoon_booked[index] == 0:
                        temp.append('Morning')
                    if morning_booked[index] == 0 and afternoon_booked[index] == 1:
                        temp.append('Afternoon')
                else:
                    temp.append(' ')
            status.append(temp)

        total_week = len(status) / 7

        return render_template('user.html', data=db_all, user=username, month=current_month_text, mon=current_month,
                               year=current_year, status=status, total=int(total_week))

    else:
        username = None
        return render_template('error.html')


@app.route('/add')
def add_form():
    if 'username' in session:
        user = session['username']
        return render_template('add.html', user=user)
    else:
        user = None
        return render_template('error.html')


@app.route('/insert', methods=['POST'])
def insert():
    user = session['username']
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        phone = request.form['phone']
        email = request.form['email']
        instru_date = request.form['instru_date']
        time_1 = request.form['time_1']
        time_2 = request.form['time_2']
        time = request.form.getlist('time')

        with conn:
            cur = conn.cursor()
            sql = "INSERT INTO `SEM` (`username`,`name`,`department`,`phone`,`email`,`instru_date`,`instru_1`,`instru_2`,`book_date`) values(%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)"
            cur.execute(sql, (user, name, department, phone, email, instru_date, time_1, time_2))
            conn.commit()
    return redirect(url_for('home'))


@app.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    with conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM `SEM` where id = %s", (id))
        conn.commit()
    return redirect(url_for('home'))


@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        department = request.form['department']
        phone = request.form['phone']
        email = request.form['email']
        instru_date = request.form['instru_date']
        time = request.form.getlist('time')
        if 'time_1' in time:
            time_1 = 1
        else:
            time_1 = 0
        if 'time_2' in time:
            time_2 = 1
        else:
            time_2 = 0
        with conn:
            cur = conn.cursor()
            sql = "UPDATE `SEM` SET name=%s, department=%s, phone=%s, email=%s, instru_date=%s, instru_1=%s, instru_2=%s, book_date=CURRENT_TIMESTAMP  WHERE id=%s"
            cur.execute(sql, (name, department, phone, email, instru_date, time_1, time_2, id))
            conn.commit()
    return redirect(url_for('home'))


@app.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        phone = request.form['phone']
        email = request.form['email']
        instru_date = request.form['instru_date']
        instru_date = datetime.strptime(instru_date, '%d-%m-%Y').date()
        time = request.form.getlist('time')
        if 'time_1' in time:
            time_1 = 1
        else:
            time_1 = 0
        if 'time_2' in time:
            time_2 = 1
        else:
            time_2 = 0

        if time_1 == 0 and time_2 == 0:
            text = 'กรุณาระบุเวลาที่ต้องการใช้เครื่องมือ'
            return redirect(url_for('booking_error', message=text))

        now = datetime.now()
        diff = instru_date - now.date()
        if diff.days <= 0:
            text = "ไม่สามารถทำการจองเครื่องมือย้อนหลังได้"
            return redirect(url_for('booking_error', message=text))

        with conn:
            cur = conn.cursor()
            sql = "SELECT COUNT(*) FROM `SEM` WHERE `instru_date`=%s "
            cur.execute(sql, (instru_date))
            all = cur.fetchone()
            if 0 in all:  # ไม่เจอ = ว่าง
                return redirect(url_for('booking_confirm', name=name, department=department, phone=phone, email=email,
                                        instru_date=instru_date, time_1=time_1, time_2=time_2))
            else:
                if time_1 == 1 and time_2 == 0:
                    cur = conn.cursor()
                    sql = "SELECT COUNT(*) FROM `SEM` WHERE `instru_date`=%s AND `instru_1`=%s "
                    cur.execute(sql, (instru_date, time_1))
                    all = cur.fetchone()
                    if 0 in all:  # ไม่เจอ = ว่าง
                        return redirect(
                            url_for('booking_confirm', name=name, department=department, phone=phone, email=email,
                                    instru_date=instru_date, time_1=time_1, time_2=time_2))
                    else:
                        text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                        return redirect(url_for('booking_error', message=text))
                elif time_1 == 0 and time_2 == 1:
                    cur = conn.cursor()
                    sql = "SELECT COUNT(*) FROM `SEM` WHERE `instru_date`=%s AND `instru_2`=%s "
                    cur.execute(sql, (instru_date, time_2))
                    all = cur.fetchone()
                    if 0 in all:  # ไม่เจอ = ว่าง
                        return redirect(
                            url_for('booking_confirm', name=name, department=department, phone=phone, email=email,
                                    instru_date=instru_date, time_1=time_1, time_2=time_2))
                    else:
                        text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                        return redirect(url_for('booking_error', message=text))
                elif time_1 == 1 and time_2 == 1:
                    cur = conn.cursor()
                    sql = "SELECT COUNT(*) FROM `SEM` WHERE `instru_date`=%s AND (`instru_1`=%s OR `instru_2`=%s) "
                    cur.execute(sql, (instru_date, time_1, time_2))
                    all = cur.fetchone()
                    if 0 in all:  # ไม่เจอ = ว่าง
                        return redirect(
                            url_for('booking_confirm', name=name, department=department, phone=phone, email=email,
                                    instru_date=instru_date, time_1=time_1, time_2=time_2))
                    else:
                        text = 'วัน/เวลาที่ทำการจองไม่ว่าง'
                        return redirect(url_for('booking_error', message=text))


@app.route('/booking_error')
def booking_error():
    message = request.args.get('message')
    return render_template('booking_error.html', message=message)


@app.route('/booking_confirm')
def booking_confirm():
    name = request.args.get('name')
    department = request.args.get('department')
    phone = request.args.get('phone')
    email = request.args.get('email')
    instru_date = request.args.get('instru_date')
    time_1 = request.args.get('time_1')
    time_2 = request.args.get('time_2')
    return render_template('booking_confirm.html', name=name, department=department, phone=phone, email=email,
                           instru_date=instru_date, time_1=time_1, time_2=time_2)


if __name__ == "__main__":
    app.run(debug=True)
