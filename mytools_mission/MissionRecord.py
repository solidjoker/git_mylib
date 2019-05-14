
# coding: utf-8

# # MissionRecord

# In[2]:


"""
the decorator for mission record, see the docs in the Class MissionRecord for detail
    - tool_name: MissionRecord
    - version: 0.0.2
    - update date: 2019-05-10
    - import: from mytools_mission import MissionRecord
"""

import datetime
from functools import wraps
from collections import namedtuple
import os

from mytools_database import sqlite3_tools


# In[3]:


class MissionRecord:
    """
    the decorator for mission record, see the docs in the Class MissionRecord for detail
        - tool_name: MissionRecord
        - version: 0.0.2
        - update date: 2019-05-10
        - import: from mytools_mission import MissionRecord
        - basic function:

            1. decorator_mission_record(self,mission_name=None)

                decorator for mission record
                :param exception_warning: True for print exception

        - support function:  

            1. init_db_table(self)

                init the database and the table: MISSION_RECORD.db/MISSION_RECORD
                :return: True if success; False if exception occurs

            2. clean_all_records(self)

                clean all records in the table: MISSION_RECORD.db/MISSION_RECORD
                :return: True if success; False if exception occurs

            3. clean_false_record(self)

                clean the false records whose status == 0
                :return: True if success; False if exception occurs

            4. clean_mission_record(self,mission_name=None)

                clean the mission_name records
                :return: True if success; False if exception occurs

        - statistics function:  

            1. summary_mission_record(self,period=None,status=True,mission_name=None)

                get the summary of mission record in df 
                :return: df

            2. check_mission_success(self,mission_name=None, date=None):

                get the mission success counts
                :return: int, False if exception occurs
    """        
    
    def __init__(self,exception_warning=None):
        """
        init the class and init the database and the table: MISSION_RECORD.db/MISSION_RECORD
        :param exception_warning: True for print exception
        """
        self._timefmt = '%Y-%m-%d %H:%M:%S'
        self._mission_name = 'MISSION_NAME'
        self._date = 'DATE'
        self._status = 'STATUS'
        self._period_dict = {'y':4, 'm':7, 'd':10, 'hh':13,'mm':16,'ss':19} # for statistics
        self.exception_warning = exception_warning
        try:
            basedir = os.path.dirname(os.path.abspath(__file__)) # abspath
        except:
            basedir = './'
        self.db = os.path.join(basedir,'MISSION_RECORD.db')
