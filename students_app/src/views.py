"""
    Основная логика приложения 
    набор функциий выполняющих операции 
    по добавлению просмотру редактированию и удалению данных о студентах и предметах
"""

import psycopg2

from src import app, get_db
from flask import render_template, flash, request
from .configure import STUDENTS_PER_PAGE
from .utils import add_search_filters, filter_changed_data


@app.route('/')
@app.route('/index')
def index():
    """
        Рендерит шаблон главной страницы
    """
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
    """
        Выводит список пользователей.
        Есть функция пагинации( вывод осуществляется по 50 студентов)
        Выполняет функции поиска студентов
    """
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
    """
        Показывает данные о студенте и оценки по предметам(карточку студента). 
    """
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
    """
        Выполняет редактирование пользователя.
        Изменяет только те данные, которые были изменены в форме.
    """
    if request.method == 'GET':
        return student(student_id, edit=1)
    elif request.method == 'POST':
        all_data = request.values
        secondname = all_data.get('st_secondname', all_data.get('st_old_secondname', ''))
        firstname = all_data.get('st_firstname', all_data.get('st_old_firstname', ''))
        middlename = all_data.get('st_middlename', all_data.get('st_old_middlename', ''))
        students_data = {field: all_data[field] for field in all_data if 'st_' in field}
        subjects_data = {field: all_data[field] for field in all_data if 'sb_' in field}
        changed_students_data = filter_changed_data(students_data)
        changed_subjects_data = filter_changed_data(subjects_data)
        if changed_students_data:
            db = get_db()
            cur = db.cursor()
            values_for_update = []
            for key in changed_students_data:
                value = changed_students_data[key]
                key = key.replace('st_', '')
                values_for_update.append("{}='{}'".format(key, value))
            values_for_update = ','.join(values_for_update)
            query = "UPDATE students SET {} WHERE stid=%s".format(values_for_update)
            cur.execute(query, (student_id,))
            db.commit()
        if changed_subjects_data:
            db = get_db()
            cur = db.cursor()
            query_template = "INSERT INTO assessments (stid, sbid, valuation)" \
                             " VALUES {} ON CONFLICT (stId, sbId) " \
                             "DO UPDATE SET valuation=EXCLUDED.valuation"
            update_subjects = [str((student_id, int(subject.replace('sb_', '')), changed_subjects_data[subject]))
                               for subject in changed_subjects_data]
            query = query_template.format(','.join(update_subjects))
            cur.execute(query)
            db.commit()
        return render_template('student_update_success.html',
                               title='Успешное обновление данных',
                               secondname=secondname,
                               firstname=firstname,
                               middlename=middlename,
                               student_id=student_id)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """
        Добавление студента. 
    """
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
                               title='Успешное добавление студента')


@app.route('/student/delete/<int:student_id>', methods=['GET', 'POST'])
def student_delete(student_id):
    """
        Удаление студента с подтверждением.
    """
    if request.method == 'GET':
        db = get_db()
        cur = db.cursor()
        expected_fields = ('stid', 'secondname', 'firstname', 'middlename')
        query_string = 'SELECT {}, {}, {}, {} FROM students WHERE stid=%s'.format(*expected_fields)
        cur.execute(query_string, (student_id,))
        student_entry = cur.fetchall()
        secondname = student_entry[0][1]
        firstname = student_entry[0][2]
        middlename = student_entry[0][3]
        return render_template("student_delete_confirmation.html",
                               secondname=secondname,
                               firstname=firstname,
                               middlename=middlename,
                               student_id=student_id,
                               title='Подтверждение удаления студента')
    elif request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        query_string = 'DELETE FROM students WHERE stid=%s RETURNING *'
        cur.execute(query_string, (student_id,))
        student_entry = cur.fetchall()
        secondname = student_entry[0][1]
        firstname = student_entry[0][2]
        middlename = student_entry[0][3]
        db.commit()
        return render_template("student_delete_success.html",
                               secondname=secondname,
                               firstname=firstname,
                               middlename=middlename,
                               student_id=student_id,
                               title='Успешное удаление студента')


@app.route('/subjects', methods=['GET'])
def subjects():
    """
        Список предметов.
    """
    db = get_db()
    cur = db.cursor()
    query_string = 'SELECT * FROM subjects ORDER BY sbid ASC'
    cur.execute(query_string)
    subjects_count = cur.rowcount
    subjects_list = cur.fetchall()
    return render_template("subjects_list.html",
                           title='Список предметов',
                           subjects_count=subjects_count,
                           subjects_list=subjects_list)


@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    """
        Добавление предмета.
    """
    if request.method == 'GET':
        return render_template("add_subject.html",
                               title='Добавить новый предмет', )
    elif request.method == 'POST':
        new_subject_title = request.values.get('title', '')
        if new_subject_title:
            db = get_db()
            cur = db.cursor()
            query_string = 'INSERT INTO subjects (title) VALUES (%s) RETURNING *'
            cur.execute(query_string, (new_subject_title,))
            subject_entry = cur.fetchall()[0]
            subject_id = subject_entry[0]
            db.commit()
            return render_template('update_subject.html',
                                   title='Редактирование предмета',
                                   subject=subject_entry,
                                   subject_id=subject_id)
        else:
            flash('Проверте пожалуйста корректность введенных данных.')
            return render_template("add_subject.html",
                                   title='Добавить новый предмет',
                                   subject_title=new_subject_title)


@app.route('/subject/edit/<int:subject_id>', methods=['GET', 'POST'])
def subject_edit(subject_id):
    """
        Редактирование названия предмета.
    """
    if request.method == 'GET':
        db = get_db()
        cur = db.cursor()
        query_string = 'SELECT * FROM subjects WHERE sbid=%s'
        cur.execute(query_string, (subject_id,))
        subject_entry = cur.fetchall()
        return render_template('update_subject.html',
                               title='Редактирование предмета',
                               subject=subject_entry[0],
                               subject_id=subject_id)
    elif request.method == 'POST':
        new_title = request.values.get('title', request.values.get('old_title', ''))
        old_title = request.values.get('old_title', '')
        if new_title != old_title:
            db = get_db()
            cur = db.cursor()
            query_string = 'UPDATE subjects SET title=%s WHERE sbid=%s RETURNING *'
            cur.execute(query_string, (new_title, subject_id))
            subject_entry = cur.fetchall()[0]
            db.commit()
            flash('Данные о предмете обновлены.')
        else:
            subject_entry = (subject_id, old_title)
        return render_template('update_subject.html',
                               title='Редактирование предмета',
                               subject=subject_entry,
                               subject_id=subject_id)


@app.route('/subject/delete/<int:subject_id>', methods=['GET', 'POST'])
def subject_delete(subject_id):
    """
        Удаление предмета с подтверждением.
    """
    if request.method == 'GET':
        db = get_db()
        cur = db.cursor()
        query_string = 'SELECT * FROM subjects WHERE sbid=%s'
        cur.execute(query_string, (subject_id,))
        subject_entry = cur.fetchall()
        return render_template('subject_delete_confirmation.html',
                               title='Удаление предмета',
                               subject=subject_entry[0],
                               subject_id=subject_id)
    elif request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        query_string = 'DELETE FROM subjects WHERE sbid=%s RETURNING *'
        cur.execute(query_string, (subject_id,))
        subject_entry = cur.fetchall()[0]
        db.commit()
        return render_template("subject_delete_success.html",
                               subject_entry=subject_entry,
                               title='Успешное удаление предмета')
