
# coding: utf-8

# # sqlite3_tools
# 
# - [官方文档](https://www.sqlite.org/docs.html)
# - [官方文档 - SQL As Understood By SQLite](https://www.sqlite.org/lang_createtable.html)

# In[14]:


"""
- tool_name: sqlite3_tools
- version: 0.0.1
- date: 2019-05-09
- import: from mytools_database import sqlite3_tools
- func:

    1. assert_item(item=None, info=None)

        general func for tools
        :return: True if success; False if error 
    
    2. execute_sql(db=None, sql=None, params=None, exception_warningg=None)

        cursor.execute[many]_sql(sql, [params]) in db
        :return: cursor.fetchall() if success; False if error 

    3. vacuum_db(db=None, exception_warningg=None)

        vacuum db
        :return: True if success; False if error 

    4. get_tables(db=None, exception_warningg=None)

         get table list from db
        :return: list of all tables in db; False if error 

    5. drop_table(db=None, table=None, exception_warningg=None)

        drop table from db
        :return: True if success; False if error 

    6. get_table_infos(db=None, table=None, exception_warningg=None)

        get table infos ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk') in list; 
        :return: table_info of the table, ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk') in list; 
                 False if error 

    7. get_table_variables(db=None, table=None)

        get variables from table in dict format
        :return: variables dict of ('all','primary_keys','not_primary_keys'); False if error

    8. get_table_rows(db=None, table=None, exception_warning=None)

        get count of rows of table data
        :return: count of rows; False if error

    9. insert_data(db=None, table=None, data=None, many=None, replace=None, exception_warning=None)
        
        insert data or datas with many into table
        :return: True if success; False if error  

    10. get_df(db=None, table=None, exception_warningg=None)
        
        get df from table
        return: df; False if error    
        
    11. get_df_where(db=None, table=None, where=None, exception_warningg=None)
        
        get df from table, where is the namedtuple('WHERE',['variable','condition'])
        :return: df; False if error   

    12. delete_data(db=None, table=None, exception_warningg=None)

        delete all data in table
        :return  
        
    13. delete_data_where(db=None, table=None, where=None, exception_warningg=None)
    
        delete all data in table, where is the namedtuple('WHERE',['variable','condition'])
        return: True if success; False if error   
        
    13. select_all(db=None, table=None, exception_warning=None)
        select all from table
        :return: list; False if error 
        
"""

import sqlite3
import pprint
import pandas as pd
from collections import namedtuple


# In[11]:


def assert_item(item=None, info=None):
    """
    general func for tools
    :param item: item for check
    :param info: info if AssertionError occur
    :return: True if success; False if error 
    """    
    try:
        assert item
        return True
    except AssertionError:
        print(info)
        return False
    
