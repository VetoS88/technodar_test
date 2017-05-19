/*
После подключения к базе данных под пользователем professor.
psql -h localhost -U professor -d students
нужно выполнить команды по созданию таблиц
*/

-- Таблица для хранения о личности студента.
CREATE TABLE students(
stId SERIAL PRIMARY KEY,
firstName VARCHAR(64),
secondName VARCHAR(64),
middleName VARCHAR(64));

-- Таблица содержащая информацию о предметах.
CREATE TABLE subjects(
sbId SERIAL PRIMARY KEY,
title VARCHAR(64));

-- Таблица реализующая связь многое ко многим и хранящая данные об оценках студентов по предметам.
CREATE TABLE assessments(
assId SERIAL PRIMARY KEY,
valuation VARCHAR(64),
stId INTEGER REFERENCES students ON DELETE CASCADE,
sbId INTEGER REFERENCES subjects ON DELETE CASCADE,
UNIQUE (stId, sbId)
);