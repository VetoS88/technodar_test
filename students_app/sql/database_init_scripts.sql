-- Создаем базу данных для приложения.
CREATE DATABASE students;
-- Создаем пользователя для приложения.
CREATE ROLE professor WITH LOGIN PASSWORD 'professor';
-- Даем полномочия на базу данных пользователю.
GRANT ALL PRIVILEGES ON DATABASE students TO professor;
