from flask import Flask, render_template, redirect, url_for, request
import sqlite3 as sql

app = Flask(__name__)

def generate_matches():
    return [
        {'name': 'Match 1', 'data': 'Data 1', 'location': 'Location 1', 'details': 'Details 1'},
        {'name': 'Match 2', 'data': 'Data 2', 'location': 'Location 2', 'details': 'Details 2'}
    ]


@app.route('/')
def home():
    return render_template('bar.html')

@app.route('/daily')
def daily():
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
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

            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO soccer (match, time, details) VALUES (?,?,?)",(match, time, details) )
        except:
            con.rollback()
        finally:
            con.close()
    return render_template('soccer.html')

@app.route('/load_soccer_list')
def load_soccer_list():
    conn = sql.connect('database.db')
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

            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO basketball (match, time, details) VALUES (?,?,?)",(match, time, details) )
        except:
            con.rollback()
        finally:
            con.close()
    return render_template('basketball.html')

@app.route('/load_basketball_list')
def load_basketball_list():
    conn = sql.connect('database.db')
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

            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO tennis (match, time, details) VALUES (?,?,?)",(match, time, details) )
        except:
            con.rollback()
        finally:
            con.close()
    return render_template('tennis.html')

@app.route('/load_tennis_list')
def load_tennis_list():
    conn = sql.connect('database.db')
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
