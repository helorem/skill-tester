CREATE TABLE question (
		id INTEGER PRIMARY KEY,
		name TEXT,
		language TEXT,
		text TEXT,
		qtype TEXT,
		answers TEXT,
		options TEXT
	);

CREATE TABLE test (
		id INTEGER PRIMARY KEY,
		username TEXT,
		creation_date DATE,
        finished INTEGER(1) DEFAULT 0
	);

CREATE TABLE test_question (
		test_id INTEGER,
		question_id INTEGER,
		num INTEGER,
		FOREIGN KEY(test_id) REFERENCES test(id) ON DELETE CASCADE,
		FOREIGN KEY(question_id) REFERENCES question(id) ON DELETE CASCADE
	);

CREATE TABLE answer (
		id INTEGER PRIMARY KEY,
		datetime DATE,
		text TEXT,
		success INTEGER(1) DEFAULT 0,
		test_id INTEGER,
		question_id INTEGER,
		FOREIGN KEY(test_id) REFERENCES test(id) ON DELETE CASCADE,
		FOREIGN KEY(question_id) REFERENCES question(id) ON DELETE CASCADE
	);

CREATE TABLE users (
		id INTEGER PRIMARY KEY,
		login TEXT,
		password TEXT
	);
