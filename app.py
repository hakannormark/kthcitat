from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'kthcitat_secret_2004')

DB_PATH = os.path.join(os.path.dirname(__file__), 'kthcitat.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS Institution (ID INTEGER PRIMARY KEY, Namn TEXT, Anvandare INTEGER);
    CREATE TABLE IF NOT EXISTS Person (ID INTEGER PRIMARY KEY, Namn TEXT, Typ INTEGER, Institution INTEGER, Anvandare INTEGER);
    CREATE TABLE IF NOT EXISTS Citat (ID INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER, tid TEXT, inlagt TEXT, citat TEXT, notering TEXT, anvandare INTEGER);
    CREATE TABLE IF NOT EXISTS Users (ID INTEGER PRIMARY KEY AUTOINCREMENT, Namn TEXT, Anvandare TEXT, Losenord TEXT, Email TEXT, Koppling TEXT);
    """)
    # Only insert data if tables are empty
    if c.execute("SELECT COUNT(*) FROM Institution").fetchone()[0] == 0:
        c.executemany("INSERT INTO Institution VALUES (?,?,?)", [
            (11,"Fysik",14),(12,"Mikroelektronik och informationsteknik",14),(13,"Mekanik",14),
            (14,"Språk och kommunikation",14),(15,"NADA",14),(16,"Elektronik",14),(1,"INDEK",14),(2,"Matematik",14),
        ])
        c.executemany("INSERT INTO Person VALUES (?,?,?,?,?)", [
            (38,"Lasse Svensson",1,2,13),(40,"Dan Johansson",1,1,14),(41,"Göran Manneberg",1,11,14),
            (42,"Karl-Filip Faxén",1,12,14),(43,"Sven Modell",1,1,14),(44,"Mattias Löfgren",1,1,14),
            (45,"Johan Moberg",1,2,14),(46,"Tomas Höglund",1,2,14),(47,"Gunnar Maxe",1,13,14),
            (48,"Tom Åseskog",1,14,14),(49,"Björn Eiderbäck",1,15,14),(50,"Hans Weinberger",1,1,14),
            (51,"Staffan Laestadius",1,1,14),(52,"Håkan Isoz",1,16,14),(53,"Jan Forslin",1,1,14),
            (54,"Jonathan Schroeder",1,1,14),(55,"Per Hiller",1,1,14),(56,"Bengt Domeij",1,1,14),
            (58,"Peter Englund",2,16,14),(59,"Johan Rockberg",2,16,14),(60,"Pär Thorstensson",2,16,14),
            (61,"Thomas Sandberg",1,1,14),(62,"Anders Back",2,16,14),(20,"Alf Rehn",1,1,14),(21,"Axel Hultman",1,2,14),
        ])
        c.executemany("INSERT INTO Citat (ID,person,tid,inlagt,citat,notering,anvandare) VALUES (?,?,?,?,?,?,?)", [
            (88,38,"1993-09-10","2002-10-22","Har ni några argument för det där, annat än rena svordomar?",None,13),
            (91,38,"1993-09-30","2002-10-22","När vi inte inser vad vi ska göra...så deriverar vi.",None,13),
            (92,38,"1993-09-30","2002-10-22","Man behöver nästan inte tänka. Det är ju hela avsikten med matematiken!","Lasse berömmer styrkan i medelvärdessatsen.",13),
            (93,38,"1993-09-30","2002-10-22","Jag ligger ju som sagt i den här kursen på något vis...helt olokaliserad.","Svensson funderar på sin förmåga att inrymma hela kursens budskap i varje föreläsning.",13),
            (99,20,"2002-10-09","2002-10-24","Som lärare har jag rätt att bestämma när en kurs är bra eller dålig, och den här kursen är fan dålig!","En självkritisk lärare ber om ursäkt för sin insats inför klassen.",14),
            (100,40,"2001-09-13","2002-10-30","Kejsaren säger: -Jag vill ha dina prylar!","Johansson pinpointar problemet med den fornkinesiska ekonomiska strukturen.",14),
            (101,41,"2000-09-15","2002-10-30","Plattkondensatorer finns bara i skolan, inte i verkligheten.","Manneberg förtydligar det meningsfulla i talet.",14),
            (102,41,"2000-09-15","2002-10-30","Sfäriska kondensatorer finns bara för att dom är svåra att räkna på.","Manneberg rättfärdigar försummandet av sfäriska kondensatorer i undervisningen.",14),
            (103,41,"2000-09-19","2002-10-30","Bland lärarna är det väl känt att I-teknologer är en receptiv och bra grupp som dessutom hatar mekanik.",None,14),
            (104,41,"2000-10-17","2002-10-30","Det här ser ut som en Besselfunktion, men skit i dom...","Manneberg relaterar till en nog så viktig del av fysiken.",14),
            (105,41,"2000-10-17","2002-10-30","Om jag är en ljusstråle, (detta är min favoritliknelse), ...","Manneberg myser...",14),
            (106,42,"2002-03-12","2002-10-30","Jag slipar mina knivar för att begå lustmord på Windows 2000s schemaläggare.",None,14),
            (107,42,"2002-03-12","2002-10-30","Gud är den icke implementerade virtuella maskinen.",None,14),
            (108,43,"1999-09-10","2002-10-30","Det är ingen jävel som orkar läsa rapporter 30 sidor ute i näringslivet.",None,14),
            (109,43,"1999-09-10","2002-10-30","schh - Tyst!","Modell irriteras över främre bänks okoncentration.",14),
            (110,44,"1999-11-10","2002-10-30","Dom har helt enkelt diktat upp en balansräkning och en resultaträkning och gjort helt jävla fel!","Övningsassen Löfgren är lätt kritisk till INDEKs övningsuppgifter.",14),
            (111,44,"1999-11-10","2002-10-30","Talet är helt värdelöst.",None,14),
            (112,44,"1999-12-08","2002-10-30","Det är inte svårt, det blir bara krångligare.","Akademiskt baklås?",14),
            (113,45,"1999-11-10","2002-10-31","Det här talet är svårare än vad det är bra.","Assen menar underförstått att alla tal måste räknas.",14),
            (114,46,"1999-09-21","2002-10-31","Med det här vill jag bara antyda att det inte är något konstigt med det här.","Ett desperat försök att hålla matematikens obegriplighet om ryggen.",14),
            (115,47,"1999-11-04","2002-10-31","Om man har en hockeypuck och drar eller skjuter den går det bra, har man en gräddsemla blir det värre.","Maxe trånar efter institutionens obligatoriska niofika.",14),
            (116,47,"1999-11-23","2002-10-31","-Ja... Nejnej, fan heller!","Maxe på teknologens fråga om H2 är lika med H4.",14),
            (117,47,"1999-11-25","2002-10-31","Kul tal, roligare än vanligt!","En ljuspunkt efter 30 års mekaniktristess.",14),
            (118,47,"2000-01-19","2002-10-31","Äh, det här var ju svårt!","Vad trodde han om mekanik egentligen?",14),
            (119,47,"2000-01-26","2002-10-31","Och här spelar också bankurvan ingen roll.",None,14),
            (120,48,None,"2002-10-31","Man ska inte gödsla med semikolon.","Så sant som det är sagt!",14),
            (121,49,None,"2002-10-31","Trenden är ju lite grann i industrin att man hoppar av RUP i sista stund för att få klart nått.","Björne motiverar teknologerna att läsa en hel kurs med RUP.",14),
            (122,49,None,"2002-10-31","I praktiken är man aldrig mer än femton personer i ett projekt, och är man det är det för att nån manager har bestämt sig för att vara jätteviktig och ha 100 personer i sitt projekt. Då går det till så att några håller undan dom andra så att femton kan få nått gjort.",None,14),
            (123,50,"2002-02-11","2002-11-01","Det handlar inte om nån jävla ordutfyllelse i största allmänhet!","Märkligt! Det går ju stick i stäv med övriga INDEK.",14),
            (124,40,None,"2002-11-01","Och nu kommer poängen med dagens föreläsning...","Det fanns teknolger som gick när fem minuter återstod av fyratimmarsföreläsningen, det skulle de aldrig ha gjort.",14),
            (125,43,None,"2002-11-01","Här kommer lite late afternoon benefit...","Äntligen kunde man skörda frukten av att sitta tiden ut!",14),
            (126,51,"2001-09-04","2002-11-01","Kompendiet balanserar på legalitetens utmarker.",None,14),
            (127,48,None,"2002-11-02","Jag skulle vilja slå ett slag för ordet dryfta. Det är ett utmärkt ord som används alltför sällan.",None,14),
            (67,20,"2002-09-04","2002-10-07",'INDEK är ett bisarrt ställe med en massa människor som pratar om saker som "att vara i tekniken".',None,14),
            (128,52,"2001-03-19","2002-11-02","Men det där oktalt, det är bara larv. Det är ingen som håller på med det.","Återigen skönt att veta att man inte slänger bort sin tid i skolan.",14),
            (129,53,"2002-09-05","2002-11-02","Kasta spjut på gaseller är läckert.",None,14),
            (130,53,"2002-09-17","2002-11-02","Att vara bonde gav inte lika mycket proteiner som elefanten, och så blev man religiös på kuppen!","Forslin påpekar det absurda i att övergå från jägar- till bondesamhälle.",14),
            (131,53,"2002-10-08","2002-11-02","Han används väldigt mycket i konsultsammanhang, men det faller ingen skugga på honom för det.","Nej, Douglas McGregor kan ju inte rå för det!",14),
            (132,54,"2002-10-01","2002-11-02","We&appre all gonna die, sorry...",None,14),
            (133,54,"2002-10-01","2002-11-02","I shop, therefore I am.",None,14),
            (134,55,"2002-10-23","2002-11-02","Boken är ganska tjock, det innebär att vissa delar måste läsas med förnuft och andra mer intensivt.",None,14),
            (135,55,"2002-10-23","2002-11-02","Konkurs innebär inte konkurs, utan finansiella problem. Det vill säga banken blir lite mer irriterad när den pratar med företaget.",None,14),
            (136,55,"2002-10-31","2002-11-02","Jag kan diversifiera bort Kurt Hellström men inte Bosse Ringholm, risken med Bosse Ringholm får jag alltid bära.",None,14),
            (137,56,"2002-10-31","2002-11-02","Det är inte ett så jätteattraktivt jobb, det är knappt nått betalt alls och man får sitta där hela dagarna.","Om det tveksamma nöjet att vara nämndeman.",14),
            (138,20,"2002-10-30","2002-11-02","Om man inte vet vad man ska säga säger man komplext eller integrerat.",None,14),
            (139,55,"2002-11-04","2002-11-11","Är du lönsam lille vän?","En stilla undran riktad till Jonas Birgersson.",14),
            (140,20,"2002-11-13","2002-11-13","Man ska alltid dra en sportmetafor om man kan!",None,14),
            (141,58,"2003-10-16","2003-11-03","Nä asså det är alltid en massa lik i första startled som man måste springa om.","Englund ursäktar sin 156:e plats i Lidingöloppet och det faktum att Malin Ewerlöf passerade honom under sista kilometern.",14),
            (142,59,"2003-10-16","2003-11-03","Det finns alltid en hake med gratisresor, antingen hamnar man i skogsindustrin eller också måste man göra kärnvapen.","Johan höjer ett varningens finger för glättiga exjobbserbjudanden.",14),
            (143,60,None,"2003-11-03","Men då bestämmer vi det, kärnkraftverk är bättre än gym som energikälla!",None,14),
            (144,61,"2003-06-04","2003-11-03","Vi är ganska imperialistiska av oss på Industriell Ekonomi, vi anser oss ha något att säga om det mesta.",None,14),
            (145,61,"2003-06-04","2003-11-03","Jag fick ta honom åt sidan och läxa upp honom. Efteråt var han oerhört förkrossad, och mycket tacksam.","Sandberg glänser med pedagogiska skalper.",14),
            (146,43,"2003-06-04","2003-11-03","Jag tror han jobbar på ackord den jäveln!","Modell visar lätt irritation mot hantverkaren i byggnaden.",14),
            (147,62,"2003-11-20","2003-11-21","När företag inför kostnadsbesparingar är det skitsnackarna som rycker.","Jordnära konstaterande om varför det är kärvt på arbetsmarknaden för I:are i lågkonjunktur.",14),
            (148,62,"2004-06-07","2004-06-24","Dom bara utnyttjar oss!","Back beklagar sig över det faktum att han som hockeyproffs tvingas spela golf på dagtid för att fördriva tiden mellan träningarna.",14),
            (68,20,"2002-09-11","2002-10-07","I vår serie elitistiska uttalanden har vi idag kommit fram till: Låt en arbetslös kulturarbetare skriva instruktionsboken.",None,14),
            (69,20,"2002-09-11","2002-10-07","Va fan betyder ingenjörsmässigt för nått?",None,14),
            (70,20,"2002-09-18","2002-10-07","Kursen handlar ju rekursivt om va fan den här kursen handlar om!",None,14),
            (71,20,"2002-09-18","2002-10-07","Vad handlar bokhelvetet om?",None,14),
            (72,20,"2002-09-18","2002-10-07","Om 400 års historia innehåller 3 kvinnor och 4800 män så finns det nån form av viktning.",None,14),
            (73,20,"2002-09-18","2002-10-07","KTH som skitsnacksgenerator!",None,14),
            (74,20,"2002-09-25","2002-10-07","TELen har varit en sån här klassisk INDEK-sillsalladskurs: - Alla mina vänner gästföreläser!",None,14),
            (75,21,"2000-04-11","2002-10-07","Ni läser i Beta som Fan läser Bibeln!",None,14),
            (76,21,"2000-04-13","2002-10-07",'Tao som i "spår", tao är väl nån förgrekning av trace.',None,14),
        ])
        c.executemany("INSERT INTO Users VALUES (?,?,?,?,?,?)", [
            (13,"Magnus","mnk",None,"magnus.normark@usa.net","F93"),
            (14,"Håkan Normark","hoc","hoc21","hakan.normark@home.se","I99"),
        ])
    conn.commit()
    conn.close()

init_db()


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
