import sqlite3 as sql
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime, timedelta
import pytz

# 한국 시간대로 설정
KST = pytz.timezone('Asia/Seoul')

# 현재 시간을 한국 시간대로 변환
now_kst = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'database.db'

def datetimeformat(value, format='%Y/%m/%d %H:%M'):

    return datetime.strptime(value, '%Y-%m-%dT%H:%M').strftime(format)

# Jinja2 필터 등록
app.jinja_env.filters['datetimeformat'] = datetimeformat

def get_db():
    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    return conn

@app.route('/')
def home():
    login = session.get('login', False)
    username = session.get('username', '')
    return render_template('bar.html', login=login, username=username)

@app.route('/club-recruitment')
def club_recruitment():
    return render_template('club-recruitment.html')

@app.route('/general-board')
def general_board():
    return render_template('general-board.html')

PER_PAGE = 10

@app.route('/left_board')
def left_board():
    login = session.get('login', False)
    page = request.args.get('page', 1, type=int)
    posts = load_left_board_list()
    
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_posts = posts[start:end]
    
    total_posts = len(posts)
    total_pages = (total_posts + PER_PAGE - 1) // PER_PAGE
    
    return render_template('left_board.html', left_board_list=paginated_posts, page=page, total_pages=total_pages, login=login)

@app.route('/left_board_add', methods=('GET', 'POST'))
def left_board_add():
    if request.method == 'POST':
        title = request.form['title']
        context = request.form['context']
        username = session.get('name')
        
        if not title or not context:
            flash('Title and Content are required!')
        else:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO leftboard (title, context, username, created_at) VALUES (?, ?, ?, ?)", (title, context, username, now_kst))
            conn.commit()
            return redirect(url_for('left_board'))
    
    return redirect(url_for('left_board'))

def load_left_board_list():
    conn = get_db()
    cur = conn.cursor()
    left_board_list = []
    try:
        cur.execute("SELECT id, title, context, username, created_at FROM leftboard ORDER BY created_at DESC")
        rows = cur.fetchall()
        for row in rows:
            left_board_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()    
    return left_board_list

@app.route('/left_board/<int:post_id>', methods=('GET', 'POST'))
def left_board_detail(post_id):
    login = session.get('login', False)
    conn = get_db()
    cur = conn.cursor()
    
    # 게시물 가져오기
    cur.execute('SELECT * FROM leftboard WHERE id = ?', (post_id,))
    post = cur.fetchone()
    
    # 댓글 가져오기
    cur.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY created_at DESC', (post_id,))
    comments = cur.fetchall()

    if request.method == 'POST':
        comment_text = request.form['comment_text']
        username = session.get('name', '')
        
        if not comment_text:
            flash('Comment cannot be empty!')
        else:
            cur.execute("INSERT INTO comments (post_id, comment_text, username, created_at) VALUES (?, ?, ?, ?)", (post_id, comment_text, username, now_kst))
            conn.commit()
            return redirect(url_for('left_board_detail', post_id=post_id))
    
    cur.close()
    conn.close()
    
    return render_template('left_board_detail.html', post=post, comments=comments, login=login)

@app.route('/daily')
def daily():
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/mypage')
def mypage():
    login = session.get('login', False)
    if login==False:
        return redirect(url_for('login'))

    user_info = load_user_info()
    applied_soccer, applied_basketball, applied_tennis, applied_vs = load_applied()
    added_soccer, added_basketball, added_tennis, added_vs = load_added()

    return render_template('mypage.html', user_info=user_info, login=login,
                           applied_soccer=applied_soccer, applied_basketball=applied_basketball, applied_tennis=applied_tennis, applied_vs=applied_vs,
                           added_soccer=added_soccer, added_basketball=added_basketball, added_tennis=added_tennis, added_vs=added_vs)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    try:
        email = session.get('username', '')
        cur.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        session.clear()
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('home'))

def load_user_info():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    user_info = ()

    try:
        login = session.get('login', False)
        email = session.get('username', '')
        cur.execute("SELECT email, username, major, team, manager FROM users WHERE email = ?", (email,))
        user_info = cur.fetchone()

    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return user_info

def is_Manager():
    user_info = load_user_info()
    if user_info is not None and user_info[4] == "on":
        return True
    else:
        return False
