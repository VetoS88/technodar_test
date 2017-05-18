import psycopg2

from src import app, get_db
from flask import render_template, flash, request
from src.config import STUDENTS_PER_PAGE
from src.utils import add_search_filters


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
def student(student_id):
    db = get_db()
    cur = db.cursor()
    flash('Был передан id={} студента.'.format(student_id))
    expected_fields = ('assid', 'sbid', 'title', 'valuation',
                       'stid', 'secondname', 'firstname', 'middlename', student_id)
    query = 'SELECT {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7} ' \
            'FROM students JOIN assessments USING(stid) JOIN subjects USING(sbid) ' \
            'WHERE stid={8}'.format(*expected_fields)
    cur.execute(query)
    student_card = cur.fetchall()
    student_id = student_card[0][4]
    student_full_name = '{} {} {}'.format(student_card[0][5], student_card[0][6], student_card[0][7])
    student_data = [{'subject': row[2], 'valuation': row[3]} for row in student_card]
    return render_template("student_card.html",
                           title='Карточка студента',
                           student_data=student_data,
                           student_id=student_id,
                           student_full_name=student_full_name)


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
