from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'database.db'

def generate_matches():
    return [
        {'name': 'Match 1', 'data': 'Data 1', 'location': 'Location 1', 'details': 'Details 1'},
        {'name': 'Match 2', 'data': 'Data 2', 'location': 'Location 2', 'details': 'Details 2'}
    ]


@app.route('/')
def home():
    login = session.get('login', False)
    username = session.get('username', '')
    return render_template('bar.html', login=login, username=username)

@app.route('/daily')
def daily():
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('inputEmail')
        password = request.form.get('inputPassword')

        conn = sql.connect(DATABASE)
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cur.fetchone()
        if user:
            session['login'] = True
            session['username'] = email # session['username']은 이름이 아니라 id를 뜻합니다.
            return redirect(url_for('home'))
        else:
            return '로그인 실패. 다시 시도해주세요.'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        conn = sql.connect(DATABASE)
        cur = conn.cursor()

        existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?',
                                     (username, email)).fetchone()

        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))

        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/soccer')
def soccer():
    soccer_list = load_soccer_list()
    length = len(soccer_list)
    return render_template('soccer.html', soccer_list=soccer_list, length=length)

@app.route('/soccer_info', methods = ['POST', 'GET'])
def soccer_info():
    if request.method == 'POST':
        try:
            match = request.form['matchInput']
            time = request.form['timeInput']
            details = request.form['detailsInput']

            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO soccer (match, time, details) VALUES (?,?,?)",(match, time, details) )
        except:
            con.rollback()
        finally:
            con.close()
    return render_template('soccer.html')

@app.route('/load_soccer_list')
def load_soccer_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    soccer_list = []
    try:
        cur.execute("SELECT * FROM soccer")
        rows = cur.fetchall()

        for row in rows:
            soccer_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return soccer_list

@app.route('/basketball')
def basketball():
    basketball_list = load_basketball_list()
    length = len(basketball_list)
    return render_template('basketball.html', basketball_list=basketball_list, length=length)

@app.route('/basketball_info', methods = ['POST', 'GET'])
def basketball_info():
    if request.method == 'POST':
        try:
            match = request.form['matchInput']
            time = request.form['timeInput']
            details = request.form['detailsInput']

            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO basketball (match, time, details) VALUES (?,?,?)",(match, time, details) )
        except:
            con.rollback()
        finally:
            con.close()
    return render_template('basketball.html')

@app.route('/load_basketball_list')
def load_basketball_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    basketball_list = []
    try:
        cur.execute("SELECT * FROM basketball")
        rows = cur.fetchall()

        for row in rows:
            basketball_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return basketball_list


@app.route('/tennis')
def tennis():
    tennis_list = load_tennis_list()
    length = len(tennis_list)
    return render_template('tennis.html', tennis_list=tennis_list, length=length)

@app.route('/tennis_info', methods = ['POST', 'GET'])
def tennis_info():
    if request.method == 'POST':
        try:
            match = request.form['matchInput']
            time = request.form['timeInput']
            details = request.form['detailsInput']

            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO tennis (match, time, details) VALUES (?,?,?)",(match, time, details) )
        except:
            con.rollback()
        finally:
            con.close()
    return render_template('tennis.html')

@app.route('/load_tennis_list')
def load_tennis_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    tennis_list = []
    try:
        cur.execute("SELECT * FROM tennis")
        rows = cur.fetchall()

        for row in rows:
            tennis_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return tennis_list


@app.route('/vs', methods=['GET', 'POST'])
def vs():
    if request.method == 'POST':  #POST요청 시 검색
        search_term = request.form.get('searchInput')
        #검색한 내용 있는지 찾기
        matches = generate_matches()
        filtered_matches = [match for match in matches if search_term.lower() in match['name'].lower()]
        #결과 있으면 -> 템플릿 렌더링
        if len(filtered_matches) > 0:
            return render_template('vs.html', matches=filtered_matches, search_term=search_term)
        else:
            #검색 결과 없는 경우
            return render_template('vs.html', no_result=True, search_term=search_term)

    else:
        matches = generate_matches()
        return render_template('vs.html', matches=matches, search_term=None)
    


if __name__ == '__main__':
    app.run(debug=True)
