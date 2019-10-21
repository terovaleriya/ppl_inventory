CREATE TABLE students (
  student_id INTEGER PRIMARY KEY,
  student_name TEXT NOT NULL,
  birthday INTEGER);

CREATE TABLE subjects (
  subject_id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  teacher_name TEXT);

CREATE TABLE grades (
  grade_id INTEGER PRIMARY KEY,
  student_id INTEGER NOT NULL,
  subject_id INTEGER NOT NULL,
  grade INTEGER NOT NULL,
  day INTEGER,
  FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id),
  FOREIGN KEY (student_id)
    REFERENCES students (student_id));

INSERT INTO students (student_id, student_name, birthday)
VALUES
  (1, 'Иван Иванов', strftime('%s','2000-01-12')),
  (2, 'Мария Петрова', strftime('%s','2000-06-04')),
  (3, 'Анна Сидорова', strftime('%s','2001-02-25'));

INSERT INTO subjects (subject_id, title, teacher_name)
VALUES
  (1, 'Алгебра', 'Александр Козлов'),
  (2, 'Матан', 'Сергей Баранов');

INSERT INTO grades (grade_id, grade, student_id, subject_id, day)
VALUES
  (1, 10, 1, 2, strftime('%s','2019-09-01')),
  (2, 12, 2, 1, strftime('%s','2019-10-05')),
  (3, 5, 2, 2, strftime('%s','2019-09-11')),
  (4, 8, 3, 1, strftime('%s','2019-09-20'));
