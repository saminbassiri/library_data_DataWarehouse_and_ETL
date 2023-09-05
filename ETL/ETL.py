import psycopg2
from psycopg2 import Error
import networkx as nx


query_get_all_pk_of_tables_in_schema = '''
SELECT table_schema,table_name, column_name FROM information_schema.constraint_column_usage pk 
'''

quer_get_table_column_info = '''
SELECT column_name, udt_name, is_nullable, character_maximum_length
  FROM information_schema.columns
 WHERE table_schema = 'public'
   AND table_name   = 'book';
'''

test_query = '''INSERT INTO public.members(membership_number, fullname, phone_number, adress, birthday, date_of_join) VALUES (9, 'jjj', '3455', 'rrr', '1998-12-02 00:00:00', '1998-12-02 00:00:00');'''


get_fk_and_pk_query = '''SELECT 
  fk.table_name AS foreign_table, fk.column_name AS foreign_colomn,
  pk.table_name AS target_table, pk.column_name AS target_colomn
FROM 
  information_schema.referential_constraints rc 
  INNER JOIN information_schema.key_column_usage fk 
    ON (rc.constraint_catalog = fk.constraint_catalog 
        AND rc.constraint_schema = fk.constraint_schema 
        AND rc.constraint_name = fk.constraint_name) 
  INNER JOIN information_schema.constraint_column_usage pk 
    ON (rc.unique_constraint_catalog = pk.constraint_catalog 
        AND rc.unique_constraint_schema = rc.constraint_schema 
        AND rc.unique_constraint_name = pk.constraint_name);'''

get_schema_table ="""SELECT table_name FROM information_schema.tables WHERE table_schema = (%s)"""

select_row_of_table = """ SELECT * FROM  """

query_for_create_change_table ='''
    CREATE SCHEMA logging;
    CREATE TABLE logging.t_history (
            id  serial,
            tstamp  timestamp DEFAULT now(),
            schemaname  text,
            tabname text,
            operation text,
            who text  DEFAULT current_user,
            new_val json,
            old_val json
    );
  '''

query_chenge_trigger ='''  CREATE FUNCTION change_trigger() RETURNS trigger AS $$
            BEGIN
                    IF TG_OP = 'INSERT' THEN
                            INSERT INTO logging.t_history (tabname, schemaname, operation, new_val) VALUES (TG_RELNAME, TG_TABLE_SCHEMA, TG_OP, row_to_json(NEW));
                            RETURN NEW;
                    ELSIF   TG_OP = 'UPDATE' THEN
                            INSERT INTO logging.t_history (tabname, schemaname, operation, new_val, old_val) VALUES (TG_RELNAME, TG_TABLE_SCHEMA, TG_OP,row_to_json(NEW), row_to_json(OLD));
                            RETURN NEW;
                    ELSIF   TG_OP = 'DELETE' THEN
                            INSERT INTO logging.t_history (tabname, schemaname, operation, old_val) VALUES (TG_RELNAME, TG_TABLE_SCHEMA, TG_OP, row_to_json(OLD));
                            RETURN OLD;
                    END IF;
            END;
    $$ LANGUAGE 'plpgsql' SECURITY DEFINER;
'''


def get_query_apply_trigger_change(table):
    apply_change_trigger_on_a_table = """ CREATE TRIGGER t AFTER INSERT OR UPDATE OR DELETE ON """+ table +""" FOR EACH ROW EXECUTE PROCEDURE change_trigger();"""
    return apply_change_trigger_on_a_table


def connectdb(user,password,host,port,database):
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=user,
                                    password=password,
                                    host=host,
                                    port=port,
                                    database=database)

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    return connection