def load_applied():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    applied_list=[]
    applied_soccer=[]
    applied_basketball=[]
    applied_tennis=[]
    applied_vs=[]

    try:
        email = session.get('username', '')
        cur.execute("SELECT matchnum, sports FROM applied WHERE email = ?", (email,))
        rows = cur.fetchall()

        for row in rows:
            applied_list.append(row)

        for i in range(len(applied_list)):
            if applied_list[i][1]=="soccer":
                cur.execute("SELECT * FROM soccer WHERE id = ?", (int(applied_list[i][0]),))
                applied_soccer.append(cur.fetchone())


            if applied_list[i][1]=="basketball":
                cur.execute("SELECT * FROM basketball WHERE id = ?", (int(applied_list[i][0]),))
                applied_basketball.append(cur.fetchone())

            if applied_list[i][1]=="tennis":
                cur.execute("SELECT * FROM tennis WHERE id = ?", (int(applied_list[i][0]),))
                applied_tennis.append(cur.fetchone())

        cur.execute("SELECT * FROM vs WHERE applied_team = ?", (email,))
        rows = cur.fetchall()
        for row in rows:
            applied_vs.append(row)

    except Exception as e:
        print(e)

    finally:
        cur.close()
        conn.close()

    return applied_soccer, applied_basketball, applied_tennis, applied_vs

def load_added():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    added_soccer=[]
    added_basketball=[]
    added_tennis=[]
    added_vs=[]


    if is_Manager():
        try:
            email = session.get('username', '')

            cur.execute("SELECT * FROM soccer WHERE email = ?", (email,)) # email==관리자 이메일
            rows = cur.fetchall()

            for row in rows:
                added_soccer.append(list(row))

            for i in range(len(added_soccer)):
                cur.execute("SELECT email FROM applied WHERE matchnum = ? AND sports = ?", (int(added_soccer[i][0]),"soccer"))
                rows = cur.fetchall()
                temp=[]

                for row in rows:
                    temp.append(row[0])

                added_soccer[i].append(temp)

            cur.execute("SELECT * FROM basketball WHERE email = ?", (email,)) # email==관리자 이메일
            rows = cur.fetchall()

            for row in rows:
                added_basketball.append(list(row))

            for i in range(len(added_basketball)):
                cur.execute("SELECT email FROM applied WHERE matchnum = ? AND sports = ?", (int(added_basketball[i][0]),"basketball"))
                rows = cur.fetchall()
                temp=[]

                for row in rows:
                    temp.append(row[0])

                added_basketball[i].append(temp)

            cur.execute("SELECT * FROM tennis WHERE email = ?", (email,))  # email==관리자 이메일
            rows = cur.fetchall()

            for row in rows:
                added_tennis.append(list(row))

            for i in range(len(added_tennis)):
                cur.execute("SELECT email FROM applied WHERE matchnum = ? AND sports = ?",
                            (int(added_tennis[i][0]), "tennis"))
                rows = cur.fetchall()
                temp = []

                for row in rows:
                    temp.append(row[0])

                added_tennis[i].append(temp)

            cur.execute("SELECT * FROM vs WHERE email = ?", (email,))
            rows = cur.fetchall()
            for row in rows:
                added_vs.append(row)

        except Exception as e:
            print(e)

        finally:
            cur.close()
            conn.close()

    return added_soccer, added_basketball, added_tennis, added_vs


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
            session['username'] = email
            session['name'] = user[3]
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login', login_failed=True))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('username', None)
    session.pop('name', None)
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        major = request.form.get('major')
        team = request.form.get('team')
        manager = request.form.get('is_manager')

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

        conn.execute('INSERT INTO users (username, email, password, major, team, manager) VALUES (?, ?, ?, ?, ?, ?)',
                     (username, email, password, major, team, manager))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/soccer')
def soccer():
    soccer_list, count_dict = load_soccer_list()
    length = len(soccer_list)
    login = session.get('login', False)
    manager = is_Manager()
    return render_template('soccer.html', soccer_list=soccer_list, length=length, count_dict=count_dict, login=login, manager=manager)


@app.route('/soccer_info', methods=['POST'])
def soccer_info():
    if request.method == 'POST':
        try:
            team1 = request.form['team1']
            team2 = request.form['team2']
            time = request.form['timeInput']
            location = request.form['locationInput']
            details = request.form['detailsInput']
            people = request.form['peopleInput']
            email = session.get('username', '')

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO soccer (team1, team2, time, location, details, people, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (team1, team2, time, location, details, people, email))
                conn.commit()
                flash('Submission completed successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Submission failed. Error: {e}', 'danger')
        finally:
            cur.close()
            conn.close()

    return redirect(url_for('soccer'))

