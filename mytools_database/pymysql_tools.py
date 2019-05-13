
# coding: utf-8

# # pymysql_tools
# 
# - [官方文档 - pymysql](https://pymysql.readthedocs.io/en/latest/)
# - [官方文档 - aiomysql](https://aiomysql.readthedocs.io/en/latest/)
# - [其他参考 数据备份、pymysql模块](https://www.cnblogs.com/linhaifeng/articles/7525619.html)

# In[4]:


"""
- tool_name: pymysql_tools
- version: 0.0.1
- date: 2019-05-09
- import: from mytools_database import pymysql_tools
- requirements: pymysql_config with username etc...
- remark: with asyncio and aiomysql
- func:

    1. assert_item(item=None, info=None)

        general func for tools
        :return: True if success; False if error 
        
    2. get_mysql_config():
        
        general func for get mysql_config dict
        :return: mysql_config as dictionary
    
    3. async def execute_sql(db=None, sql=None, params=None, many=None, exception_warning=None):
    
        cursor.execute[many]_sql(sql, [params]) in db, in asyncio
        :return: cursor.fetchall() if success; False if error 

    4. get_databases(exception_warning=None)

        to show databases in mysql
        :return: databases in list 
        
    5. create_database(db=None,exception_warning=None):
        
        create a new database named db
        :return: True if success; False if error
        
    6. drop_database(db=None,exception_warning=None):

        drop database named db
        :return: True if success; False if error
            
    7. get_tables(db=None, exception_warningg=None)

         get table list from db
        :return: list of all tables in db; False if error 

    8. drop_table(db=None, table=None, exception_warningg=None)

        drop table from db
        :return: True if success; False if error 

    9. get_table_infos(db=None, table=None, exception_warningg=None)

        same as desc_table
        :return: ('Field','Type','Null','Key','Default','Extra'); False if error 


    10. desc_table(db=None, table=None, exception_warning=None):
        
        get table structure in db
        :return: ('Field','Type','Null','Key','Default','Extra'); False if error 

    11. get_table_variables(db=None, table=None)

        get variables from table in dict format
        :return: variables dict of ('all','primary_keys','not_primary_keys'); False if error

    12. get_table_rows(db=None, table=None, exception_warning=None)

        get count of rows of table data
        :return: count of rows; False if error

    13. insert_data(db=None, table=None, data=None, many=None, replace=None, exception_warning=None)
        
        insert data or datas with many into table
        :return: True if success; False if error  

    14. get_df(db=None, table=None, exception_warningg=None)
        
        get df from table
        return: df; False if error    
        
    15. get_df_where(db=None, table=None, where=None, exception_warningg=None)
        
        get df from table, where is the namedtuple('WHERE',['variable','condition'])
        :return: df; False if error   

    16. delete_data(db=None, table=None, exception_warningg=None)

        delete all data in table
        :return  
        
    17. delete_data_where(db=None, table=None, where=None, exception_warningg=None)
    
        delete all data in table, where is the namedtuple('WHERE',['variable','condition'])
        return: True if success; False if error   
        
    18. select_all(db=None, table=None, exception_warning=None)
        select all from table
        :return: list; False if error 
        
"""

import asyncio
import aiomysql
import pprint
import pymysql
import pandas as pd
from collections import namedtuple

import pymysql_config


# In[2]:


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

def get_mysql_config():
    """
    general func for get mysql_config dict
    :return: mysql_config as dictionary
    """
    mysql_config = dict(user=pymysql_config.user,
                        password=pymysql_config.password,
                        host=pymysql_config.host,
                        port=pymysql_config.port,
                        use_unicode=pymysql_config.use_unicode)
    return mysql_config