#         print(os.path.abspath(self.db))
#         print('db path:',os.path.abspath(self.db))
        self.table = 'MISSION_RECORD'
        self.init_db_table()
        
    def decorator_mission_record(self,mission_name=None):
        """
        decorator for mission record
        :param mission_name: record mission_name, when None record func.__name__
        """
        def decorator_func(func):
            # 修饰器，记录函数运行
            @wraps(func)
            def wrapper(*args,**kwargs):
                result = func(*args, **kwargs)
                now = datetime.datetime.now().strftime(self._timefmt)
                status = True if result else False
                if mission_name:
                    data = (mission_name,now,status)
                else:
                    data = (func.__name__,now,status)              
                sqlite3_tools.insert_data(db=self.db,table=self.table,
                                          data=data,exception_warning=self.exception_warning)
                return result
            return wrapper
        return decorator_func

    def init_db_table(self):
        """
        init the database and the table: _mission_record.db/MISSION_RECORD
        :return: True if success; False if exception occurs
        """
        try:
            sql = f'''
            CREATE TABLE {self.table}(
            {self._mission_name} TEXT NOT NULL,
            {self._date} DATETIME NOT NULL,
            {self._status} BOOLEAN NOT NULL
            )
            '''
            # create the db
            sqlite3_tools.execute_sql(db=self.db,sql=sql,exception_warning=self.exception_warning)
            # vaccum the db
            sqlite3_tools.vacuum_db(db=self.db,exception_warning=self.exception_warning)  
            return True
        except Exception as e:
            if self.exception_warning:
                print(e)
            return False
        
    def clean_all_records(self):
        """
        clean all records in the table: MISSION_RECORD.db/MISSION_RECORD
        :return: True if success; False if exception occurs
        """
        return sqlite3_tools.delete_data(db=self.db,table=self.table,exception_warning=self.exception_warning) 
    
    def clean_false_record(self):
        """
        clean the false records whose status == 0
        :return: True if success; False if exception occurs
        """
        WHERE = namedtuple('WHERE',['variable','condition'])
        where = WHERE('STATUS',[0])
        result = sqlite3_tools.delete_data_where(db=self.db,table=self.table,
                                                 where=where,exception_warning=self.exception_warning)
        return result  
        
    def clean_mission_record(self,mission_name=None):
        """
        clean the mission_name records
        :param mission_name: mission_name
        :return: True if success; False if exception occurs
        """
        if not sqlite3_tools.assert_item(item=mission_name,info='no mission name input!'):
            return False
        WHERE = namedtuple('WHERE',['variable','condition'])
        where = WHERE('MISSION_NAME',[mission_name])        
        result = sqlite3_tools.delete_data_where(db=self.db,table=self.table,
                                                 where=where,exception_warning=self.exception_warning)
        return result  
    
    def summary_mission_record(self,period=None,status=True,mission_name=None):
        """
        get the summary of mission record in df 
        :param period: 'y':4, 'm':7, 'd':10, 'hh':13,'mm':16,'ss':19
        :param status: True for success only, None for all 
        :param mission_name: mission_name
        :return: df
        """
        if not period:
            period = 'd'
        lenth = self._period_dict.get(str(period).lower(), 'd')
        df = sqlite3_tools.get_df(db=self.db,table=self.table,exception_warning=self.exception_warning)        
        df['Period'] = df[self._date].apply(lambda x: x[:lenth])
        df = df.groupby(['Period',self._mission_name,self._status]).count()
        df = df.reset_index().rename(columns={self._date:'Count'})
        if status:
            df = df[df[self._status]==1]
        if mission_name:
            df = df[df[self._mission_name] == mission_name]
        return df
    
    def check_mission_success(self,mission_name=None, date=None):
        """
        get the mission success counts
        :param mission_name: mission_name
        :param date: None for today, else for the appoint date in '%Y-%m-%d' format
        :return: int
        """
        if not sqlite3_tools.assert_item(item=mission_name,info='no mission name input!'):
            return False
        df = self.summary_mission_record(period='d',status=True,mission_name=mission_name)
        try:
            if not date:
                date = datetime.date.today().isoformat()
            return df[df['Period']==date]['Count'].iloc[0]
        except Exception as e:
            print(e)
            return False


# In[4]:


if __name__ == '__main__':
    print('=='*40)
    MR = MissionRecord() 
    
#     print('-'*40)
#     print('example of init_record\n')     
#     MR.clean_all_records() 

#     print('-'*40)
#     print('example of clean_false_record\n')     
#     MR.clean_false_record() 

#     print('-'*40)
#     print('example of clean_mission_record\n')  
#     MR.clean_mission_record(mission_name='test_with_name')

    from random import randint
    print('-'*40)    
    print('example of decorator_mission_record with mission_name\n')    
    @MR.decorator_mission_record(mission_name='test_with_mission_name')
    def test_with_mission_name(*args, **kwargs): 
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    test_with_mission_name()
    
    print('-'*40)    
    print('example of decorator_mission_record without mission_name\n')    
    @MR.decorator_mission_record()
    def test_without_mission_name(*args, **kwargs): 
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    test_without_mission_name()
    
    print('=='*40)
    print('statistics function:')    
    
    print('-'*40)    
    print('example of summary_mission_record\n')  
    df = MR.summary_mission_record(period=None,status=True)
    print(df)

    print('-'*40)    
    print('example of summary_mission_record all\n')  
    df = MR.summary_mission_record(status=None)
    print(df)
    
    print('-'*40)    
    print('example of summary_mission_record with mission_name\n')  
    df = MR.summary_mission_record(period='d',status=True,mission_name='test_with_name')
    print(df)
    
    print('-'*40)    
    print('example of summary_mission_record with period\n')  
    df = MR.summary_mission_record(period='mm',status=True)
    print(df)

