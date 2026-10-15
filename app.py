from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3, os, csv, io, math
from collections import defaultdict
from datetime import datetime
from database import get_student_profile, save_student_profile

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'local-development-only-change-me')
DB = os.environ.get('TIGER_DB_PATH', os.path.join(os.path.dirname(__file__), 'tiger_pathway.db'))
TERMS=['Spring','Summer','Fall']; STATUSES=['Completed','In Progress','Planned','Remaining']; CATEGORIES=['General Education','Mathematics','Science','Computer Engineering Core','Electrical Engineering Core','Computer Science','Technical Elective','Senior Design','Free Elective']


def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c

def init_db():
    c=db(); c.executescript('''
    CREATE TABLE IF NOT EXISTS student(id INTEGER PRIMARY KEY CHECK(id=1),student_id TEXT,name TEXT,email TEXT,major TEXT,concentration TEXT,catalog_year TEXT,standing TEXT,gpa REAL DEFAULT 0,credits_completed INTEGER DEFAULT 0,total_credits INTEGER DEFAULT 128,target_graduation TEXT,pace INTEGER DEFAULT 15);
    CREATE TABLE IF NOT EXISTS course(id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT UNIQUE NOT NULL,name TEXT NOT NULL,credits INTEGER NOT NULL,department TEXT,category TEXT NOT NULL,description TEXT,status TEXT DEFAULT 'Remaining',grade TEXT,planned_term TEXT,offered_spring INTEGER DEFAULT 1,offered_summer INTEGER DEFAULT 0,offered_fall INTEGER DEFAULT 1,min_grade TEXT);
    CREATE TABLE IF NOT EXISTS requirement(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,credits_required INTEGER NOT NULL,notes TEXT);
    CREATE TABLE IF NOT EXISTS course_requirement(course_id INTEGER REFERENCES course(id) ON DELETE CASCADE,requirement_id INTEGER REFERENCES requirement(id) ON DELETE CASCADE,PRIMARY KEY(course_id,requirement_id));
    CREATE TABLE IF NOT EXISTS prerequisite(course_id INTEGER REFERENCES course(id) ON DELETE CASCADE,prereq_id INTEGER REFERENCES course(id) ON DELETE CASCADE,PRIMARY KEY(course_id,prereq_id));
    CREATE TABLE IF NOT EXISTS whatif(id INTEGER PRIMARY KEY AUTOINCREMENT,course_id INTEGER REFERENCES course(id) ON DELETE CASCADE,action TEXT NOT NULL);
    ''');
    if not c.execute('SELECT 1 FROM student WHERE id=1').fetchone():
        c.execute('INSERT INTO student(id,student_id,name,email,major,concentration,catalog_year,standing,gpa,total_credits,target_graduation) VALUES(1,?,?,?,?,?,?,?,?,?,?)',('DEMO0001','Sample Student','student@example.com','Computer Engineering','Embedded Systems','2026-2027','Senior',3.42,128,'Spring 2027'))
        seed=[
        ('ENGL 1010','English Composition I',3,'ENGL','General Education','Written communication','Completed','A',None,1,0,1),('ENGL 1020','English Composition II',3,'ENGL','General Education','Written communication','Completed','A-',None,1,0,1),('MATH 1910','Calculus I',4,'MATH','Mathematics','Calculus I','Completed','B+',None,1,0,1),('MATH 1920','Calculus II',4,'MATH','Mathematics','Calculus II','Completed','B',None,1,0,1),('MATH 2110','Calculus III',4,'MATH','Mathematics','Calculus III','In Progress',None,'Fall 2026',1,0,1),('MATH 3242','Differential Equations',3,'MATH','Mathematics','Differential equations','Remaining',None,None,1,0,1),('PHYS 2110','Physics for Engineers I',4,'PHYS','Science','Engineering physics','Completed','B+',None,1,0,1),('PHYS 2120','Physics for Engineers II',4,'PHYS','Science','Engineering physics','Completed','B',None,1,0,1),('EECE 3213','Computer Organization',3,'EECE','Computer Engineering Core','Architecture and organization','In Progress',None,'Fall 2026',1,0,1),('EECE 3270','Introduction to Microprocessors',3,'EECE','Computer Engineering Core','Microprocessors','Completed','A-',None,1,0,1),('EECE 4213','Advanced Computer Engineering',3,'EECE','Computer Engineering Core','Advanced engineering','Remaining',None,None,1,0,1),('EECE 4310','Senior Design I',2,'EECE','Senior Design','Capstone design I','Remaining',None,None,1,0,1),('EECE 4320','Senior Design II',2,'EECE','Senior Design','Capstone design II','Remaining',1,None,1,0,1),('COMP 2150','Data Structures',3,'COMP','Computer Science','Data structures','Completed','B+',None,1,0,1),('TECH 4381','Principles of Supervision',3,'TECH','General Education','Professional development','Remaining',None,None,1,0,1)]
        c.executemany('INSERT INTO course(code,name,credits,department,category,description,status,grade,planned_term,offered_spring,offered_summer,offered_fall) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',seed)
        for name,cat,cr in [('Mathematics Core','Mathematics',18),('Science Core','Science',12),('Computer Engineering Core','Computer Engineering Core',30),('Senior Design','Senior Design',4),('General Education','General Education',30),('Technical Electives','Technical Elective',12)]: c.execute('INSERT INTO requirement(name,category,credits_required,notes) VALUES(?,?,?,?)',(name,cat,cr,''))
        links=[('EECE 4213','EECE 3213'),('EECE 4310','EECE 4213'),('EECE 4320','EECE 4310'),('MATH 3242','MATH 2110')]
        for a,b in links:
            x=c.execute('SELECT id FROM course WHERE code=?',(a,)).fetchone(); y=c.execute('SELECT id FROM course WHERE code=?',(b,)).fetchone(); c.execute('INSERT OR IGNORE INTO prerequisite VALUES(?,?)',(x['id'],y['id']))
    c.commit(); c.close()