async def execute_sql(db=None, sql=None, params=None, many=None, exception_warning=None):
    """
    cursor.execute[many]_sql(sql, [params]) in db, in asyncio
    :param db: database name
    :param sql: sql 
    :param params: data or datas with many
    :param many: True for executemany
    :param exception_warning: True for print exception
    :return: cursor.fetchall() if success; False if error 
    """
    mysql_config = get_mysql_config()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if not db:
        pool = await aiomysql.create_pool(loop=loop, **mysql_config)
    else:
        pool = await aiomysql.create_pool(db=db, loop=loop, **mysql_config)
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if params and many:
                    await cursor.executemany(sql,params)
                elif params:
                    await cursor.execute(sql,params)
                else:
                    await cursor.execute(sql)
                result = await cursor.fetchall()
                await conn.commit() # 提交
                return result
    except Exception as e:
        if exception_warning:
            print(e)
        return False
    finally:
        pool.close()
        await pool.wait_closed()

def get_databases(exception_warning=None):
    """
    to show databases in mysql
    :param exception_warning: True for print exception
    :return: databases in list 
    """
    sql = 'SHOW DATABASES'
    result = asyncio.run(execute_sql(sql=sql, exception_warning=exception_warning))
    if result == False:
        return False
    dbs = [_[0] for _ in result]
    return dbs

def create_database(db=None,exception_warning=None):
    """
    create a new database named db
    :param db: database name
    :param exception_warning: True for print exception
    :return: True if success; False if error
    """
    if not assert_item(item=db, info='no db input'):
        return False
    sql = f'CREATE DATABASE {db} DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci'
    result = asyncio.run(execute_sql(sql=sql, exception_warning=exception_warning))
    if result == False:
        return False
    print(f'Database {db} Created!')
    return True

def drop_database(db=None,exception_warning=None):
    """
    drop database named db
    :param db: database name
    :param exception_warning: True for print exception
    :return: True if success; False if error
    """
    if not assert_item(item=db, info='no db input'):
        return False
    
    if not input(f'Please enter "y" to confirm to DROP DATABASE: {db}\n') == 'y':
        return False
    
    sql = f'DROP DATABASE {db}'
    result = asyncio.run(execute_sql(sql=sql,exception_warning=exception_warning))
    if result == False:
        return False
    
    print(f'Database {db} has been dropped!')
    return True 

def get_tables(db=None, exception_warning=None):
    """
    get tables list from db
    :param db: database name
    :param exception_warning: True for print exception
    :return: list of all tables in db; False if error 
    """
    sql = "SHOW TABLES;"
    result = asyncio.run(execute_sql(db=db, sql=sql, exception_warning=exception_warning))
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
    result = asyncio.run(execute_sql(db=db, sql=sql, exception_warning=exception_warning))
    if result == False:
        return False
    print(f'Table {table} has been dropped!')
    return True

def get_table_infos(db=None, table=None, exception_warning=None):
    """
    same as desc_table
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: ('Field','Type','Null','Key','Default','Extra'); False if error 
    """
    return desc_table(db=db, table=table, exception_warning=exception_warning)

def desc_table(db=None, table=None, exception_warning=None):
    """
    get table structure in db
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: ('Field','Type','Null','Key','Default','Extra'); False if error 
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    sql = f"DESC {table};"
    result = asyncio.run(execute_sql(db=db, sql=sql, exception_warning=exception_warning))
    if result == False:
        return False
    return result

def get_table_variables(db=None, table=None):
    """
    get variables from table in dict format
    :param db: database name
    :param table: table name
    :param exception_warning: True for print exception
    :return: variables dict of ('all','primary_keys','not_primary_keys','auto_increment'); False if error
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    fields = get_table_infos(db=db, table=table)
    if not assert_item(item=fields, info=f'no fields in {table}'):
        return False
    variables = {}
    variables['all'] = [field[0] for field in fields]
    variables['primary_key'] = [field[0] for field in fields if field[3] == 'PRI']
    variables['not_primary_key'] = [field[0] for field in fields if not field[3] == 'PRI']
    variables['auto_increment'] = [field[0] for field in fields if field[5] =='auto_increment']
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
    result = asyncio.run(execute_sql(db=db, sql=sql, exception_warning=exception_warning))
    if result == False:
        return False        
    return len(result)

