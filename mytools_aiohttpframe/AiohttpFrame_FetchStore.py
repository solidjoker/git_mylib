
# coding: utf-8

# # AiohttpFrame_FetchStore
# - [aiohttp使用参考](https://www.jianshu.com/p/3de5c3626012)

# In[2]:


import aiohttp
import aiomysql
import asyncio
import pandas as pd
import traceback
import tqdm
from collections import defaultdict

from mytools_aiohttpframe.AiohttpFrame_Login import AiohttpFrame_Login


# In[28]:


class AiohttpFrame_FetchStore(AiohttpFrame_Login):
    """
    tools for aiohttpframe, see the docs in the Class AiohttpFrame_FetchStore for detail
        - tool_name: AiohttpFrame_FetchStore
        - version: 0.0.3
            - adjust delegate function with (*,**kwargs)
        - update date: 2019-05-15
        - import: from mytools_aiohttpframe import AiohttpFrame_FetchStore
        - inherit the class and must finish 2 delegate function:
            - 1. delegate_prepare_data
            - 2. delegate_sql_config
    """
    
    def __init__(self,chrome_path=None,cookies_jsonfile=None,headers=None,astime=None,chances=None): 
        """
        init the class and get the setting of chrome browser
        :param chrome_path: chrome_path, or AiohttpFrame_Config.chrome_path if None
        :param cookies_jsonfile: cookies_jsonfile, or AiohttpFrame_Config.cookies_jsonfile if None
        :param headers: headers, or AiohttpFrame_Config.headers if None        
        """   
        super(AiohttpFrame_FetchStore,self).__init__(chrome_path=chrome_path,
                                                     cookies_jsonfile=cookies_jsonfile,
                                                     headers=headers)
        self.cookies = self.ab_load_cookies()
        
        if astime == None:
            astime = 0.1
        self.astime = astime
        if chances == None:
            self.chances = 3
            
        try:
            asyncio.get_running_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    
    async def run(self,*args,**kwargs):
        params = self.delegate_set_tasks(*args,**kwargs)
        self._set_tasks(**params)
        return await self._run_tasks()
        # status,result = await self._run_tasks()
        # return status, result
    
    async def run_again(self,chances=None):
        if chances == None:
            chances = 3
        self.chances = chances
        return await self._run_tasks()
        # status,result = await self._run_tasks()
        # return status, result
        
    async def run_tasks(self,urls=None,datas=None,**kwargs):
        """
        main function to run tasks
        :param urls: urls
        :param datas: None for method get and datas for method post
        :return: (msg,result) in tuple
        """        
        self._set_tasks(urls=urls,datas=datas,**kwargs)
        return await self._run_tasks()
        # status,result = await self._run_tasks()
        # return status, result
    
    def _set_tasks(self, urls=None, datas=None, **kwargs):
        """
        init the tasks_status and remain_urls for track the tasks
        :param urls: urls
        :param datas: None for method get and datas for method post
        :return: None
        """
        if not datas:
            datas = [None] * len(urls)
        self.tasks_status = {
            task_id:{
                'params':{
                    'url':url,
                    'data':data,},
                'prepared_data':None,
                'stored':None,
                'status':None} 
            for task_id,(url,data) in enumerate(zip(urls,datas))
        }
        if kwargs:
            kwargs_dict = defaultdict(dict)
            for k in kwargs:
                for task_id,v in enumerate(kwargs[k]):
                    kwargs_dict[task_id].update({k:v})
            for task_id in self.tasks_status:
                self.tasks_status[task_id]['params'].update(kwargs_dict[task_id])
        
    async def _run_tasks(self):
        status = all((self.tasks_status[_]['status'] for _ in self.tasks_status))
        while not status and self.chances > 0:
            print(f'Runing, and remaining {self.chances} chances!')        
            loop_tasks = []
            for task_id in tqdm.tqdm(self.tasks_status):
                if not self.tasks_status[task_id]['status']:
                    if self.astime > 0:
                        await asyncio.sleep(self.astime)
                    task = asyncio.ensure_future(self.run_task(task_id=task_id,
                                                               **self.tasks_status[task_id]['params']))
                    if self.astime > 0:
                        await task
                    loop_tasks.append(task)
            result = await asyncio.wait(loop_tasks)
            status = self.summary_status()
            self.chances -= 1
        return status, result

    async def run_task(self,task_id=None,url=None,data=None,**kwargs):
        """
        function to run task
        :param task_idl: task_id for record         
        :param url: url
        :param data: None for method get and data for method post
        :return: True if success
        """
        print(f'task_id {task_id} is running!')
        async with aiohttp.ClientSession(headers=self.headers,cookies=self.cookies) as session:
            response = await self.fetch_url(session=session,url=url,data=data)     
            prepared_data = await self.prepare_data(response,**kwargs)
            if self.check_prepared_data(prepared_data):
                self.tasks_status[task_id]['status'] = True
                self.tasks_status[task_id]['prepared_data'] = prepared_data
                storedata = await self.store_data(prepared_data)
                if storedata:
                    self.tasks_status[task_id]['stored'] = True
                status = True
            else:
                status = False
            return status
    
    async def fetch_url(self,session=None,url=None,data=None):
        """
        support function to get response
        :param session: aiohttp.session
        :param ursl: url
        :param data: None for method get and data for method post
        :return: response.text(), None if Exception
        """
        try:
            if not data:
                async with session.get(url) as response:
                    return await response.text()
            else:
                async with session.post(url,data=data) as response:
                    return await response.text()
        except:
            traceback.print_exc()
            return None
    
    async def prepare_data(self,response=None,**kwargs):
        """
        support function to prepare_data for store
        need rewrite the delegate_prepare_data(response)
        :param response: response from function fetch_url
        :return: pandas.DataFrame from delegate_prepare_data(response) or list of datas
        """
        return self.delegate_prepare_data(response=response,**kwargs)

    def check_prepared_data(self,prepared_data=None):
        """
        function to check prepare_data
        :param prepare_data: prepare_data for check
        :return: True if success, None if empty
        """
        try:
            result = None if prepared_data.empty else True
        except:
            try:
                result = True if prepared_data else None
            except:
                result = None
        return result
                      
    async def store_data(self,prepared_data=None):
        """
        function to store prepare_data
        need rewrite the delegate_sql_config()
        :param prepare_data: prepare data for store
        :return: True if success, False if Exception occurs
        """
        try:
            host,port,user,password,db,use_unicode,table,variables,replace = self.delegate_sql_config()
            _1 = ','.join(variables)
            _2 = ','.join(['%s'] * len(variables))
            sql = f'INSERT INTO {table} ({_1}) VALUES ({_2});'
            if replace:
                sql=sql.replace('INSERT INTO','REPLACE',1) 
            if isinstance(prepared_data,pd.DataFrame):
                prepared_data = prepared_data.get_values().tolist()
            pool = await aiomysql.create_pool(host=host, port=port,
                                              user=user, password=password,
                                              db=db, use_unicode=use_unicode)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        await cur.executemany(sql,prepared_data)
                    except:
                        prepared_data = [list(map(str,_)) for _ in prepared_data]
                        await cur.executemany(sql,prepared_data)
                    await conn.commit()
            pool.close()
            await pool.wait_closed()
            return True
        except Exception as e:
            print(e)
            return False

    def summary_status(self):
        count_total = len(self.tasks_status)
        count_remain = count_total - sum((self.tasks_status[_]['status'] for _ in self.tasks_status))
        if not count_remain:
            print(f'All of total {count_total} missions success!')
            return True
        else:  
            print(f'All of total {count_total} missions\n'                   f'{count_total-count_remain} success! {count_remain} failed!')
            print('-'*40)
            print(f'asyncio.run(self.run_again() again!')
            print('-'*40)
            return False
    
    def delegate_set_tasks(self,*args,**kwargs):
        raise NotImplementedError
    
    def delegate_prepare_data(self,response=None,**kwargs):
        """
        support function to prepare_data for store
        need rewrite
        :param response: response from function fetch_url
        :return: pandas.DataFrame or list of datas, False if Exception occurs
        """
        raise NotImplementedError  

    def delegate_sql_config(self):
        """
        support function to set sql config
        need rewrite
        :return: (host,port,user,password,db,use_unicode,table,variables,replace) in tuples
        """
        raise NotImplementedError

