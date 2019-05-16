
# coding: utf-8

# # MissionPool

# In[2]:


"""
the decorator for mission, see the docs in the Class MissionLoop for detail
    - tool_name: MissionPool
    - version: 0.0.1
    - update date: 2019-05-14
    - import: from mytools_mission import MissionPool
"""

import threading


# In[11]:


class MissionPool():
    
    """
    the decorator for mission, see the docs in the Class MissionLoop for detail
        - tool_name: MissionPool
        - version: 0.0.1
        - update date: 2019-05-14
        - import: from mytools_mission import MissionPool
        
        - basic function:

            1. decorater_add_mission(mission_name=None,pre_mission_names=[],result_check=True, max_tries=10)

                decorator for add mission into loop

                - support function:  

                1. get_premission_names(self,mission_name=None,pre_mission_names=[])
        
                    decorator support tools for get pre_mission_names
                    :return: pre_mission_names

            2. def mission_pool_run(self):

                primary run function
                usage: mp.mission_pool_run()

                - support function:  
                
                1. check_pre_mission_names(self):
                
                    run support tools for check pre_mission_names
                    :return: True if all of pre_mission_names are in mission
                    
                2. mission_run(self,md=None,m=None):

                    run support tools for run mission

                3. print_report(self,md=None):
                    
                    run support tools for print report

    """

    def __init__(self,print_msg=True):
        """
        init the class
        :param print_msg: True for print report
        mission_set: for duplicated
        mission_dict: for record status
        prepard: True for run, False not run
        """
        self.mission_set = set()
        self.mission_dict = dict()
        self.prepared = False # run if True
        self.threadings = []
        self.print_msg = print_msg
    
    def decorater_add_mission(self,mission_name=None,pre_mission_names=[],result_check=True, max_tries=10):
        """
        decorator for add mission into loop
        :param mission_name: record mission_name, when None record func.__name__
        :param pre_mission_names: list of pre_mission_name
        :param result_check: True if result == result_check
        :param max_tries: max_tries
        """
        def decorator_func(func):
            # nonlocal because of decorator 
            nonlocal mission_name, pre_mission_names, result_check, max_tries 
            if not mission_name:
                mission_name = func.__name__
            # set mission with func
            if not mission_name in self.mission_set:
                pre_mission_names = self.get_premission_names(mission_name=mission_name,
                                                              pre_mission_names=pre_mission_names)
                self.mission_set.add(mission_name)
                self.mission_dict[mission_name] = {'status':False,
                                                   'func':func,
                                                   'result_check':result_check,
                                                   'pre_mission_names':pre_mission_names,
                                                   'max_tries':max_tries,
                                                   '_max_tries':max_tries,} # for init
            else:
                raise AssertionError(f'duplicated mission_name {mission_name}!')
            # for decorator format
            def wrapper():
                return func()
            return wrapper
        return decorator_func
    
    def get_premission_names(self,mission_name=None,pre_mission_names=[]):
        """
        decorator support tools for get pre_mission_names
        :param mission_name: check for delete if mission_name in pre_mission_names
        :param pre_mission_names: list of pre_mission_name
        :return: pre_mission_names
        """ 
        if isinstance(pre_mission_names,list):
            pre_mission_names = pre_mission_names
        elif isinstance(pre_mission_names,str):
            pre_mission_names = [pre_mission_names]
        else:
            pre_mission_names = []
        while mission_name in pre_mission_names:
            pre_mission_names.pop(pre_mission_names.index(mission_name)) 
        return pre_mission_names
    
    def mission_pool_run(self):
        """
        primary run function
        usage: asyncio.run(MP.mission_pool_run())
        """ 
        self.prepared = self.check_pre_mission_names()
        if not self.prepared:
            raise AssertionError('Error in mission! Not Run!')
        md = self.mission_dict # simlified self.mission_dict
        for m in md: # init missions, simplified mission
            md[m]['status'] = False
            md[m]['max_tries'] = md[m]['_max_tries']
        
        while self.stastic_dict(md=md,k='max_tries') and not self.stastic_dict(md=md,k='status') :
            self.threadings = []
            for m in md:
                if not md[m]['status'] and len(md[m]['pre_mission_names']):
                    if all(md[p]['status'] for p in md[m]['pre_mission_names']):
                        if md[m]['max_tries']:
                            t = threading.Thread(target=self.mission_run,kwargs={'md':md,'m':m})
                            self.threadings.append(t)
                elif not md[m]['status']:
                    if md[m]['max_tries']:
                        t = threading.Thread(target=self.mission_run,kwargs={'md':md,'m':m})
                        self.threadings.append(t)
            for t in self.threadings:
                t.start()
            for t in self.threadings:
                if t.isAlive():
                    t.join()
                        
        else:
            print('-=' * 20) 
            print('mission_pool_run_done! and the report is:') 
            self.print_report(md=md)
            print('=-' * 20) 
             
    def check_pre_mission_names(self):
        """
        run support tools for check pre_mission_names
        :return: True if all of pre_mission_names are in mission
        """ 
        for mission in self.mission_set:
            pre_mission_names = self.mission_dict[mission]['pre_mission_names']
            if pre_mission_names:
                for pre_mission_name in pre_mission_names:
                    if pre_mission_name not in self.mission_set:
                        print(f'Error pre_mission_name: {pre_mission_name} in mission: {mission}')
                        return False
        return True
    
    def stastic_dict(self,md=None,k=None):
        return all(md[m][k] for m in self.mission_set)
    
    def mission_run(self,md=None,m=None):
        """
        run support tools for run mission in asyncio
        :param md: simplified self.mission_dict
        :param m: simplified mission_name
        """
        result = md[m]['func']()
        if result == md[m]['result_check']:
            md[m]['status'] = True
        md[m]['max_tries'] -= 1
    
    def print_report(self,md=None):
        """
        run support tools for print report
        :param md: simplified self.mission_dict
        """ 
        if self.print_msg:
            for m in md:
                print(f"mission: {m}, status: {md[m]['status']}, pre_mission_names: {md[m]['pre_mission_names']}")
            