def insert_data(db=None, table=None, data=None, many=None, 
                auto_increment=None, replace=None, exception_warning=None):
    """
    insert data or datas with many into table
    :param db: database name
    :param table: table name
    :param data: data or datas with many
    :param auto_increment: if True, can skip auto_increment data
    :param many: True for executemany
    :param replace: Replace into the table
    :param exception_warning: True for print exception
    :return: True if success; False if error 
    """
    if not assert_item(item=table, info='no table input'):
        return False  
    if not assert_item(item=data, info='no data input'):
        return False  
    
    variables = get_table_variables(db=db, table=table)
    if not auto_increment:
        variables = variables['all']
    else:
        _ais = variables['auto_increment']
        variables = variables['all']
        for _ai in _ais:
            variables.pop(variables.index(_ai))
    
    _1 = ','.join(variables)
    _2 = ','.join(['%s'] * len(variables))
    sql = f'INSERT INTO {table} ({_1}) VALUES ({_2});'
    if replace:
        sql=sql.replace('INSERT INTO','REPLACE',1)
    print(sql)
    result = asyncio.run(execute_sql(db=db,sql=sql,params=data,many=many,exception_warning=exception_warning))
    if result == False:
        return False        
    return True    

def get_df(db=None, table=None, exception_warning=None):
    """
    :param db:
    :param table:
    :param exception_warning: True for print exception
    :return: df; False if error    
    """
    if not assert_item(item=table, info='no table input'):
        return False
    if not assert_item(item=table, info='no table input'):
        return False
    mysql_config = get_mysql_config()
    conn = pymysql.connect(**mysql_config, database=db)
    sql = f'SELECT * from {table}'
    df = pd.read_sql(sql,conn)
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
    if not assert_item(item=table, info='no table input'):
        return False
    if not assert_item(item=table, info='no table input'):
        return False
    if not where: # if no where
        print(f'where is {where} and return all')
        return get_df(db=db, table=table, exception_warning=exception_warning)    
    
    mysql_config = get_mysql_config()
    conn = pymysql.connect(**mysql_config, database=db)
    variable = where.variable
    condition = [str(_) for _ in where.condition]
    condition = '","'.join(condition)
    sql = f'SELECT * FROM {table} WHERE {variable} IN ("{condition}")'
    df = pd.read_sql(sql,conn)
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
    result = asyncio.run(execute_sql(db=db, sql=sql, exception_warning=exception_warning))
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
    result = asyncio.run(execute_sql(db=db, sql=sql, exception_warning=exception_warning))
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
    result = asyncio.run(execute_sql(db=db,sql=sql,exception_warning=exception_warning))
    if result == False:
        return False
    return result


# In[3]:


if __name__ == '__main__':
    print('=='*40)
    print('test for mysql db relatate function')
    
    print('-'*40)
    print('Example of get_config:\n')
    mysql_config = get_mysql_config()
    print(mysql_config)
    
    print('-'*40)
    print('Example of async execute_sql:\n')    
    sql = 'SHOW DATABASES'
    result = asyncio.run(execute_sql(sql=sql))
    pprint.pprint(result)
    
    print('-'*40)
    print('Example of get_databases:\n')    
    dbs = get_databases(exception_warning=True)
    pprint.pprint(dbs)
    
#     print('-'*40)
#     print('Example of create_database:\n')
#     db = 'abc'
#     create_database(db=db,exception_warning=True)

#     print('-'*40)
#     print('Example of drop_database:\n')
#     db = 'abc'
#     drop_database(db=db,exception_warning=True)

if __name__ == '__main__':
    print('=='*40)