def create_dag_for_fk(source_connection,schema_name):
    cursor = source_connection.cursor()
    cursor.execute(get_fk_and_pk_query)
    pk_fk = list(map(lambda x: [x[0],x[1],x[2],x[3]], cursor.fetchall()))
    cursor.execute(get_schema_table,[schema_name])
    table_names= list(map(lambda x: x[0], cursor.fetchall()))
    vertexs = (list(map(lambda x: ("INSERT",x), table_names))) + (list(map(lambda x: ("DELETE",x), table_names)))
    edge = (list(map(lambda x: (("INSERT",x[2]),("INSERT",x[0])), pk_fk))) + (list(map(lambda x: (("DELETE",x[0]),("DELETE",x[2])), pk_fk)))
    #print(edge[0])
    dag = nx.DiGraph()
    dag.add_nodes_from(vertexs)
    dag.add_edges_from(edge)
    cursor.close()
    return dag

def create_table_for_change_in_source(source_connection,source_schema_name):
    cursor = source_connection.cursor()
    cursor.execute(query_for_create_change_table)
    cursor.execute(query_chenge_trigger)
    cursor.execute(get_schema_table,[source_schema_name])
    table_names= list(map(lambda x: x[0], cursor.fetchall()))
    for table in table_names:
      cursor.execute(get_query_apply_trigger_change(table))
    source_connection.commit()
    cursor.close()
    cursor

def insert_in_table(datas, connection,schema_name, table_name):
    cursor = connection.cursor()
    for data in datas:
      tmp_data = (tuple(map(lambda x: str(x) ,list(data))))
      cursor.execute("INSERT INTO "+ schema_name+"."+ table_name + " VALUES " + str(tmp_data))
    connection.commit()

def transfer_data_to_destination_db(source_connection, source_schema_name, dist_connection, dist_schema_name):
    cursor = source_connection.cursor()
    cursor.execute(get_schema_table,[source_schema_name])
    table_names= list(map(lambda x: x[0], cursor.fetchall()))
    for source_table in table_names:
        cursor.execute(select_row_of_table+source_schema_name+"."+str(source_table)) 
        records = list(cursor.fetchall())
        insert_in_table(records,dist_connection, dist_schema_name, source_table)

def apply_change_delete(source_connection,dist_connection, action, dist_schema_name, all_pk):
    table_name = action[3]
    cursor_dist = dist_connection.cursor()
    cursor_source = source_connection.cursor()
    table_pk = list(set([pk[2] for pk in all_pk if pk[1] == table_name and pk[0] == dist_schema_name]))
    old_row = action[-1]
    where_cond_list = [ " "+ table_pk_indx + "=" + "'" + old_row[table_pk_indx] + "'" + " " for table_pk_indx in table_pk]
    where_cond_str = " AND ".join(where_cond_list)
    query_delete_change_from_history = "DELETE FROM "+" logging.t_history " + " WHERE id  = " + str(action[0])+ ";"
    query_base_table = "DELETE FROM "+ dist_schema_name+"."+ table_name + " WHERE " + where_cond_str + ";"
    query_change_table = "INSERT INTO "+ dist_schema_name+"."+"change_"+ table_name + " " + str(tuple(old_row.keys())  + ('operation',)).replace("'", "") + " VALUES " + str(tuple(old_row.values()) + ('DELETE', )) + ";"
    try:
      cursor_dist.execute(query_base_table)
      cursor_dist.execute(query_change_table)
      dist_connection.commit()
    except (Exception, Error) as error:
        print("Eror in delete", error) 
    cursor_source.execute(query_delete_change_from_history)
    source_connection.commit()

def apply_change_update(source_connection,dist_connection, action, dist_schema_name, all_pk):
    table_name = action[3]
    cursor_dist = dist_connection.cursor()
    cursor_source = source_connection.cursor()
    table_pk = list(set([pk[2] for pk in all_pk if pk[1] == table_name and pk[0] == dist_schema_name]))
    old_row = action[-1]
    new_row = action[-2]
    where_cond_list = [ " "+ table_pk_indx + "=" + "'" + old_row[table_pk_indx] + "'" + " " for table_pk_indx in table_pk]
    where_cond_str = " AND ".join(where_cond_list)
    query_delete_change_from_history = "DELETE FROM "+" logging.t_history " + " WHERE id  = " + str(action[0])+ ";"
    query_base_table = "UPDATE "+ dist_schema_name+"."+ table_name +" SET "+ (str(tuple(old_row.keys()))).replace("'", "") + " = "+ str(tuple(new_row.values())) +" WHERE " + where_cond_str + ";"
    query_change_table = "INSERT INTO "+ dist_schema_name+"."+"change_"+ table_name + " " + str(tuple(old_row.keys())  + ('operation',)).replace("'", "") + " VALUES " + str(tuple(old_row.values()) + ('UPDATE', )) + ";"
    try:
      cursor_dist.execute(query_base_table)
      cursor_dist.execute(query_change_table)
      dist_connection.commit()
    except (Exception, Error) as error:
        print("Eror in update", error) 
    cursor_source.execute(query_delete_change_from_history)
    source_connection.commit()