@app.route('/soccer_apply', methods=['POST'])
def soccer_apply():
    if request.method == 'POST':
        try:
            matchnum = request.json['matchnum']
            email = session.get('username', '')
            sports ="soccer"

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()

                # 이미 신청했는지 확인
                cur.execute("SELECT * FROM applied WHERE matchnum = ? AND email = ? AND sports = ?", (matchnum, email, sports))
                existing_application = cur.fetchone()

                if existing_application:
                    return jsonify({'error': '이미 신청한 경기입니다.'}), 400

                # 신청하기
                cur.execute("INSERT INTO applied (matchnum, email, sports) VALUES (?, ?, ?)",
                            (matchnum, email, sports))
                conn.commit()
                return jsonify({'message': '신청이 완료되었습니다.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'신청 실패. 오류: {e}'}), 500
        finally:
            conn.close()

    return redirect(url_for('soccer'))


def get_max_soccer_id():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(id) FROM soccer")
        max_id = cur.fetchone()[0]
        return max_id
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def load_soccer_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    soccer_list = []
    count_dict = {}
    max_match_num= get_max_soccer_id()
    now = datetime.now().strftime('%Y-%m-%dT%H:%M')
    try:

        for match_num in range(1, max_match_num + 1):  # 최대 매치 번호까지 반복
            count_query = f'SELECT COUNT(*) FROM applied WHERE matchnum = {match_num} AND sports = "soccer"'
            count = conn.execute(count_query).fetchone()[0]
            count_dict[match_num] = count

        cur.execute("SELECT id, team1, team2, time, location, details, people FROM soccer WHERE time > ?", (now,))
        rows = cur.fetchall()

        for row in rows:
            soccer_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return soccer_list, count_dict

@app.route('/basketball')
def basketball():
    basketball_list, count_dict = load_basketball_list()
    length = len(basketball_list)
    login = session.get('login', False)
    manager = is_Manager()
    return render_template('basketball.html', basketball_list=basketball_list, length=length, count_dict=count_dict, login=login, manager=manager)

@app.route('/basketball_info', methods=['POST'])
def basketball_info():
    if request.method == 'POST':
        try:
            team1 = request.form['team1']
            team2 = request.form['team2']
            time = request.form['timeInput']
            location = request.form['locationInput']
            details = request.form['detailsInput']
            people = request.form['peopleInput']
            email = session.get('username', '')

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO basketball (team1, team2, time, location, details, people, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (team1, team2, time, location, details, people, email))
                conn.commit()
                flash('Submission completed successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Submission failed. Error: {e}', 'danger')
        finally:
            cur.close()
            conn.close()

    return redirect(url_for('basketball'))

@app.route('/basketball_apply', methods=['POST'])
def basketball_apply():
    if request.method == 'POST':
        try:
            matchnum = request.json['matchnum']
            email = session.get('username', '')
            sports ="basketball"

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()

                # 이미 신청했는지 확인
                cur.execute("SELECT * FROM applied WHERE matchnum = ? AND email = ? AND sports = ?", (matchnum, email, sports))
                existing_application = cur.fetchone()

                if existing_application:
                    return jsonify({'error': '이미 신청한 경기입니다.'}), 400

                # 신청하기
                cur.execute("INSERT INTO applied (matchnum, email, sports) VALUES (?, ?, ?)",
                            (matchnum, email, sports))
                conn.commit()
                return jsonify({'message': '신청이 완료되었습니다.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'신청 실패. 오류: {e}'}), 500
        finally:
            conn.close()

    return redirect(url_for('basketball'))

def get_max_basketball_id():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(id) FROM basketball")
        max_id = cur.fetchone()[0]
        return max_id
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()

def load_basketball_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    basketball_list = []
    count_dict = {}
    max_match_num= get_max_basketball_id()
    now = datetime.now().strftime('%Y-%m-%dT%H:%M')
    try:

        for match_num in range(1, max_match_num + 1):  # 최대 매치 번호까지 반복
            count_query = f'SELECT COUNT(*) FROM applied WHERE matchnum = {match_num} AND sports = "basketball"'
            count = conn.execute(count_query).fetchone()[0]
            count_dict[match_num] = count

        cur.execute("SELECT id, team1, team2, time, location, details, people FROM basketball WHERE time > ?", (now,))
        rows = cur.fetchall()

        for row in rows:
            basketball_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return basketball_list, count_dict


@app.route('/tennis')
def tennis():
    tennis_list, count_dict = load_tennis_list()
    length = len(tennis_list)
    login = session.get('login', False)
    manager = is_Manager()
    return render_template('tennis.html', tennis_list=tennis_list, length=length, count_dict=count_dict, login=login, manager=manager)

@app.route('/tennis_info', methods=['POST'])
def tennis_info():
    if request.method == 'POST':
        try:
            team1 = request.form['team1']
            team2 = request.form['team2']
            time = request.form['timeInput']
            location = request.form['locationInput']
            details = request.form['detailsInput']
            people = request.form['peopleInput']
            email = session.get('username', '')

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO tennis (team1, team2, time, location, details, people, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (team1, team2, time, location, details, people, email))
                conn.commit()
                flash('Submission completed successfully.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Submission failed. Error: {e}', 'danger')
        finally:
            cur.close()
            conn.close()

    return redirect(url_for('tennis'))


@app.route('/tennis_apply', methods=['POST'])
def tennis_apply():
    if request.method == 'POST':
        try:
            matchnum = request.json['matchnum']
            email = session.get('username', '')
            sports ="tennis"

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()

                # 이미 신청했는지 확인
                cur.execute("SELECT * FROM applied WHERE matchnum = ? AND email = ? AND sports = ?", (matchnum, email, sports))
                existing_application = cur.fetchone()

                if existing_application:
                    return jsonify({'error': '이미 신청한 경기입니다.'}), 400

                # 신청하기
                cur.execute("INSERT INTO applied (matchnum, email, sports) VALUES (?, ?, ?)",
                            (matchnum, email, sports))
                conn.commit()
                return jsonify({'message': '신청이 완료되었습니다.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'신청 실패. 오류: {e}'}), 500
        finally:
            conn.close()

    return redirect(url_for('tennis'))

def get_max_tennis_id():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(id) FROM tennis")
        max_id = cur.fetchone()[0]
        return max_id
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()

def load_tennis_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    tennis_list = []
    count_dict = {}
    max_match_num= get_max_tennis_id()
    now = datetime.now().strftime('%Y-%m-%dT%H:%M')
    try:

        for match_num in range(1, max_match_num + 1):  # 최대 매치 번호까지 반복
            count_query = f'SELECT COUNT(*) FROM applied WHERE matchnum = {match_num} AND sports = "tennis"'
            count = conn.execute(count_query).fetchone()[0]
            count_dict[match_num] = count

        cur.execute("SELECT id, team1, team2, time, location, details, people FROM tennis WHERE time > ?", (now,))
        rows = cur.fetchall()

        for row in rows:
            tennis_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return tennis_list, count_dict

@app.route('/vs')
def vs():
    vs_list = load_vs_list()
    length = len(vs_list)
    login = session.get('login', False)
    manager = is_Manager()
    return render_template('vs.html', vs_list=vs_list, length=length, login=login, manager=manager)

@app.route('/vs_info', methods=['POST'])
def vs_info():
    if request.method == 'POST':
        try:
            team = request.form['team']
            time = request.form['timeInput']
            location = request.form['locationInput']
            details = request.form['detailsInput']
            email = session.get('username', '')
            sports = request.form['sportsInput']

            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO vs (team, time, location, details, email, sports) VALUES (?, ?, ?, ?, ?, ?)",
                            (team, time, location, details, email, sports))
                con.commit()
                flash('Submission completed successfully.', 'success')
        except Exception as e:
            con.rollback()
            flash(f'Submission failed. Error: {str(e)}', 'danger')
        finally:
            con.close()

    return redirect(url_for('vs'))

@app.route('/vs_apply', methods=['POST'])
def vs_apply():
    if request.method == 'POST':
        try:
            applied_team = session.get('username', '')
            matchnum = request.json['matchnum']

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()

                # 신청하기
                cur.execute("UPDATE vs SET applied_team = ? WHERE id = ?", (applied_team, matchnum))
                conn.commit()
                return jsonify({'message': '신청이 완료되었습니다.'})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'신청 실패. 오류: {e}'}), 500
        finally:
            cur.close()
            conn.close()

    return redirect(url_for('vs'))



@app.route('/search_vs')
def search_vs():
    query = request.args.get('query', '').strip()
    vs_list = search_vs_in_db(query)
    length = len(vs_list)
    login = session.get('login', False)
    manager = is_Manager()
    return render_template('vs.html', vs_list=vs_list, length=length, query=query, login=login, manager=manager)

def search_vs_in_db(query):
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    vs_list = []
    try:
        cur.execute("SELECT team, time, location, details, sports FROM vs WHERE sports LIKE ?", ('%' + query + '%', ))
        rows = cur.fetchall()

        for row in rows:
            vs_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return vs_list


def load_vs_list():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    vs_list = []
    try:
        cur.execute("SELECT team, time, location, details, id, sports FROM vs WHERE applied_team IS NULL")
        rows = cur.fetchall()

        for row in rows:
            vs_list.append(row)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return vs_list



if __name__ == '__main__':
    app.run(debug=True)
