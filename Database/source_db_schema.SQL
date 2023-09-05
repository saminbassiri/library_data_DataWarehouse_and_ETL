CREATE TABLE Book(
	ISBN VARCHAR ( 13 ) PRIMARY KEY,
	title VARCHAR ( 50 ) NOT NULL,
	publisher VARCHAR ( 50 ) NOT NULL,
	version_number VARCHAR ( 13 ),
	description TEXT,
	number_of_valide_book_in_library INT NOT NULL,
    date_of_publish TIMESTAMP NOT NULL
);
CREATE TABLE Book_writer(
	book_ISBN VARCHAR ( 13 ),
	writer_fullname VARCHAR ( 50 ),
	PRIMARY KEY (book_ISBN, writer_fullname),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE Book_language(
	book_ISBN VARCHAR ( 13 ),
	book_language VARCHAR ( 50 ),
	PRIMARY KEY (book_ISBN, book_language),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE Book_translator(
	book_ISBN VARCHAR ( 13 ),
	translator_fullname VARCHAR ( 50 ),
	PRIMARY KEY (book_ISBN, translator_fullname),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE Book_genre(
	book_ISBN VARCHAR ( 13 ),
	genre VARCHAR ( 50 ),
	PRIMARY KEY (book_ISBN, genre),
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)  ON DELETE CASCADE
);
CREATE TABLE Members(
	membership_number VARCHAR ( 20 ) PRIMARY KEY,
	fullname VARCHAR ( 50 ) NOT NULL,
	phone_number VARCHAR ( 50 ) NOT NULL,
	adress TEXT NOT NULL,
	birthday TIMESTAMP NOT NULL,
    date_of_join TIMESTAMP NOT NULL
);
CREATE TABLE Rent(
	id_rent VARCHAR ( 20 ) PRIMARY KEY,
	rent_date TIMESTAMP NOT NULL,
	membership VARCHAR ( 50 ) NOT NULL,
	FOREIGN KEY (membership) REFERENCES Members(membership_number)
);
CREATE TABLE Rent_details(
	id_rent VARCHAR ( 20 ), 
	book_ISBN VARCHAR ( 13 ),
	number_of_rent INT NOT NULL,
	day_of_rent INT NOT NULL,
	PRIMARY KEY (book_ISBN, id_rent),
	FOREIGN KEY (id_rent) REFERENCES Rent(id_rent) ON DELETE CASCADE,
	FOREIGN KEY (book_ISBN) REFERENCES Book(ISBN)
);
CREATE FUNCTION num_book_in_library() RETURNS trigger AS $num_book_in_library$ 
	DECLARE
   	total_book    INTEGER;
	BEGIN
		SELECT number_of_valide_book_in_library INTO total_book FROM book WHERE book.isbn = new.book_isbn;
		IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
			IF NEW.number_of_rent >  total_book THEN
				RAISE EXCEPTION 'not enough book in library';
			ELSE 
				UPDATE book SET number_of_valide_book_in_library = number_of_valide_book_in_library-NEW.number_of_rent WHERE book.isbn = new.book_isbn;
			END IF;
			RETURN NEW;
		ELSE
			UPDATE book SET number_of_valide_book_in_library = number_of_valide_book_in_library + OLD.number_of_rent WHERE book.isbn = OLD.book_isbn;
			RETURN OLD;
		END IF;
      
    END;
$num_book_in_library$ LANGUAGE plpgsql;

CREATE TRIGGER num_book_in_library BEFORE INSERT OR UPDATE OR DELETE ON Rent_details
    FOR EACH ROW EXECUTE FUNCTION num_book_in_library();