def apply_change_insert(source_connection,dist_connection, action, dist_schema_name):
    table_name = action[3]
    cursor_dist = dist_connection.cursor()
    cursor_source = source_connection.cursor()
    new_row = action[-2]
    query_delete_change_from_history = "DELETE FROM "+" logging.t_history " + " WHERE id  = " + str(action[0])+ ";"
    query_base_table = "INSERT INTO "+ dist_schema_name + "." + table_name + " " + str(tuple(new_row.keys())).replace("'", "") + " VALUES " + str(tuple(new_row.values())) + ";"
    try:
      cursor_dist.execute(query_base_table)
      dist_connection.commit()
    except (Exception, Error) as error:
        print("Eror in insert", error) 
    cursor_source.execute(query_delete_change_from_history)
    source_connection.commit()


def apply_change(source_connection,dist_connection, dist_schema_name, graph):
    cursor_source = source_connection.cursor()
    cursor_source.execute(select_row_of_table+" logging.t_history ")
    list_of_change = list(cursor_source.fetchall())
    if list_of_change is not None and len(list_of_change) > 0:
      cursor_source.execute(query_get_all_pk_of_tables_in_schema)
      all_pk_source = list(cursor_source.fetchall())
      sorted_action_base_on_dag = list(nx.topological_sort(graph))
      delete_action = [t for t in list_of_change if t[4] == "DELETE"]
      inset_action = [t for t in list_of_change if t[4] == "INSERT"]
      update_action = [t for t in list_of_change if t[4] == "UPDATE"]
      delete_action = [tuple for x in sorted_action_base_on_dag for tuple in delete_action if (tuple[4],tuple[3]) == x]
      inset_action = [tuple for x in sorted_action_base_on_dag for tuple in inset_action if (tuple[4],tuple[3]) == x]
      
      for inset_action_indx in inset_action:
        print(str(inset_action_indx) + "\n")
        apply_change_insert(source_connection,dist_connection, inset_action_indx, dist_schema_name)
      
      for update_action_indx in update_action:
        print(str(update_action_indx) + "\n")
        apply_change_update(source_connection, dist_connection, update_action_indx, dist_schema_name, all_pk_source)
      
      for delet_action_indx in delete_action:
        print(str(delet_action_indx) + "\n")
        apply_change_delete(source_connection, dist_connection, delet_action_indx, dist_schema_name, all_pk_source)

def first_etl_transfer_data_to_dist(source_connection,dist_connection,dist_schema_name, source_schema_name):
  create_table_for_change_in_source(source_connection,source_schema_name)
  transfer_data_to_destination_db(source_connection, source_schema_name, dist_connection, dist_schema_name)
  source_connection.close()
  dist_connection.close()


def update_dist_base_on_change(source_connection,dist_connection,dist_schema_name, source_schema_name):
    graph = create_dag_for_fk(source_connection,source_schema_name)
    apply_change(source_connection,dist_connection, dist_schema_name, graph)
    source_connection.close()
    dist_connection.close()


source_connection = connectdb("postgres","pass","host","port","postgres")
dist_connection = connectdb("postgres","pass","host","port","postgres")
first_etl_transfer_data_to_dist(source_connection,dist_connection,'dist', 'public')
update_dist_base_on_change(source_connection,dist_connection,'dist', 'public')
