from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'kthcitat_secret_2004')

DB_PATH = os.path.join(os.path.dirname(__file__), 'kthcitat.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_institutions():
    conn = get_db()
    rows = conn.execute("SELECT ID, Namn FROM Institution ORDER BY Namn").fetchall()
    conn.close()
    return rows


def get_persons(typ, institution_id):
    conn = get_db()
    query = "SELECT ID, Namn FROM Person WHERE Typ = ?"
    params = [typ]
    if str(institution_id) != '-1':
        query += " AND Institution = ?"
        params.append(institution_id)
    query += " ORDER BY Namn"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


@app.route('/', methods=['GET', 'POST'])
def index():
    institutions = get_institutions()
    typ = request.args.get('typ', '1')
    institution_id = request.args.get('institution', '-1')
    persons = get_persons(typ, institution_id)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'visa':
            inst = request.form.get('institution', '-1')
            person = request.form.get('person', '-1')
            inlagt = request.form.get('inlagt', '-1')
            t = request.form.get('typ', '1')
            return redirect(url_for('show_citat', institution=inst, person=person,
                                    inlagt=inlagt, search='form', typ=t))
        elif action == 'sok':
            query = request.form.get('query', '')
            return redirect(url_for('show_citat', institution='-1', person='-1',
                                    inlagt='-1', search='text', query=query))
        elif action == 'cascade':
            typ = request.form.get('typ', '1')
            institution_id = request.form.get('institution', '-1')
            persons = get_persons(typ, institution_id)
            return redirect(url_for('index', typ=typ, institution=institution_id))

    return render_template('index.html',
                           institutions=institutions,
                           persons=persons,
                           selected_typ=typ,
                           selected_institution=institution_id,
                           logged_in='user_id' in session)


@app.route('/show_citat')
def show_citat():
    institution = request.args.get('institution', '-1')
    person = request.args.get('person', '-1')
    inlagt = request.args.get('inlagt', '-1')
    search = request.args.get('search', 'form')
    typ = request.args.get('typ', '1')
    query = request.args.get('query', '')

    conn = get_db()
    citat_list = []

    if search == 'text':
        rows = conn.execute("""
            SELECT Citat.citat, Person.Namn, Institution.Namn, Citat.tid, Citat.notering
            FROM Citat, Person, Institution
            WHERE Citat.person = Person.ID
              AND Person.Institution = Institution.ID
              AND Citat.citat LIKE ?
            ORDER BY Citat.tid DESC
        """, (f'%{query}%',)).fetchall()
        for row in rows:
            citat_list.append({
                'citat': row[0].replace('&app', "'") if row[0] else '',
                'name': row[1],
                'institution': row[2],
                'time': format_date(row[3]),
                'note': row[4].replace('&app', "'") if row[4] else '',
            })
    else:
        sql = """
            SELECT Citat.citat, Person.Namn, Institution.Namn, Citat.tid, Citat.inlagt, Citat.notering
            FROM Citat, Person, Institution
            WHERE Citat.person = Person.ID
              AND Person.Institution = Institution.ID
        """
        params = []
        if str(institution) != '-1':
            sql += " AND Person.Institution = ?"
            params.append(institution)
        if str(person) != '-1':
            sql += " AND Person.ID = ?"
            params.append(person)
        sql += " AND Person.Typ = ?"
        params.append(typ)
        sql += " ORDER BY Citat.tid DESC"

        rows = conn.execute(sql, params).fetchall()
        today = date.today()
        for row in rows:
            inlagt_date = parse_date(row[4])
            if inlagt == '-1' or inlagt_date is None:
                include = True
            else:
                cutoff = today - timedelta(days=int(inlagt))
                include = inlagt_date >= cutoff

            if include:
                institution_name = row[2] if typ == '1' else ''
                citat_list.append({
                    'citat': row[0].replace('&app', "'") if row[0] else '',
                    'name': row[1],
                    'institution': institution_name,
                    'time': format_date(row[3]),
                    'note': row[5].replace('&app', "'") if row[5] else '',
                })

    conn.close()
    return render_template('show_citat.html', citat_list=citat_list)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_user = False
    error_pass = False
    return_url = request.args.get('ReturnUrl', url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        return_url = request.form.get('return_url', url_for('index'))

        conn = get_db()
        row = conn.execute("SELECT ID, Losenord FROM Users WHERE Anvandare = ?", (username,)).fetchone()
        conn.close()

        if row is None:
            error_user = True
        elif row['Losenord'] != password:
            error_pass = True
        else:
            session['user_id'] = row['ID']
            session['username'] = username
            return redirect(return_url)

    return render_template('login.html', error_user=error_user, error_pass=error_pass,
                           return_url=return_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    errors = {}
    return_url = request.args.get('ReturnUrl', '')

    if request.method == 'POST':
        namn = request.form.get('namn', '')
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_again = request.form.get('password_again', '')
        email = request.form.get('email', '')
        koppling = request.form.get('koppling', '')
        return_url = request.form.get('return_url', '')

        if len(namn) < 2:
            errors['namn'] = True
        if len(username) < 3:
            errors['username'] = True
        if len(password) < 3:
            errors['password'] = True
        if password != password_again:
            errors['password_again'] = True
        if '@' not in email or '.' not in email:
            errors['email'] = True
        if len(koppling) < 3:
            errors['koppling'] = True

        if not errors:
            conn = get_db()
            existing = conn.execute("SELECT ID FROM Users WHERE Anvandare = ?", (username,)).fetchone()
            if existing:
                errors['username_taken'] = True
            else:
                conn.execute(
                    "INSERT INTO Users (Namn, Anvandare, Losenord, Email, Koppling) VALUES (?,?,?,?,?)",
                    (namn, username, password, email, koppling)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('login') + ('?ReturnUrl=' + return_url if return_url else ''))
            conn.close()

    return render_template('add_user.html', errors=errors, return_url=return_url)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', ReturnUrl=request.path))
        return f(*args, **kwargs)
    return decorated


@app.route('/secure/add_citat', methods=['GET', 'POST'])
@login_required
def add_citat():
    conn = get_db()
    persons = conn.execute("SELECT ID, Namn FROM Person ORDER BY Namn").fetchall()
    conn.close()

    months = [
        ('1','Januari'),('2','Februari'),('3','Mars'),('4','April'),
        ('5','Maj'),('6','Juni'),('7','Juli'),('8','Augusti'),
        ('9','September'),('10','Oktober'),('11','November'),('12','December')
    ]
    days = [(str(i), f'{i:02d}') for i in range(1, 32)]
    today = datetime.now()
    year_error = False

    if request.method == 'POST':
        citat_text = request.form.get('citat', '')
        person_id = request.form.get('person', '')
        unknown = request.form.get('unknown') == 'on'
        year = request.form.get('year', '')
        month = request.form.get('month', '1')
        day = request.form.get('day', '1')
        note = request.form.get('note', '')

        if citat_text:
            if not unknown:
                if len(year) != 4 or not year.isdigit():
                    year_error = True
                else:
                    tid = f"{year}-{int(month):02d}-{int(day):02d}"
                    conn = get_db()
                    conn.execute(
                        "INSERT INTO Citat (citat, person, tid, inlagt, notering, anvandare) VALUES (?,?,?,?,?,?)",
                        (citat_text.replace("'", "&app"), person_id, tid,
                         today.strftime('%Y-%m-%d'), note.replace("'", "&app"), session['user_id'])
                    )
                    conn.commit()
                    conn.close()
                    return redirect(url_for('index'))
            else:
                conn = get_db()
                conn.execute(
                    "INSERT INTO Citat (citat, person, inlagt, notering, anvandare) VALUES (?,?,?,?,?)",
                    (citat_text.replace("'", "&app"), person_id,
                     today.strftime('%Y-%m-%d'), note.replace("'", "&app"), session['user_id'])
                )
                conn.commit()
                conn.close()
                return redirect(url_for('index'))

    return render_template('secure/add_citat.html', persons=persons, months=months, days=days,
                           today=today, year_error=year_error)


@app.route('/secure/add_person', methods=['GET', 'POST'])
@login_required
def add_person():
    conn = get_db()
    institutions = conn.execute("SELECT ID, Namn FROM Institution ORDER BY Namn").fetchall()
    conn.close()

    person_types = [('1', 'Lärare/Personal'), ('2', 'Teknolog')]

    if request.method == 'POST':
        namn = request.form.get('namn', '')
        typ = request.form.get('typ', '1')
        institution_id = request.form.get('institution', '')

        if namn:
            conn = get_db()
            conn.execute(
                "INSERT INTO Person (Namn, Typ, Institution, Anvandare) VALUES (?,?,?,?)",
                (namn, typ, institution_id, session['user_id'])
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('secure/add_person.html', institutions=institutions,
                           person_types=person_types)


def format_date(d):
    if not d:
        return ''
    if isinstance(d, str):
        try:
            dt = datetime.strptime(d, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except:
            return d
    return str(d)


def parse_date(d):
    if not d:
        return None
    try:
        return datetime.strptime(d, '%Y-%m-%d').date()
    except:
        return None


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
