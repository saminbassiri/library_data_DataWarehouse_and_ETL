CREATE TABLE dist.Book(
	ISBN VARCHAR ( 13 ) PRIMARY KEY,
	title VARCHAR ( 50 ) NOT NULL,
	publisher VARCHAR ( 50 ) NOT NULL,
	version_number VARCHAR ( 13 ),
	description TEXT,
	number_of_valide_book_in_library INT NOT NULL,
    date_of_publish TIMESTAMP NOT NULL,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.Book_writer(
	book_ISBN VARCHAR ( 13 ),
	writer_fullname VARCHAR ( 50 ),
	tstamp  timestamp DEFAULT now(),
	PRIMARY KEY (book_ISBN, writer_fullname),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE dist.Book_language(
	book_ISBN VARCHAR ( 13 ),
	book_language VARCHAR ( 50 ),
	tstamp  timestamp DEFAULT now(),
	PRIMARY KEY (book_ISBN, book_language),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE dist.Book_translator(
	book_ISBN VARCHAR ( 13 ),
	translator_fullname VARCHAR ( 50 ),
	tstamp  timestamp DEFAULT now(),
	PRIMARY KEY (book_ISBN, translator_fullname),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE dist.Book_genre(
	book_ISBN VARCHAR ( 13 ),
	genre VARCHAR ( 50 ),
	tstamp  timestamp DEFAULT now(),
	PRIMARY KEY (book_ISBN, genre),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE dist.Members(
	membership_number VARCHAR ( 20 ) PRIMARY KEY,
	fullname VARCHAR ( 50 ) NOT NULL,
	phone_number VARCHAR ( 50 ) NOT NULL,
	adress TEXT NOT NULL,
	birthday TIMESTAMP NOT NULL,
    date_of_join TIMESTAMP NOT NULL,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.Rent(
	id_rent VARCHAR ( 20 ) PRIMARY KEY,
	rent_date TIMESTAMP NOT NULL,
	membership VARCHAR ( 50 ) NOT NULL,
	tstamp  timestamp DEFAULT now(),
	FOREIGN KEY (membership) REFERENCES Members(membership_number)
);
CREATE TABLE dist.Rent_details(
	id_rent VARCHAR ( 20 ), 
	book_ISBN VARCHAR ( 13 ),
	number_of_rent INT NOT NULL,
	day_of_rent INT NOT NULL,
	tstamp  timestamp DEFAULT now(),
	PRIMARY KEY (book_ISBN, id_rent),
	FOREIGN KEY (id_rent) REFERENCES Rent(id_rent) ON DELETE CASCADE,
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)
);
CREATE TABLE dist.change_Book(
	id_change SERIAL PRIMARY KEY ,
	ISBN VARCHAR ( 13 ) ,
	title VARCHAR ( 50 ) NOT NULL,
	publisher VARCHAR ( 50 ) NOT NULL,
	version_number VARCHAR ( 13 ),
	description TEXT,
	number_of_valide_book_in_library INT NOT NULL,
    date_of_publish TIMESTAMP NOT NULL,
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Book_writer(
	id_change SERIAL PRIMARY KEY,
	book_ISBN VARCHAR ( 13 ),
	writer_fullname VARCHAR ( 50 ),
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Book_language(
	id_change SERIAL PRIMARY KEY,
	book_ISBN VARCHAR ( 13 ),
	book_language VARCHAR ( 50 ),
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Book_translator(
	id_change SERIAL PRIMARY KEY,
	book_ISBN VARCHAR ( 13 ),
	translator_fullname VARCHAR ( 50 ),
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Book_genre(
	id_change SERIAL PRIMARY KEY,
	book_ISBN VARCHAR ( 13 ),
	genre VARCHAR ( 50 ),
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Members(
	id_change SERIAL PRIMARY KEY,
	membership_number VARCHAR ( 20 ) ,
	fullname VARCHAR ( 50 ) NOT NULL,
	phone_number VARCHAR ( 50 ) NOT NULL,
	adress TEXT NOT NULL,
	birthday TIMESTAMP NOT NULL,
    date_of_join TIMESTAMP NOT NULL,
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Rent(
	id_change SERIAL PRIMARY KEY,
	id_rent VARCHAR ( 20 ) ,
	rent_date TIMESTAMP NOT NULL,
	membership VARCHAR ( 50 ) NOT NULL,
	operation text,
	tstamp  timestamp DEFAULT now()
);
CREATE TABLE dist.change_Rent_details(
	id_change SERIAL PRIMARY KEY,
	id_rent VARCHAR ( 20 ), 
	book_ISBN VARCHAR ( 13 ),
	number_of_rent INT NOT NULL,
	day_of_rent INT NOT NULL,
	operation text,
	tstamp  timestamp DEFAULT now()
);