def execute_sql(db=None, sql=None, params=None, many=None, exception_warning=None):
    """
    cursor.execute[many]_sql(sql, [params]) in db
    :param db: database name
    :param sql: sql 
    :param params: data or datas with many
    :param many: True for executemany
    :param exception_warning: True for print exception
    :return: cursor.fetchall() if success; False if error 
    """
    if not assert_item(item=db, info='no db input'):
        return False
    if not assert_item(item=sql, info='no sql input'):
        return False    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        if params and many:
            cursor.executemany(sql,params)
        elif params:
            cursor.execute(sql,params)
        else:
            cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        if exception_warning: 
            print(e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def vacuum_db(db=None, exception_warning=None):
    """
    vacuum db
    :param db: database name
    :param exception_warning: True for print exception
    :return: True if success; False if error 
    """
    sql = 'VACUUM;'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False
    print(f'database {db} VACUUM completed')
    return True
   
def get_tables(db=None, exception_warning=None):
    """
    get table list from db
    :param db: database name
    :param exception_warning: True for print exception
    :return: list of all tables in db; False if error 
    """
    sql = "SELECT NAME FROM SQLITE_MASTER WHERE TYPE='table' ORDER BY NAME;"
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False  
    tables = [_[0] for _ in result]
    return tables

def drop_table(db=None, table=None, exception_warning=None):
    """
    drop table from db
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: True if success; False if error 
    """
    if not assert_item(item=table, info='no table input'):
        return False       
    if not input(f'Please input y to confirm to delete the Table {table} in {db}\n') == 'y':
        return False
    sql = f'DROP TABLE {table};'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False
    print(f'Table {table} has been dropped!')
    return True

def get_table_infos(db=None, table=None, exception_warning=None):
    """
    get table infos ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk') in list; 
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: table_info of the table, ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk') in list; 
             False if error 
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    sql = f'PRAGMA table_info({table});'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False
    return result    

def get_table_variables(db=None, table=None):
    """
    get variables from table in dict format
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: variables dict of ('all','primary_keys','not_primary_keys'); False if error
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    fields = get_table_infos(db=db, table=table)
    if not assert_item(item=fields, info=f'no fields in {table}'):
        return False
    variables = {}
    variables['all'] = [field[1] for field in fields]
    variables['primary_key'] = [field[1] for field in fields if field[5] > 0]
    variables['not_primary_key'] = [field[1] for field in fields if field[5] == 0]
    return variables   
   
def get_table_rows(db=None, table=None, exception_warning=None):
    """
    get count of rows of table data
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: count of rows; False if error
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    sql = f'SELECT * FROM {table};'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False        
    return len(result)
     
def insert_data(db=None, table=None, data=None, many=None, replace=None, exception_warning=None):
    """
    insert data or datas with many into table
    :param db: database name
    :param table: table name
    :param data: data or datas with many
    :param many: True for executemany
    :param replace: Replace into the table
    :param exception_warning: True for print exception
    :return: True if success; False if error    
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    if not assert_item(item=data, info='no data input'):
        return False
    
    variables = get_table_variables(db=db, table=table)['all']
    _1 = ','.join(['?']*len(variables))
    sql = f'INSERT INTO {table} VALUES ({_1})'
    if replace:
        sql=sql.replace('INSERT INTO','REPLACE',1)
    
    result = execute_sql(db=db, sql=sql,params=data,many=many,exception_warning=exception_warning)
    if result == False:
        return False        
    return True

def get_df(db=None, table=None, exception_warning=None):
    """
    get df from table
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: df; False if error    
    """
    if not assert_item(item=db, info='no db input'):
        return False
    if not assert_item(item=table, info='no table input'):
        return False
    conn = sqlite3.connect(db)
    sql = f'SELECT * from {table}'
    try:
        df = pd.read_sql(sql,conn)
        return df
    except Exception as e:
        if exception_warning:
            print(e)
        return False
    finally:
        conn.close()

def get_df_where(db=None, table=None, where=None, exception_warning=None):
    """
    get df from table, where is the namedtuple('WHERE',['variable','condition'])
    :param db: database name
    :param table: table name
    :param where: eg..WHERE = namedtuple('WHERE',['variable','condition']); where = WHERE('AUTORUN_NAME',['funcB'])
    :param exception_warning: True for print exception
    :return: df; False if error    
    """
    if not assert_item(item=db, info='no db input'):
        return False    
    if not assert_item(item=table, info='no table input'):
        return False      
    if not where: # if no where
        print(f'where is {where} and return all')
        return get_df(db=db, table=table, exception_warning=exception_warning)    
    
    conn = sqlite3.connect(db)   
    variable = where.variable
    condition = [str(_) for _ in where.condition]
    condition = '","'.join(condition)
    sql = f'SELECT * FROM {table} WHERE {variable} IN ("{condition}")'
    try:
        df = pd.read_sql(sql,conn)
        return df
    except Exception as e:
        if exception_warning:
            print(e)
        return False
    finally:
        conn.close()
        
def delete_data(db=None, table=None, exception_warning=None):
    """
    delete all data in table
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: True if success; False if error    
    """
    if not assert_item(item=table, info='no table input'):
        return False    
    
    if not input(f'Please input y to confirm to delete the data in Table {table} in {db}\n') == 'y':
        return False
    
    sql = f'DELETE FROM {table};'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False
    print(f'Data in Table {table} has been deleted!')
    return True
    
def delete_data_where(db=None, table=None, where=None, exception_warning=None):
    """
    delete all data in table, where is the namedtuple('WHERE',['variable','condition'])
    :param db: database name
    :param table: table name
    :param where: eg..WHERE = namedtuple('WHERE',['variable','condition']); where = WHERE('AUTORUN_NAME',['funcB'])
    :param exception_warning: True for print exception
    :return: True if success; False if error     
    """
    if not assert_item(item=table, info='no table input'):
        return False    
    
    if not where: # if no where
        return delete_data(db=db, table=table, exception_warning=exception_warning)   
    
    variable = where.variable
    condition = [str(_) for _ in where.condition]
    condition = '","'.join(condition)
    info = f'Please input y to confirm to delete the data of {variable} if "{condition}" in Table {table} in {db}\n'
    
    if not input(info) == 'y':
        return False
    
    sql = f'DELETE FROM {table} WHERE {variable} IN ("{condition}")'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False
    print(f'Data of {variable} if {condition} in Table {table} has been deleted!')
    return True

def select_all(db=None, table=None, exception_warning=None):
    """
    select all from table
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: list; False if error    
    """
    if not assert_item(item=table, info='no table input'):
        return False    
    sql = f'SELECT * FROM {table};'
    result = execute_sql(db=db, sql=sql, exception_warning=exception_warning)
    if result == False:
        return False
    return result


# In[13]:


if __name__ == '__main__':
    print('=='*40)
    db = 'unitest/test_db.db'

    print('-'*40)
    print('example of vacuum db\n')          
    vacuum_db(db)

    print('-'*40)
    print('example of get_tables\n')
    tables = get_tables(db)
    print('table number is %s'%len(tables))
    print(tables)

    print('-'*40)
    print('example of get_table_infos\n')
    for table in tables:
        print(f"table {table}'s pragma is:")
        print(('cid','name','type','notnull','dflt_value','pk'))
        pprint.pprint(get_table_infos(db,table))
        
    print('-'*40)
    print('example of get_table_variables\n')
    table = 'AUTORUN_RECORD'
    print(f'Table {table} has variables:\n')
    pprint.pprint(get_table_variables(db=db,table=table))
          
    print('-'*40)
    print('example of get_table_rows\n') 
    for table in tables:
        print(f'Table {table} has {get_table_rows(db=db,table=table)} rows')
    
    print('-'*40)
    print('example of insert_data\n') 
    table = 'AUTORUN_RECORD'
    data = ('funcB','2019-05-07','0','funcA2')
    result = insert_data(db=db, table=table, data=data, exception_warning=True)
    data = ('funcB2','2019-05-07','0','funcA2')
    result = insert_data(db=db, table=table, data=data, exception_warning=True)
    print(result)

    print('-'*40)
    print('example of insert_data with many\n') 
    table = 'AUTORUN_RECORD'
    data = (('funcB','2019-05-07','0','funcA2'),('funcB2','2019-05-07','0','funcA2'))
    result = insert_data(db=db, table=table, data=data, many=True, exception_warning=True)
    print(result)

    print('-'*40)
    print('example of insert_data with replace\n') 
    table = 'AUTORUN_RECORD'
    data = (('funcB','2019-05-07','0','funcA2'),('funcB2','2019-05-07','0','funcA2'))
    result = insert_data(db=db, table=table, data=data, many=True, replace=True, exception_warning=True)
    print(result)
    
    print('-'*40)
    print('example of get_df\n') 
    df = get_df(db=db, table=tables[0])
    print(df)
          
    print('-'*40)
    print('example of get_df_where\n') 
    WHERE = namedtuple('WHERE',['variable','condition'])
    where = WHERE('AUTORUN_NAME',['funcB'])
    df = get_df_where(db=db, table=table, where=where, exception_warning=True)
    print(df)          
          
#     print('-'*40)
#     print('example of delete_data_where\n') 
#     WHERE = namedtuple('WHERE',['variable','condition'])
#     where = WHERE('AUTORUN_NAME',['funcB'])
#     result = delete_data_where(db=db, table=table, where=where, exception_warning=True)
#     print(result)  

    print('-'*40)
    print('example of select_all\n') 
    result = select_all(db=db, table=table, exception_warning=True)
    print(result)    
    
if __name__ == '__main__':
    print('=='*40)
    print('temple for create table:')
    db = 'unitest/test_db.db'
    table = 'product'
    sql = 'CREATE TABLE t(x INTEGER PRIMARY KEY DESC, y, z);'
    sql = 'CREATE TABLE t1(x INTEGER, y, z, PRIMARY KEY(x ASC,y));'
    sql = '''
    CREATE TABLE product(
    ID INTEGER PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL);
    '''
    # 在建表时声明id INTEGER PRIMARY KEY实际上是为rowid声明了一个别名，所以这也是为什么INTERGER主键默认自动增长的原因
    execute_sql(db=db, sql=sql, params=None, exception_warning=True) # 新建表
    print(get_table_variables(db,table))
    print(get_table_infos(db,table))

