# design and implementation of library database 

this project has three part:

1. Relational database 
2. ETL pipeline
3. Data Warehouse

### Relational database

This part consists of SQL queries to implement a relational database for library books and member information. All tables in this database design are in Fifth Normal Form (5NF) to remove redundancy in relational databases.

Each book could have several authors, genres, and languages. Moreover, each member could borrow more than one book, and if a book is borrowed, it is unavailable for other members.

### ETL pipeline

This part is used to transfer data from one database to another. For each table in the source DB, there is a table in the destination DB equal to this table. This pipeline should transfer each record individually. All insert, delete, and update actions on the source DB should be applied to the destination DB. Furthermore, due to the relationships between tables, a DAG should be created based on table relations to apply actions in the correct sequence. For instance, if  table A is related to table B with a FK, the node (delete, A) is connected to the node (delete, B), and the node (insert, B) is connected to (insert, A). To store and retrieve actions, there is also a table in the source DB called "t_history".

### Data Warehouse

This part is creating a database to track the history of the source BD, and it is different from "t_history" in the ETL pipeline. In this database, all tables from the source database are created with an extra column to track the timestamps of record insertion. Besides this, for each table in the source DB, there is another table to store records of every delete and update action on the source tables. This new database could help us retrieve a snapshot of the source database at any specific time.
