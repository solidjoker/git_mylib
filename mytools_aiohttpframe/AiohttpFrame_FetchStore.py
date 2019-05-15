
# coding: utf-8

# # AiohttpFrame_FetchStore
# - [aiohttp使用参考](https://www.jianshu.com/p/3de5c3626012)

# In[2]:


"""
tools for aiohttpframe, see the docs in the Class AiohttpFrame_FetchStore for detail
    - tool_name: AiohttpFrame_FetchStore
    - version: 0.0.2
    - update date: 2019-05-15
    - import: from mytools_aiohttpframe import AiohttpFrame_FetchStore
"""
import aiohttp
import aiomysql
import asyncio
import datetime
import json
import pickle
import pandas as pd
import traceback

from mytools_aiohttpframe.AiohttpFrame_Login import AiohttpFrame_Login


# In[40]:


class AiohttpFrame_FetchStore(AiohttpFrame_Login):
    """
    tools for aiohttpframe, see the docs in the Class AiohttpFrame_FetchStore for detail
        - tool_name: AiohttpFrame_FetchStore
        - version: 0.0.2
        - update date: 2019-05-15
        - import: from mytools_aiohttpframe import AiohttpFrame_FetchStore
        - inherit the class and must finish 2 delegate function:
            - 1. delegate_prepare_data
            - 2. delegate_sql_config
        - example:
        --------------------------------------------------------------------
        class ToutiaoIndexFetchStore(AiohttpFrame_FetchStore):
        
        def delegate_prepare_data(self,response):
            try:
                data = json.loads(response)
                start = data['trends_range']['start']
                end = data['trends_range']['end']
                dateindex = pd.date_range(start=start,end=end,freq='D')
                keyword = list(data['trends'].keys())[0]
                datas = data['trends'][keyword]
                df = pd.DataFrame({'keyword':keyword,'date':dateindex,'data':datas})
                return df
            except Exception as e:
                print(e)
                return None

        def delegate_sql_config(self):
            host = 'localhost'
            port = 3306
            user = 'root'
            password = ''
            db = 'toutiaoindex'
            use_unicode = True
            sql_template = 'REPLACE %s (%s) VALUES ("%s");'
            table = 'data_toutiaoindex'
            variables = ['KEYWORDS','DATE','TOUTIAO_INDEX']
            return host,port,user,password,db,use_unicode,sql_template,table,variables
        
        def get_date_list(self,sd_date,ed_date,period=15,timefmt=None):
            # 得到日期的list[{sd_str,ed_str}]
            date_list = []
            count = (ed_date - sd_date).days // period + 1
            for i in range(1,count+1):
                date_list.append({'sd_str':(sd_date+datetime.timedelta(days=period*(i-1))).strftime(timefmt),
                                  'ed_str':(sd_date+datetime.timedelta(days=period*(i)-1)).strftime(timefmt)}) 
            date_list[-1]['ed_str'] = ed_date.strftime('%Y-%m-%d')  # 最后一组的最后一个日期 = EndDate
            return date_list
    
        def prepare_urls(self,region='0',category='0',is_hourly='0',start=None,end=None,period=7,keywords=None):
            urlformat = 'https://index.toutiao.com/api/keyword/trends?' \
            'region={region}&category={category}&keyword={keyword}&start={start}&end={end}&is_hourly={is_hourly}'
            timefmt = '%Y-%m-%d'      
            sd_date = datetime.datetime.strptime(start,timefmt)
            ed_date = datetime.datetime.strptime(end,timefmt)
            date_list = self.get_date_list(sd_date,ed_date,period=period,timefmt=timefmt)
            urls = [urlformat.format(region=region,category=category,is_hourly=is_hourly,
                                     start=d['sd_str'].replace('-',''),
                                     end=d['ed_str'].replace('-',''),
                                     keyword=keyword) for d in date_list for keyword in keywords]
            return urls
        
        def main():
            import pprint
            astime = 0
            TIFS = ToutiaoIndexFetchStore(astime=astime)

            region = '0' # 全国
            category = '0'
            keywords =  ['今日头条']# 可变 
            start = '2019-04-20'#  可变 >8天不能跑出数据
            end = '2019-05-10'# 可变
            is_hourly = '0' 
            urls = TIFS.prepare_urls(start=start,end=end,period=7,keywords=keywords)
            result = asyncio.run(TIFS.run_tasks(urls))

            print('results:')
            pprint.pprint(result)

            max_tries = 10

            while TIFS.remain_urls:
                print('=' * 40)
                print(f'left tries is {max_tries}')
                results = asyncio.run(TIFS.run_tasks(urls=TIFS.remain_urls,datas=TIFS.remain_datas))
                max_tries -= 1
                if not max_tries:
                    break

        main()
        --------------------------------------------------------------------
    """
    
    def __init__(self,chrome_path=None,cookies_jsonfile=None,headers=None,astime=None): 
        """
        init the class and get the setting of chrome browser
        :param chrome_path: chrome_path, or AiohttpFrame_Config.chrome_path if None
        :param cookies_jsonfile: cookies_jsonfile, or AiohttpFrame_Config.cookies_jsonfile if None
        :param headers: headers, or AiohttpFrame_Config.headers if None        
        """   
        super(AiohttpFrame_FetchStore,self).__init__(chrome_path=chrome_path,
                                                     cookies_jsonfile=cookies_jsonfile,
                                                     headers=headers)
        if astime == None:
            astime = 0.1
        self.astime = astime
        self.cookies = self.ab_load_cookies()
             
    async def run_tasks(self,urls=None,*,datas=None):
        """
        main function to run tasks
        :param urls: urls
        :param datas: None for method get and datas for method post
        :return: (msg,result) in tuple
        """
        self.set_tasks(urls=urls,datas=datas)
        loop_tasks = []
        for task_id in self.tasks_status:
            if not self.tasks_status[task_id]['status']:
                if astime > 0:
                    await asyncio.sleep(astime)
                task = asyncio.ensure_future(self.run_task(task_id=task_id,
                                                           url=self.tasks_status[task_id]['url'],
                                                           data=self.tasks_status[task_id]['data']))
                if astime > 0:
                    await task
                loop_tasks.append(task)
        result = await asyncio.wait(loop_tasks)
        status = self.report_summary()
        return status, result        
      
    def set_tasks(self,urls=None,*,datas=None):
        """
        init the tasks_status and remain_urls for track the tasks
        :param urls: urls
        :param datas: None for method get and datas for method post
        :return: None
        """
        try:
            asyncio.get_running_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if not datas:
            datas = [None] * len(urls)
        self.tasks_status = {task_id:{'url':url,'data':data,'response':None,'stored':None,'status':None} 
                             for task_id,(url,data) in enumerate(zip(urls,datas))}
        self.remain_urls = []
        self.remain_datas = []
    
    async def run_task(self,task_id=None,url=None,*,data=None):
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
            prepare_data = await self.prepare_data(response)
            if self.check_prepare_data(prepare_data):
                self.tasks_status[task_id]['status'] = True
                self.tasks_status[task_id]['response'] = prepare_data
                storedata = await self.store_data(prepare_data)
                if not storedata:
                    self.tasks_status[task_id]['stored'] = True
                status = True
            else:
                self.remain_urls.append(self.tasks_status[task_id]['url'])
                self.remain_datas.append(self.tasks_status[task_id]['data'])
                status = False
            print('-' * 40)
            print(f'task_id:{task_id} - storedata: {storedata}')    
            print(f'task_id:{task_id} - status: {status}')
            return status
    
    async def fetch_url(self,session=None, url=None, *, data=None):
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
    
    async def prepare_data(self,response=None):
        """
        support function to prepare_data for store
        need rewrite the delegate_prepare_data(response)
        :param response: response from function fetch_url
        :return: pandas.DataFrame from delegate_prepare_data(response)
        """
        return self.delegate_prepare_data(response)

    def check_prepare_data(self,prepare_data=None):
        """
        function to check prepare_data
        :param prepare_data: prepare_data for check
        :return: True if success, None if empty
        """
        try:
            result = None if prepare_data.empty else True
        except:
            try:
                result = True if prepare_data else None
            except:
                result = None
        return result
                      
    async def store_data(self,prepare_data=None):
        """
        function to store prepare_data
        need rewrite the delegate_sql_config()
        :param prepare_data: prepare data for store
        :return: True if success, False if Exception occurs
        """
        try:
            host,port,user,password,db,use_unicode,sql_template,table,variables = self.delegate_sql_config()
            pool = await aiomysql.create_pool(host=host, port=port,
                                              user=user, password=password,
                                              db=db, use_unicode=use_unicode)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    for row in prepare_data.get_values():
                        data = [str(_) for _ in row]
                        sql = sql_template%(table,','.join(variables),'","'.join(data))
                        # breakpoint()
                        await cur.execute(sql)
                    await conn.commit()
            pool.close()
            await pool.wait_closed()
            return True
        except Exception as e:
            print(e)
            return False

    def report_summary(self):
        count_remain = len(self.remain_urls)
        count_total = len(self.tasks_status)
        if not count_remain:
            print(f'All of total {count_total} missions success!')
            return True
        else:     
            print(f'All of total {count_total} missions\n'                  f'{count_total-count_remain} success! {count_remain} failed!')
            remain_urls_pkl = 'remain_urls.pkl'
            remain_datas_pkl = 'remain_datas.pkl'
            pickle.dump(self.remain_urls,open(remain_urls_pkl,'wb'))
            pickle.dump(self.remain_datas,open(remain_datas_pkl,'wb'))
            print(f'check the {remain_urls_pkl} and {remain_datas_pkl}')
            print(f'or asyncio.run(self.run_tasks(urls=self.remain_urls,datas=self.remain_datas)) again!')
            return False                
                      
    def delegate_prepare_data(self,response=None):
        """
        support function to prepare_data for store
        need rewrite
        :param response: response from function fetch_url
        :return: pandas.DataFrame or list, False if Exception occurs
        """
        raise NotImplementedError  
                      
    def delegate_sql_config(self):
        """
        support function to set sql config
        need rewrite
        :return: (host,port,user,password,db,use_unicode,sql,table,variables) in tuples
        """
        raise NotImplementedError