def semesters(n=8):
    out=[]; y=datetime.now().year; term='Fall' if datetime.now().month>=7 else 'Spring'
    for _ in range(n): out.append(f'{term} {y}'); term,y=({'Spring':('Summer',y),'Summer':('Fall',y),'Fall':('Spring',y+1)})[term]
    return out

def prereqs(c,course_id):
    return c.execute('SELECT p.* FROM course p JOIN prerequisite r ON p.id=r.prereq_id WHERE r.course_id=?',(course_id,)).fetchall()

def completed_codes(c): return {r['code'] for r in c.execute("SELECT code FROM course WHERE status='Completed'")}

def audit(c):
    rows=[]
    for r in c.execute('SELECT * FROM requirement ORDER BY category,name'):
        courses=c.execute('SELECT c.* FROM course c JOIN course_requirement cr ON c.id=cr.course_id WHERE cr.requirement_id=?',(r['id'],)).fetchall()
        earned=sum(x['credits'] for x in courses if x['status']=='Completed')
        rows.append((r,earned,min(100,round(earned/r['credits_required']*100)) if r['credits_required'] else 0))
    # fallback category audit if no mappings
    if all(not x[1] for x in rows):
        for r in rows:
            courses=c.execute('SELECT * FROM course WHERE category=?',(r[0]['category'],)).fetchall(); earned=sum(x['credits'] for x in courses if x['status']=='Completed'); r=(r[0],earned,min(100,round(earned/r[0]['credits_required']*100))); rows[rows.index(next(z for z in rows if z[0]['id']==r[0]['id']))]=r
    return rows

@app.context_processor
def nav():
    c=db(); s=c.execute('SELECT * FROM student WHERE id=1').fetchone(); c.close(); return {'nav_student':s}

@app.route('/')
def dashboard():
    c=db(); s=c.execute('SELECT * FROM student WHERE id=1').fetchone(); courses=c.execute('SELECT * FROM course').fetchall(); rem=sum(x['credits'] for x in courses if x['status']!='Completed'); planned=sum(x['credits'] for x in courses if x['planned_term']); completed=s['credits_completed']; pct=min(100,round(completed/max(s['total_credits'],1)*100)); risks=[]
    for x in courses:
        if x['status'] in ('Planned','In Progress'):
            miss=[p['code'] for p in prereqs(c,x['id']) if p['status']!='Completed']
            if miss: risks.append(f"{x['code']} is missing: {', '.join(miss)}")
    c.close(); return render_template('dashboard.html',s=s,courses=courses,rem=rem,planned=planned,pct=pct,risks=risks,audit=audit(db())[:5])

