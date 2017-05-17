from src import app, get_db
from flask import render_template, flash


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
def students():
    db = get_db()
    cur = db.cursor()
    expected_fields = ('stid', 'secondname', 'firstname', 'middlename')
    cur.execute('SELECT {}, {}, {}, {} FROM students'.format(*expected_fields))
    cur.scroll(5)
    raw_students_list = cur.fetchmany(size=50)
    students_list = []
    for row in raw_students_list:
        named_fields = {}
        for i, val in enumerate(row):
            named_fields[expected_fields[i]] = val
        students_list.append(named_fields)

    flash('Тут должен быть список студентов.')
    return render_template("students_list.html",
                           title='Список студентов',
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