#     print('temple for create table:')
#     db='test'
#     table='product1'
#     sql='''
#     CREATE TABLE product1(
#     ID INTEGER PRIMARY KEY AUTO_INCREMENT,
#     Name NVARCHAR(100) NOT NULL);
#     '''
#     # 在建表时声明id INTEGER PRIMARY KEY实际上是为rowid声明了一个别名，所以这也是为什么INTERGER主键默认自动增长的原因
#     asyncio.run(execute_sql(db=db, sql=sql, params=None, exception_warning=True)) # 新建表
#     print(get_table_infos(db,table))


if __name__ == '__main__':
    print('=='*40)
    print('test for mysql table relatate function')
    mysql_config = get_mysql_config()
    print('-'*40)
    print('example of get_tables\n')
    db = 'test'
    tables = get_tables(db=db, exception_warning=True)
    print('table number is %s'%len(tables))
    print(tables)

#     print('-'*40)
#     print('example of drop_table\n')
#     db = 'test'
#     table = 'employee6'
#     result = drop_table(db=db, table=table, exception_warning=True)
#     pprint.pprint(result)
    
    print('-'*40)
    print('example of desc_table\n')
    db = 'test'
    table = 'product'
    result = desc_table(db=db, table=table, exception_warning=True)
    pprint.pprint(result)
    
    print('-'*40)
    print('example of get_table_variables\n')
    print(f'Table {table} has variables:\n')
    pprint.pprint(get_table_variables(db=db,table=table))
    
    print('-'*40)
    print('example of get_table_rows\n') 
    for table in tables:
        print(f'Table {table} has {get_table_rows(db=db,table=table)} rows')
    
    print('-'*40)
    print('example of insert_data\n') 
    db = 'test'
    table = 'product'
    data = (2,'def')
    result = insert_data(db=db, table=table, data=data, exception_warning=True)
    print(result)

    print('-'*40)
    print('example of insert_data with many\n') 
    db = 'test'
    table = 'product'
    data = ((3,'c'),(4,'d'))
    result = insert_data(db=db, table=table, data=data, many=True, exception_warning=True)
    print(result)

    print('-'*40)
    print('example of insert_data with many and replace\n') 
    db = 'test'
    table = 'product'
    data = ((3,'e'),(4,'f'))
    result = insert_data(db=db, table=table, data=data, many=True, replace=True, exception_warning=True)
    print(result)
    
    print('-'*40)
    print('example of insert_data with auto_increment\n') 
    db = 'test'
    table = 'product1'
    data = ('def')
    result = insert_data(db=db, table=table, data=data, auto_increment=True, exception_warning=True)
    print(result)

    print('-'*40)
    print('example of get_table_rows\n') 
    db = 'test'
    table = 'product1'
    result = get_table_rows(db=db, table=table, exception_warning=True)
    print(result)
    
    print('-'*40)
    print('example of get_df\n') 
    db = 'test'
    table = 'product'
    df = get_df(db=db, table=table)
    print(df)

    print('-'*40)
    print('example of get_df_where\n') 
    db = 'test'
    table = 'product'
    WHERE = namedtuple('WHERE',['variable','condition'])
    where = WHERE('ID',[1,2])
    df = get_df_where(db=db, table=table, where=where, exception_warning=True)
    print(df)  
    
#     print('-'*40)
#     print('example of delete_data\n') 
#     db = 'test'
#     table = 'product'
#     result = delete_data(db=db, table=table, exception_warning=True)
#     print(result)
    
#     print('-'*40)
#     print('example of delete_data_where\n') 
#     db = 'test'
#     table = 'product'
#     WHERE = namedtuple('WHERE',['variable','condition'])
#     where = WHERE('ID',['1'])
#     result = delete_data_where(db=db, table=table, where=where, exception_warning=True)
#     print(result)

    
    print('-'*40)
    print('example of select_all\n') 
    db = 'test'
    table = 'product'
    result = select_all(db=db, table=table, exception_warning=True)
    print(result)