# In[22]:


# test of Mission Pool, with simple setting
if __name__ == '__main__':
    print('=' * 40)
    print('test of Mission Pool, with simple setting:\n')
    MP = MissionPool()
    @MP.decorater_add_mission(mission_name='a',pre_mission_names='b')
    def test_func():
        print('test_a')
        return False

    @MP.decorater_add_mission(mission_name='b',pre_mission_names=None,max_tries=5)
    def test_func():
        print('test_b')
        return False

    @MP.decorater_add_mission(mission_name='c',pre_mission_names=None)
    def test_func():
        print('test_c')
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    
    @MP.decorater_add_mission(mission_name='d',pre_mission_names=None)
    def test_func():
        print('test_d')
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    
    @MP.decorater_add_mission(mission_name='e',pre_mission_names=None)
    def test_func():
        print('test_e')
        return True      
    
    MP.mission_pool_run()


# In[23]:


# test of Mission Pool, with MissionLoop setting
if __name__ == '__main__':
    print('='*40)
    print('test of Mission Pool, with MissionLoop setting:\n')
    MP = MissionPool()
    from mytools_mission.MissionLoop import MissionLoop
    ML = MissionLoop()
    
    ML.set_loop(seconds=3, max_tries=5,daily_check=False,result_check=True)    
    @MP.decorater_add_mission(mission_name='a',pre_mission_names='b')
    @ML.decorator_loop(mission_name='a')
    def test_func_random(*args,**kwargs):
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False

    ML.set_loop(seconds=3, max_tries=5,daily_check=False,result_check=True)    
    @MP.decorater_add_mission(mission_name='b',pre_mission_names='b')
    @ML.decorator_loop(mission_name='b')
    def test_func_random(*args,**kwargs):
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
  
#     ML.set_loop(seconds=3, max_tries=5,daily_check=True,result_check=True)    
#     @MP.decorater_add_mission(mission_name='c',pre_mission_names='c',max_tries=1)
#     @ML.decorator_loop(mission_name='c')
#     def test_func_random(*args,**kwargs):
#         return False    
        
    MP.mission_pool_run()


# In[14]:


# test of Mission Pool, with MissionLoop and Misson Period Loop
if __name__ == '__main__':
    print('='*40)
    print('test of Mission Pool, with MissionLoop setting:\n')
    MP = MissionPool()
    from mytools_mission.MissionLoop import MissionLoop
    ML = MissionLoop()
        
    ML.set_loop(seconds=3, max_tries=5,daily_check=False,result_check=True)    
    @MP.decorater_add_mission(mission_name='c',pre_mission_names='c',max_tries=1)
    @ML.decorator_loop(mission_name='c')
    def test_func_random(*args,**kwargs):
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    
    import datetime
    p_mission_name = 'decorator_p_loop'
    p_period = 'ss' # for test 10 seconds
    p_start_time = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(seconds=5),'%H:%M:%S')
    p_result_check=True
    p_must_run=True
    ML.set_p_loop(p_period=p_period,p_start_time=p_start_time,p_result_check=True,p_must_run=None)

    @ML.decorator_p_loop(p_mission_name=p_mission_name)
    def mission_pool_run():
        MP.mission_pool_run()
        return True

    mission_pool_run()


# In[24]:


# MR test
if __name__ == '__main__':
    ML = MissionLoop()
    print(ML.MR.summary_mission_record(status=None))
    # ML.MR.clean_all_records()