# In[41]:


if __name__ == '__main__':
    
    class ToutiaoIndexFetchStore(AiohttpFrame_FetchStore):
        
        def delegate_prepare_data(self,response):
            try:
                data = json.loads(response)
                start = data['trends_range']['start']
                end = data['trends_range']['end']
                dateindex = pd.date_range(start=start,end=end,freq='D')
                keyword = list(data['trends'].keys())[0]
                datas = data['trends'][keyword]
                df = pd.DataFrame({'keyword':keyword,'date':dateindex,'data':datas})
                return df
            except Exception as e:
                print(e)
                return None

        def delegate_sql_config(self):
            host = 'localhost'
            port = 3306
            user = 'root'
            password = ''
            db = 'toutiaoindex'
            use_unicode = True
            sql_template = 'REPLACE %s (%s) VALUES ("%s");'
            table = 'data_toutiaoindex'
            variables = ['KEYWORDS','DATE','TOUTIAO_INDEX']
            return host,port,user,password,db,use_unicode,sql_template,table,variables
        
        def get_date_list(self,sd_date,ed_date,period=15,timefmt=None):
            # 得到日期的list[{sd_str,ed_str}]
            date_list = []
            count = (ed_date - sd_date).days // period + 1
            for i in range(1,count+1):
                date_list.append({'sd_str':(sd_date+datetime.timedelta(days=period*(i-1))).strftime(timefmt),
                                  'ed_str':(sd_date+datetime.timedelta(days=period*(i)-1)).strftime(timefmt)}) 
            date_list[-1]['ed_str'] = ed_date.strftime('%Y-%m-%d')  # 最后一组的最后一个日期 = EndDate
            return date_list
    
        def prepare_urls(self,region='0',category='0',is_hourly='0',start=None,end=None,period=7,keywords=None):
            urlformat = 'https://index.toutiao.com/api/keyword/trends?'             'region={region}&category={category}&keyword={keyword}&start={start}&end={end}&is_hourly={is_hourly}'
            timefmt = '%Y-%m-%d'      
            sd_date = datetime.datetime.strptime(start,timefmt)
            ed_date = datetime.datetime.strptime(end,timefmt)
            date_list = self.get_date_list(sd_date,ed_date,period=period,timefmt=timefmt)
            urls = [urlformat.format(region=region,category=category,is_hourly=is_hourly,
                                     start=d['sd_str'].replace('-',''),
                                     end=d['ed_str'].replace('-',''),
                                     keyword=keyword) for d in date_list for keyword in keywords]
            return urls
        
    def main():
        import pprint
        astime = 0
        TIFS = ToutiaoIndexFetchStore(astime=astime)
        
        region = '0' # 全国
        category = '0'
        keywords =  ['今日头条']# 可变 
        start = '2019-04-20'#  可变 >8天不能跑出数据
        end = '2019-05-10'# 可变
        is_hourly = '0' 
        urls = TIFS.prepare_urls(start=start,end=end,period=7,keywords=keywords)
        result = asyncio.run(TIFS.run_tasks(urls))
    
        print('results:')
        pprint.pprint(result)

        max_tries = 10

        while TIFS.remain_urls:
            print('=' * 40)
            print(f'left tries is {max_tries}')
            results = asyncio.run(TIFS.run_tasks(urls=TIFS.remain_urls,datas=TIFS.remain_datas))
            max_tries -= 1
            if not max_tries:
                break
    
    main()


# In[1]:


if __name__ == '__main__':
    from mytools_database import pymysql_tools
    db = 'toutiaoindex'
    table = 'data_toutiaoindex'
    df = pymysql_tools.get_df(db=db,table=table)
    print(df)
    # df.to_excel('toutiao.xlsx')