@app.route('/student',methods=['GET','POST'])
def student():
    if request.method=='POST':
        f=request.form
        try:
            save_student_profile(DB, {
                'student_id': f.get('student_id', ''),
                'name': f.get('name', ''),
                'email': f.get('email', ''),
                'major': f.get('major', ''),
                'concentration': f.get('concentration', ''),
                'catalog_year': f.get('catalog_year', ''),
                'standing': f.get('standing', ''),
                'gpa': f.get('gpa') or 0,
                'credits_completed': f.get('credits_completed') or 0,
                'total_credits': f.get('total_credits') or 128,
                'target_graduation': f.get('target_graduation', ''),
                'pace': f.get('pace') or 15,
            })
        except (TypeError, ValueError):
            flash('Please enter valid numeric values for GPA and credit fields.', 'error')
            return redirect(url_for('student'))
        flash('Student profile saved.','success')
        return redirect(url_for('student'))
    s=get_student_profile(DB)
    return render_template('student.html',s=s)

@app.route('/catalog',methods=['GET','POST'])
def catalog():
    c=db()
    if request.method=='POST':
        f=request.form; vals=(f['code'].upper(),f['name'],int(f['credits']),f.get('department',''),f['category'],f.get('description',''),f.get('status','Remaining'),f.get('grade') or None,f.get('planned_term') or None,int('spring' in f),int('summer' in f),int('fall' in f),f.get('min_grade',''))
        try: c.execute('INSERT INTO course(code,name,credits,department,category,description,status,grade,planned_term,offered_spring,offered_summer,offered_fall,min_grade) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',vals); c.commit(); flash('Course added to catalog.','success')
        except sqlite3.IntegrityError: flash('Course code already exists. Use Edit/Update or choose another code.','error')
        return redirect(url_for('catalog'))
    q=request.args.get('q',''); cat=request.args.get('category','All'); rows=c.execute('SELECT * FROM course WHERE (code LIKE ? OR name LIKE ?) AND (?="All" OR category=?) ORDER BY department,code',(f'%{q}%',f'%{q}%',cat,cat)).fetchall(); c.close(); return render_template('catalog.html',courses=rows,categories=CATEGORIES,q=q,cat=cat,statuses=STATUSES)

@app.post('/course/<int:id>/update')
def course_update(id):
    c=db(); f=request.form; c.execute('UPDATE course SET name=?,credits=?,department=?,category=?,description=?,status=?,grade=?,planned_term=?,offered_spring=?,offered_summer=?,offered_fall=?,min_grade=? WHERE id=?',(f['name'],int(f['credits']),f.get('department',''),f['category'],f.get('description',''),f['status'],f.get('grade') or None,f.get('planned_term') or None,int(f.get('spring')=='on'),int(f.get('summer')=='on'),int(f.get('fall')=='on'),f.get('min_grade',''),id)); c.commit(); c.close(); flash('Course updated.','success'); return redirect(url_for('catalog'))
@app.post('/course/<int:id>/delete')
def course_delete(id):
    c=db(); c.execute('DELETE FROM course WHERE id=?',(id,)); c.commit(); c.close(); flash('Course deleted.','success'); return redirect(url_for('catalog'))

@app.route('/requirements',methods=['GET','POST'])
def requirements():
    c=db()
    if request.method=='POST':
        f=request.form; c.execute('INSERT INTO requirement(name,category,credits_required,notes) VALUES(?,?,?,?)',(f['name'],f['category'],int(f['credits_required']),f.get('notes',''))); c.commit(); flash('Degree requirement added.','success'); return redirect(url_for('requirements'))
    rows=c.execute('SELECT * FROM requirement ORDER BY category,name').fetchall(); c.close(); return render_template('requirements.html',requirements=rows,categories=CATEGORIES)
@app.post('/requirement/<int:id>/delete')
def req_delete(id):
    c=db(); c.execute('DELETE FROM requirement WHERE id=?',(id,)); c.commit(); c.close(); return redirect(url_for('requirements'))

@app.route('/prerequisites',methods=['GET','POST'])
def prerequisites():
    c=db()
    if request.method=='POST':
        c.execute('INSERT OR IGNORE INTO prerequisite(course_id,prereq_id) VALUES(?,?)',(int(request.form['course_id']),int(request.form['prereq_id']))); c.commit(); flash('Prerequisite relationship saved.','success'); return redirect(url_for('prerequisites'))
    links=c.execute('SELECT r.course_id,r.prereq_id,a.code AS course_code,a.name AS course_name,b.code AS prereq_code,b.name AS prereq_name FROM prerequisite r JOIN course a ON a.id=r.course_id JOIN course b ON b.id=r.prereq_id ORDER BY a.code').fetchall(); courses=c.execute('SELECT * FROM course ORDER BY code').fetchall(); c.close(); return render_template('prerequisites.html',links=links,courses=courses)
