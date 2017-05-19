/*
 Скрипт, который реализует заполнение базы псевдопроизводльными данными.
 ТРЕБУЕТСЯ при полностью пустых таблицах.
 Команды в данном файле выполняються после создания таблиц students, subjects, assessments.
*/

-- Запрос добавляет в базу список из 20 предметов.
INSERT INTO subjects (title) VALUES
('Алгебра'), ('Геометрия'), ('Физика'), ('Экономика'), ('Английский'),
('Религия'), ('История'), ('ПТЦА'), ('Радиоматериалы'), ('Программирование'),
('Метрология'), ('Теория цепей'), ('Компьютерная графика'), ('Цифровые утсройства'), ('Философия'),
('Основы права'), ('Механика'), ('Радиоавтоматика'), ('Социология'), ('Политология');

/*
  Функция наполняет базу данных студетами, формируя случайные комбинации имен фамилий и отчеств
  из встроенных списков.
  Функция создает 50000 студетов.
*/
-- Создать функцию
CREATE OR REPLACE FUNCTION make_random_students()
RETURNS int AS $$
DECLARE
r record;
studentsCount int;
names VARCHAR[];
secondnames VARCHAR[];
middlenames VARCHAR[];
arr_names_length int;
arr_secondnames_length int;
arr_middlenames_length int;
BEGIN
studentsCount := 0;
names := ARRAY['Сергей', 'Антон', 'Михаил', 'Степан', 'Семен', 'Николай', 'Василий', 'Виктор', 'Геннадий', 'Александр',
                'Владимир', 'Денис', 'Дмитрий', 'Алексей', 'Константин', 'Евгений', 'Борис', 'Виталий', 'Станислав', 'Анатолий'];
secondnames := ARRAY['Сергеев', 'Антонов', 'Михаилов', 'Степанов', 'Семенов', 'Николаевский', 'Васильев', 'Викторов', 'Геннадиев', 'Александров',
                'Владимирский', 'Денисов', 'Дмитриев', 'Алексеев', 'Константинов', 'Евгениев', 'Борисов', 'Витальев', 'Станиславский', 'Анатольев'];
middlenames := ARRAY['Сергевич', 'Антонович', 'Михаилович', 'Степанович', 'Семенович', 'Николаевич', 'Васильевич', 'Викторович', 'Геннадьевич', 'Александрович',
                'Владимирович', 'Денисович', 'Дмитриевич', 'Алексеевич', 'Константинович', 'Евгениевич', 'Борисович', 'Витальевич', 'Станиславович', 'Анатольевич'];
arr_names_length := array_length(names, 1);
arr_secondnames_length := array_length(secondnames, 1);
arr_middlenames_length := array_length(middlenames, 1);
FOR i IN 1..50000
LOOP
    INSERT INTO students (firstName, secondName, middleName) VALUES
    (names[trunc(random()*arr_names_length)+1],
    secondnames[trunc(random()*arr_secondnames_length)+1],
    middlenames[trunc(random()*arr_middlenames_length)+1]);
    studentsCount := studentsCount+1;
END LOOP;
RETURN studentsCount;
END;
$$ LANGUAGE  plpgsql;

-- Выполнить функцию.
SELECT make_random_students();


/*
  Функция создает все возможные комбинации студентов и предметов, генеруя произвольную оценку
  по предмету.
  Функцию необходимо выполнять после заполнения таблиц предметов и студентов.
  При наличии в базе 50000 записей студентов и 20 предметов, функция создаст 1000000 оценок.
*/

-- Создать функцию
CREATE OR REPLACE FUNCTION make_random_assessments()
RETURNS int AS $$
DECLARE
student record;
subject record;
assessmentCount int;
BEGIN
assessmentCount := 0;
FOR student IN SELECT * FROM students LOOP
    FOR subject IN SELECT * FROM subjects LOOP
        INSERT INTO assessments (valuation, stId, sbId) VALUES
        (trunc(random()*5)+1, student.stID, subject.sbID);
        assessmentCount := assessmentCount+1;
    END LOOP;
END LOOP;
RETURN assessmentCount;
END;
$$ LANGUAGE  plpgsql;

-- Выполнить функцию.
SELECT make_random_assessments();