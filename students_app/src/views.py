import psycopg2

from src import app, get_db
from flask import render_template, flash, request
from src.config import STUDENTS_PER_PAGE
from src.utils import add_search_filters, filter_changed_data


@app.route('/')
@app.route('/index')
def index():
    greetings = "Добро пожаловать в систему учета успеваемости студентов."
    authors = [
        {'name': 'Виталий',
         'secondname': 'Копачёв'},
    ]

    return render_template("index.html",
                           title='Home',
                           greetings=greetings,
                           authors=authors)


@app.route('/students', methods=['GET'])
@app.route('/students/<int:page>', methods=['GET'])
def students(page=0):
    db = get_db()
    cur = db.cursor()
    expected_fields = ('stid', 'secondname', 'firstname', 'middlename')
    query_string = 'SELECT {}, {}, {}, {} FROM students'.format(*expected_fields)
    search_param = request.args.get('search_param', '')
    if search_param:
        query_string = add_search_filters(query_string, search_param)
    query_string += ' ORDER BY stid DESC'
    cur.execute(query_string)
    students_count = cur.rowcount
    try:
        cur.scroll(page * STUDENTS_PER_PAGE)
        raw_students_list = cur.fetchmany(size=STUDENTS_PER_PAGE)
    except psycopg2.ProgrammingError:
        raw_students_list = cur.fetchall()
    students_list = []
    for row in raw_students_list:
        named_fields = {}
        for i, val in enumerate(row):
            named_fields[expected_fields[i]] = val
        students_list.append(named_fields)
    return render_template("students_list.html",
                           title='Список студентов',
                           students_count=students_count,
                           students=students_list)


@app.route('/student/<int:student_id>', methods=['GET'])
def student(student_id, edit=0):
    db = get_db()
    cur = db.cursor()
    flash('Был передан id={} студента.'.format(student_id))
    expected_fields = ('assid', 'sbid', 'title', 'valuation',
                       'stid', 'secondname', 'firstname', 'middlename', student_id)
    query = 'SELECT {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7} ' \
            'FROM students LEFT JOIN assessments USING(stid)  LEFT JOIN subjects USING(sbid) ' \
            'WHERE stid={8}'.format(*expected_fields)
    cur.execute(query)
    student_card = cur.fetchall()
    subject_fields = ('sbid', 'title')
    subject_query = 'SELECT {}, {} FROM subjects'.format(*subject_fields)
    cur.execute(subject_query)
    all_subjects = cur.fetchall()
    student_id = student_card[0][4]
    student_full_name = {
        'secondname': student_card[0][5],
        'firstname': student_card[0][6],
        'middlename': student_card[0][7]
    }
    student_data = {(row[1], row[2]): row[3] for row in student_card if row[2]}
    for subject in all_subjects:
        student_data[subject] = student_data.get(subject, 'Нет оценки')
    template_name = 'update_student_card.html' if edit else 'student_card.html'
    return render_template(template_name,
                           title='Карточка студента',
                           student_data=student_data,
                           student_id=student_id,
                           student_full_name=student_full_name)


@app.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
def student_edit(student_id):
    if request.method == 'GET':
        return student(student_id, edit=1)
    elif request.method == 'POST':
        all_data = request.values
        students_data = {field: all_data[field] for field in all_data if 'st_' in field}
        subjects_data = {field: all_data[field] for field in all_data if 'sb_' in field}
        changed_students_data = filter_changed_data(students_data)
        changed_subjects_data = filter_changed_data(subjects_data)
        if changed_students_data:
            db = get_db()
            cur = db.cursor()
            query = 'UPDATE students ' \
                    'SET (secondname, firstname, middlename) VALUES (%s, %s, %s)'
            pass
        return render_template('student_update_success.html',
                               title='Карточка студента',
                               student_id=student_id)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        return render_template("new_student.html",
                               title='Добавление студента')
    elif request.method == 'POST':
        secondname = request.values.get('secondname', '')
        firstname = request.values.get('firstname', '')
        middlename = request.values.get('middlename', '')
        if not (secondname and firstname and middlename):
            flash('Проверте пожалуйста корректность введенных данных.')
            return render_template("new_student.html",
                                   secondname=secondname,
                                   firstname=firstname,
                                   middlename=middlename,
                                   title='Добавление студента')
        db = get_db()
        cur = db.cursor()
        query = 'INSERT INTO students (secondname, firstname, middlename) VALUES (%s, %s, %s)'
        cur.execute(query, (secondname, firstname, middlename))
        db.commit()
        return render_template("student_add_success.html",
                               secondname=secondname,
                               firstname=firstname,
                               middlename=middlename,
                               title='Добавление студента')