@app.post('/prerequisite/delete')
def prereq_delete():
    c=db(); c.execute('DELETE FROM prerequisite WHERE course_id=? AND prereq_id=?',(request.form['course_id'],request.form['prereq_id'])); c.commit(); c.close(); return redirect(url_for('prerequisites'))

@app.route('/transcript',methods=['GET','POST'])
def transcript():
    c=db()
    if request.method=='POST':
        ids=request.form.getlist('course_id'); statuses=request.form.getlist('status'); grades=request.form.getlist('grade');
        for i,cid in enumerate(ids): c.execute('UPDATE course SET status=?,grade=? WHERE id=?',(statuses[i],grades[i] or None,cid))
        s=c.execute('SELECT credits FROM course WHERE status="Completed"').fetchall(); total=sum(x['credits'] for x in s); c.execute('UPDATE student SET credits_completed=? WHERE id=1',(total,)); c.commit(); flash('Transcript updated.','success'); return redirect(url_for('transcript'))
    courses=c.execute('SELECT * FROM course ORDER BY category,code').fetchall(); c.close(); return render_template('transcript.html',courses=courses,statuses=STATUSES)

@app.route('/planner',methods=['GET','POST'])
def planner():
    c=db(); terms=semesters(8)
    if request.method=='POST':
        for cid in request.form.getlist('course_id'):
            term=request.form.get(f'term_{cid}','');
            if term: c.execute('UPDATE course SET planned_term=?,status=CASE WHEN status="Remaining" THEN "Planned" ELSE status END WHERE id=?',(term,cid))
        c.commit(); flash('Academic plan saved.','success'); return redirect(url_for('planner'))
    courses=c.execute('SELECT * FROM course WHERE status!="Completed" ORDER BY category,code').fetchall(); grouped=defaultdict(list)
    for x in courses:
        if x['planned_term']: grouped[x['planned_term']].append(x)
    c.close(); return render_template('planner.html',courses=courses,grouped=grouped,terms=terms)

@app.post('/auto-plan')
def auto_plan():
    c=db(); terms=semesters(8); completed=completed_codes(c); available=[x for x in c.execute('SELECT * FROM course WHERE status="Remaining" ORDER BY category,code').fetchall()]; planned_by=defaultdict(int)
    for term in terms: planned_by[term]=0
    for x in available:
        ps=prereqs(c,x['id']);
        if any(p['code'] not in completed for p in ps): continue
        for term in terms:
            ok=(term.startswith('Spring') and x['offered_spring']) or (term.startswith('Summer') and x['offered_summer']) or (term.startswith('Fall') and x['offered_fall'])
            if ok and planned_by[term]+x['credits']<=15:
                c.execute('UPDATE course SET planned_term=?,status="Planned" WHERE id=?',(term,x['id'])); planned_by[term]+=x['credits']; completed.add(x['code']); break
    c.commit(); c.close(); flash('A proposed plan was generated using prerequisites, availability, and a 15-credit target. Review it with an advisor.','success'); return redirect(url_for('planner'))

@app.route('/audit')
def degree_audit():
    c=db(); rows=audit(c); s=c.execute('SELECT * FROM student WHERE id=1').fetchone(); c.close(); return render_template('audit.html',rows=rows,s=s)

@app.route('/priority')
def priority():
    c=db(); done=completed_codes(c); out=[]
    for x in c.execute('SELECT * FROM course WHERE status!="Completed" ORDER BY code').fetchall():
        score=0; reasons=[]; ps=prereqs(c,x['id']);
        if not ps or all(p['code'] in done for p in ps): score+=25; reasons.append('Prerequisites satisfied or none')
        else: reasons.append('Waiting on prerequisite')
        if 'Core' in x['category'] or x['category']=='Senior Design': score+=30; reasons.append('Core/capstone requirement')
        if x['status']=='In Progress': score+=20; reasons.append('Currently in progress')
        if x['planned_term']: score+=15; reasons.append('Already in academic plan')
        if x['offered_spring'] or x['offered_fall']: score+=10; reasons.append('Regularly offered')
        out.append((x,min(score,100),reasons))
    out.sort(key=lambda z:z[1],reverse=True); c.close(); return render_template('priority.html',items=out)

@app.route('/risks')
def risks():
    c=db(); risks=[]
    for x in c.execute('SELECT * FROM course WHERE status IN ("Planned","In Progress")').fetchall():
        miss=[p['code'] for p in prereqs(c,x['id']) if p['status']!='Completed']
        if miss: risks.append(('High','Prerequisite risk',f"{x['code']} requires {', '.join(miss)}."))
    for term in semesters(8):
        total=sum(x['credits'] for x in c.execute('SELECT * FROM course WHERE planned_term=?',(term,)).fetchall())
        if total>18: risks.append(('Medium','Credit overload',f'{term} has {total} planned credits.'))
    if not risks: risks.append(('Low','No major risks detected','Review your plan regularly and confirm requirements with advising.'))
    c.close(); return render_template('risks.html',risks=risks)

@app.route('/what-if',methods=['GET','POST'])
def what_if():
    c=db(); message=None; impacted=[]
    if request.method=='POST':
        cid=int(request.form['course_id']); action=request.form['action']; course=c.execute('SELECT * FROM course WHERE id=?',(cid,)).fetchone(); impacted=c.execute('SELECT c.* FROM course c JOIN prerequisite p ON c.id=p.course_id WHERE p.prereq_id=?',(cid,)).fetchall(); message=f"What-if: {action} {course['code']}. {len(impacted)} downstream course(s) depend directly on it."; 
    courses=c.execute('SELECT * FROM course ORDER BY code').fetchall(); c.close(); return render_template('whatif.html',courses=courses,message=message,impacted=impacted)

@app.route('/data-center')
def data_center():
    c=db(); counts={'courses':c.execute('SELECT COUNT(*) FROM course').fetchone()[0],'requirements':c.execute('SELECT COUNT(*) FROM requirement').fetchone()[0],'prereqs':c.execute('SELECT COUNT(*) FROM prerequisite').fetchone()[0]}; c.close(); return render_template('data_center.html',counts=counts)

@app.post('/import-courses')
def import_courses():
    file=request.files.get('file');
    if not file: flash('Choose a CSV file first.','error'); return redirect(url_for('data_center'))
    c=db(); rows=csv.DictReader(io.TextIOWrapper(file.stream,encoding='utf-8-sig')); n=0
    for r in rows:
        if not r.get('code') or not r.get('name'): continue
        data=(r['code'].upper(),r['name'],int(r.get('credits') or 3),r.get('department',''),r.get('category','General Education'),r.get('description',''),r.get('status','Remaining'),r.get('grade') or None,r.get('planned_term') or None,int(r.get('offered_spring','1') not in ('0','false','False')),int(r.get('offered_summer','0') in ('1','true','True')),int(r.get('offered_fall','1') not in ('0','false','False')),r.get('min_grade',''))
        c.execute('INSERT INTO course(code,name,credits,department,category,description,status,grade,planned_term,offered_spring,offered_summer,offered_fall,min_grade) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(code) DO UPDATE SET name=excluded.name,credits=excluded.credits,department=excluded.department,category=excluded.category,description=excluded.description,offered_spring=excluded.offered_spring,offered_summer=excluded.offered_summer,offered_fall=excluded.offered_fall,min_grade=excluded.min_grade',data); n+=1
    c.commit(); c.close(); flash(f'Imported {n} course records.','success'); return redirect(url_for('catalog'))

@app.get('/export/courses')
def export_courses():
    c=db(); rows=c.execute('SELECT * FROM course ORDER BY code').fetchall(); out=io.StringIO(); w=csv.writer(out); w.writerow(rows[0].keys() if rows else ['code','name']); w.writerows([tuple(x) for x in rows]); c.close(); return send_file(io.BytesIO(out.getvalue().encode()),mimetype='text/csv',as_attachment=True,download_name='tiger_course_catalog.csv')

@app.get('/export/student')
def export_student():
    c=db(); s=c.execute('SELECT * FROM student WHERE id=1').fetchone(); out=io.StringIO(); w=csv.writer(out); w.writerow(s.keys()); w.writerow(tuple(s)); c.close(); return send_file(io.BytesIO(out.getvalue().encode()),mimetype='text/csv',as_attachment=True,download_name='tiger_student.csv')

init_db()
if __name__=='__main__': app.run(debug=True)
