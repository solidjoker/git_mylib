
# coding: utf-8

# # MissionLoop

# In[12]:


"""
the decorator for mission record, see the docs in the Class MissionLoop for detail
    - tool_name: MissionLoop
    - version: 0.0.2
    - update date: 2019-05-10
    - import: from mytools_mission import MissionLoop
    - two decorator for function:
        - 1. decorator_loop(self,mission_name=None)
        - 2. decorator_p_loop(self,p_mission_name=None)
        
"""

import datetime
import time
from functools import partial,wraps
from dateutil.relativedelta import relativedelta
from math import ceil

from mytools_mission import MissionRecord

from mytools_sendmail import SendMail
from mytools_sendmail import SendMail_config


# In[13]:


class MissionLoop():
    """
    the decorator for mission record, see the docs in the Class MissionLoop for detail
        - tool_name: MissionLoop
        - version: 0.0.2
        - update date: 2019-05-10
        - import: from mytools_mission import MissionLoop
        - two decorator for function:
        
            - 1. decorator_loop(self,mission_name=None)
                
                record as mission_name in db, repeat max_tries if False 
                :param mission_name: mission_name
                :return: True if success and finished
                
                example:
                
                ML = MissionLoop()
                ML.set_loop(seconds=3, max_tries=3, daily_check=None,result_check=True)
                @ML.decorator_loop(mission_name='MissionAutorunTestDailyCheckNone')
                def test_func(*args,**kwargs):
                    pass
                    
            - 2. decorator_p_loop(self,p_mission_name=None)
                    
                decorator function, loop no matter func success or not  
                :param p_mission_name: p_mission_name
                :return: True if success and finished  
                
                example:
                
                ML = MissionLoop()
                ML.set_p_loop(p_period='d',p_start_time=None,p_result_check=True,p_must_run=None)
                p_mission_name = 'my p loop test'
                @ML.decorator_p_loop(p_mission_name=p_mission_name)
                def test_p_func_random(*args,**kwargs):
                    return False
                    
            - 3. combine decorator_loop with decorator_p_loop,
                
                example:
                
                ML = MissionLoop()
                ML.set_p_loop(p_period='d',p_start_time=None,p_result_check=True,p_must_run=None)
                p_mission_name = 'my p loop test'
                ML.set_loop(seconds=5, max_tries=3, daily_check=None,result_check=True)
                mission_name='decorator_loop_false'
                @ML.decorator_p_loop(p_mission_name=p_mission_name)
                @ML.decorator_loop(mission_name=mission_name)
                def test_func(*args,**kwargs):
                    pass
                
        - support function:
        
            - 1.  update_next_time(self,next_time=None,interval=None):
                
                support functions for compare now and next_time, update the next_time
                :return: next_time

            - 2. time_sleep(self,next_time=None):
            
                support functions for time sleep
                :return: None

            - 3. init_mail(self,mail_config=None,receivers=None,not_mail=None)
            
                set _send_mail function: send_mail(subject=subject,content=content,attachments=attachments)
                return: None
                
    """
    
    def __init__(self,exception_warning=None):
        """
        init the class and init the MissionRecord decorator
        :param exception_warning: True for print exception
        """ 
        self._timefmt = '%Y-%m-%d %H:%M:%S'
        self.MR = MissionRecord.MissionRecord(exception_warning=exception_warning)
        self.set_loop()
        self.init_mail()
        self.loop_dict = self.get_loop_dict() 
        self.msg_flag = True
        self.min_time_sleep = 5
        self.period_dict = {'m':relativedelta(months=1),
                            'w':datetime.timedelta(days=7),
                            'd':datetime.timedelta(days=1),
                            'hh':datetime.timedelta(hours=1),
                            'mm':datetime.timedelta(minutes=1),
                            'ss':datetime.timedelta(seconds=10),} # for test
    
    # decorator_loop
    
    def decorator_loop(self,mission_name=None):
        """
        decorator function, record as mission_name in db, repeat max_tries if False 
        :param mission_name: mission_name
        :return: True if success and finished
        """
        def decorator_func(func):
            nonlocal mission_name # nonlocal because of decorator 
            if not mission_name:
                mission_name = func.__name__
            # if daily_check and True
            if self.daily_check and self.MR.check_mission_success(mission_name=mission_name) > 0:
                self.send_loop_mail(loop_dict='already',mission_name=mission_name)
                @wraps(func)
                def wrapper(*args, **kwargs):
                    return True # not execute and return True
            else:
                @self.MR.decorator_mission_record(mission_name=mission_name) # if return then record
                @wraps(func)
                def wrapper(*args, **kwargs):
                    # get func's return
                    next_time = datetime.datetime.now()
                    while True:
                        now = datetime.datetime.now()
                        if now > next_time: # repeat when now > next_time
                            print(f'Mission loop left tries: {self.max_tries}')
                            result = func(*args, **kwargs)
                            # run success
                            if result == self.result_check:
                                self.send_loop_mail(loop_dict='success',mission_name=mission_name)
                                return True
                            # run failure
                            else:
                                next_time = self.update_next_time(next_time) # Get next iteration time
                                if self.msg_flag: # only send fail email one time
                                    self.send_loop_mail(loop_dict='fail',mission_name=mission_name,next_time=next_time)
                                    self.msg_flag = False
                            self.max_tries -= 1    
                            # return False beyond max_tries
                            if self.max_tries <= 0:
                                self.send_loop_mail(loop_dict='max_tries',mission_name=mission_name)
                                return False
                            # time_sleep
                            self.time_sleep(next_time=next_time)
            return wrapper            
        return decorator_func
    
    def set_loop(self,days=0,hours=0,minutes=0,seconds=0,max_tries=0,daily_check=True,result_check=True):
        """
        set loop
        :param days: days
        :param hours: hours
        :param minutes: minutes
        :param seconds: seconds
        :param max_tries: return False if tries greater than max_tries
        :param daily_check: True to check the record, if already run then return True and not repeat
        :param result_check: if result of func is result_check set status to True
        :return: None
        """
        self.interval = datetime.timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)
        if not self.interval:
            self.interval = datetime.timedelta(minutes=15)
        self.max_tries = self.p_max_tries = max_tries if max_tries else 999
        self.daily_check = daily_check
        self.result_check = result_check
        
    def get_loop_dict(self):
        """
        set message format
        """
        subject = 'Subject: Mission Loop Msg of {mission_name}: {subject} at {now}'
        content = 'Content: Mission {mission_name} {content}'
        content_next = 'Content: Mission {mission_name} {content} at {next_time}'
        reason = 'Reason: {reason}'
        loop_dict = {
            'already': {
                'subject': subject.format(subject='Already Run!',mission_name='{mission_name}',now='{now}'),
                'content': content.format(content='will not run',mission_name='{mission_name}'),
                'reason': reason.format(reason='already successed in past'),
            },
            'success':{
                'subject': subject.format(subject='Success!'*3,mission_name='{mission_name}',now='{now}'),
                'content': content.format(content='will not run',mission_name='{mission_name}'),
                'reason': reason.format(reason='success and will not repeat'),
            },
            'fail':{
                'subject': subject.format(subject='Fail!'*3,mission_name='{mission_name}',now='{now}'),
                'content': content_next.format(content='will run',mission_name='{mission_name}',
                                              next_time='{next_time}'),
                'reason': reason.format(reason='fail and will repeat'),
            },
            'max_tries':{
                'subject': subject.format(subject='Reach Max Tries!',mission_name='{mission_name}',now='{now}'),
                'content': content.format(content='will not run',mission_name='{mission_name}'),
                'reason': reason.format(reason='tries exhausted, terminated!'),
            },
        }
        return loop_dict
    
    def send_loop_mail(self,loop_dict=None,mission_name=None,now=None,next_time=None):
        """
        self.msg_partial 
        """
        if not now:
            now = datetime.datetime.now()
        now = datetime.datetime.strftime(now,'%Y-%m-%d %H:%M:%S')
        try:
            if not self._send_mail:
                raise AssertionError
            subject = self.loop_dict[loop_dict]['subject'].format(mission_name=mission_name,now=now)
            if not loop_dict == 'fail':
                content = self.loop_dict[loop_dict]['content'].format(mission_name=mission_name)
            else:
                content = self.loop_dict[loop_dict]['content'].format(mission_name=mission_name,next_time=next_time)
            reason = self.loop_dict[loop_dict]['reason']
            self._send_mail(subject=subject,content=content+'\n'+reason)
        except AssertionError: # for test
            subject = self.loop_dict[loop_dict]['subject'].format(mission_name=mission_name,now=now)
            if not loop_dict == 'fail':
                content = self.loop_dict[loop_dict]['content'].format(mission_name=mission_name)
            else:
                content = self.loop_dict[loop_dict]['content'].format(mission_name=mission_name,next_time=next_time)
            reason = self.loop_dict[loop_dict]['reason']
            print(f'{subject}\n{content}\n{reason}')
            pass # for test
        except Exception as e:
            print(e)
            print('mail not sent!')
        
    # decorator_p_loop    
    
    def decorator_p_loop(self,p_mission_name=None):
        """
        decorator function, loop no matter func success or not  
        :param p_mission_name: p_mission_name
        :return: True if success and finished    
        """
        def decorator_func(func):
            nonlocal p_mission_name # nonlocal because of decorator 
            if not p_mission_name:
                p_mission_name = func.__name__
            @wraps(func)
            def wrapper(*args, **kwargs):
                # must run
                if self.p_must_run:
                    print(f'{p_mission_name} must run start!!!')
                    result = func(*args,**kwargs)
                    if result == self.p_result_check:
                        p_status = True
                    else:
                        p_status = False
                    now = datetime.datetime.now()
                    p_next_time = self.p_start_time
                    self.send_p_mail(p_mission_name=p_mission_name,p_status=p_status,
                                     p_start_time=now,p_next_time=p_next_time,p_must_run=True)
                # not must run
                else:
                    p_next_time = self.p_start_time
                    s_next_time = datetime.datetime.strftime(p_next_time,'%Y-%m-%d %H:%M:%S')
                    while True:
                        now = datetime.datetime.now()
                        if now > p_next_time:
                            print(f'{p_mission_name} start!!!')
                            p_next_time = self.update_next_time(next_time=p_next_time,interval=self.p_period)
                            result = func(*args,**kwargs)
                            if result == self.p_result_check:
                                p_status = True
                            else:
                                p_status = False
                            self.send_p_mail(p_mission_name=p_mission_name,p_status=p_status,
                                             p_start_time=now,p_next_time=p_next_time)
                            self.time_sleep(next_time=p_next_time) 
                            try: 
                                self.max_tries = self.p_max_tries
                            except:
                                pass
                            try: 
                                self.msg_flag = True
                            except:
                                pass
                            continue 
            return wrapper            
        return decorator_func   
    
    def set_p_loop(self,p_period=None,p_start_time=None,p_result_check=True,p_must_run=None):
        """
        set p_loop
        :param p_period: 'm':next month, 'w':1 week, 'd':1 day, 'hh':1 hour, 'mm': 1 minute, 'ss': 10 second for test
        :param p_start_time: daily start time
        :param p_result_check: p_result_check
        :param p_must_run: Ture to run right now
        :return: None
        """     
        self.p_period = self.get_p_period(p_period=p_period)
        self.p_start_time = self.get_p_start_time(p_start_time=p_start_time)
        self.p_result_check = p_result_check            
        self.p_must_run = p_must_run
    
    def send_p_mail(self,p_mission_name=None,p_status=None,p_start_time=None,p_next_time=None,
                    p_must_run=None,print_msg=True):
        """
        send p loop mail
        :param p_mission_name: p_mission_name
        :param p_status: result status, True or False
        :param p_start_time: time of current run
        :param p_next_time: time of next run
        :parma p_must_run: True if must run
        :param print_msg: True to print msg
        :return: None
        """
        try:
            if not self._send_mail:
                raise AssertionError
            s_start_time = datetime.datetime.strftime(p_start_time,'%Y-%m-%d %H:%M:%S')
            s_next_time = datetime.datetime.strftime(p_next_time,'%Y-%m-%d %H:%M:%S')
            if p_status:
                status = 'Success!' * 3
            else:
                status = 'Fail!' * 3
            subject = f'Subject: Mission Period Loop of {p_mission_name}: {status} at {s_start_time}' 
            content = 'Content:\n'
            if p_must_run:
                content += f'{p_mission_name} must run start at {s_start_time}!!!'
            else:
                content += f'{p_mission_name} start at {s_start_time}'
            content += f'\nresult is {p_status}'
            content += f'\n{p_mission_name} will run next time at {s_next_time}!!!\n'
            content += f'==' * 40
            self._send_mail(subject=subject,content=content)
            if print_msg:
                print(subject + '\n' + content)
        except Exception as e:
            print(e)
            print('mail not sent!')
    
    def get_p_period(self,p_period=None):
        """
        get p_period
        :param p_period: 'm':next month, 'w':1 week, 'd':1 day, 'hh':1 hour, 'mm': 1 minute, 'ss': 10 second for test
        :return: datetime       
        """
        try:
            return self.period_dict.get(p_period.lower(),self.period_dict.get('d'))
        except:
            return self.period_dict.get('d')
        
    def get_p_start_time(self,p_start_time=None):
        """
        get p_start_time
        :param p_start_time: '%H:%M:%S'
        :return: datetime       
        """
        if not p_start_time:
            p_start_time = '08:00:00'
        start = datetime.datetime.strptime(p_start_time,'%H:%M:%S')
        today = datetime.datetime.today()
        start = datetime.datetime(year=today.year,month=today.month,day=today.day,
                                  hour=start.hour,minute=start.minute,second=start.second)
        if start < datetime.datetime.now():
            start += datetime.timedelta(days=1)
        return start
    
    # support tools
    
    def update_next_time(self,next_time=None,interval=None):
        """
        support functions for compare now and next_time, update the next_time
        :param next_time: next_time
        :param interval: interval from loop or p_period from p_loop
        :return: next_time
        """
        now = datetime.datetime.now()
        if not interval:
            interval = self.interval
        while now > next_time:
            next_time += interval
        return next_time
    
    def time_sleep(self,next_time=None):
        """
        support functions for time sleep
        :param next_time: next_time
        :return: None
        """
        _ = next_time - datetime.datetime.now()
        if _.days >=0:
            time_sleep = (next_time - datetime.datetime.now()).seconds
        else:
            time_sleep = self.min_time_sleep
        if time_sleep > self.min_time_sleep:
            time.sleep(time_sleep-self.min_time_sleep)
        else:
            time.sleep(time_sleep)
        
    def init_mail(self,mail_config=None,receivers=None,not_mail=None):
        """
        set _send_mail function: send_mail(subject=subject,content=content,attachments=attachments)
        :param mail_config: {'host': '', 'account': '', 'password': '', 'encoding': ''}
        :param receivers: account from mail_config if None 
        :param not_mail: None for test and not send mail
        return: None
        """
        try:
            if not_mail: # for test
                raise AssertionError 
            if not mail_config:
                mail_config = SendMail_config.mailQQ
            mail = SendMail.SendMail(**mail_config)
            self._send_mail = partial(mail.send_mail,receivers=receivers)
        except:
            self._send_mail = None
    


# In[14]:


if __name__ == '__main__':
    
    ML = MissionLoop()
    # Test daily_run None and repeat is True
    print('=='*40)
    print('test for daily_check None!')
    ML.set_loop(seconds=3, max_tries=3, daily_check=None,result_check=True)
    @ML.decorator_loop(mission_name='MissionAutorunTestDailyCheckNone')
    def test_func(*args,**kwargs):
        return True
    test_func('hello',world='world')
    
    # Test daily_run True or None
    print('=='*40)
    print('test for daily_check is True!')
    ML.set_loop(seconds=3, max_tries=3,daily_check=True,result_check=True)
    @ML.decorator_loop(mission_name='MissionAutorunTestDailyCheckTrue')
    def test_func(*args,**kwargs):
        return False
    test_func('hello',world='world')
    
    print('=='*40)
    print('test for daily_check is None, Random Result!')
    ML.set_loop(seconds=3, max_tries=3,daily_check=None,result_check=True)
    @ML.decorator_loop(mission_name=None)
    def test_func_random(*args,**kwargs):
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    test_func_random('hello',world='world')
    
# if __name__ == '__main__':   
#     清除记录
#     MR.clean_all_records()
    
#     查询所欲记录
#     from mytools_mission import MissionRecord
#     MR = MissionRecord.MissionRecord()
#     df = MR.summary_mission_record(status=None)
#     print(df)


# In[ ]:


if __name__ == '__main__':
    
    # Test for decorator_p_loop
    print('=='*40)
    print('Test for decorator_p_loop!')
    ML = MissionLoop()
    p_mission_name = 'my p loop test'
    p_period = 'ss' # for test 10 seconds
    p_start_time = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(seconds=5),'%H:%M:%S')
    p_result_check=True
    p_must_run=True
    ML.set_p_loop(p_period=p_period,p_start_time=p_start_time,p_result_check=True,p_must_run=None)
    print(f'p_mission_name: {p_mission_name}')
    print(f'ML.p_start_time: {ML.p_start_time}')
    print(f'ML.p_start_time: {ML.p_start_time}')
    print(f'ML.p_period: {ML.p_period}')
    print(f'ML.p_must_run: {ML.p_must_run}')
    print(f'=='*40)

    @ML.decorator_p_loop(p_mission_name=p_mission_name)
    def test_p_func_random(*args,**kwargs):
        return False
        from random import randint
        data = randint(1,10)
        if data % 2: 
            return True
        else:
            return False
    test_p_func_random('hello',world='world')


# In[ ]:


if __name__ == '__main__':
    
    # Test for decorator_p_loop with decorator_loop
    print('=='*40)
    print('Test for decorator_p_loop with decorator_loop!')
    ML = MissionLoop()
    p_mission_name = 'decorator_p_loop'
    p_period = 'ss' # for test 10 seconds
    p_start_time = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(seconds=5),'%H:%M:%S')
    p_result_check=True
    p_must_run=True
    ML.set_p_loop(p_period=p_period,p_start_time=p_start_time,p_result_check=True,p_must_run=None)
    print(f'p_mission_name: {p_mission_name}')
    print(f'ML.p_start_time: {ML.p_start_time}')
    print(f'ML.p_start_time: {ML.p_start_time}')
    print(f'ML.p_period: {ML.p_period}')
    print(f'ML.p_must_run: {ML.p_must_run}')
    print(f'=='*40)

    ML.set_loop(seconds=5, max_tries=3, daily_check=None,result_check=True)
    mission_name='decorator_loop_false'
    @ML.decorator_p_loop(p_mission_name=p_mission_name)
    @ML.decorator_loop(mission_name=mission_name)
    def test_func(*args,**kwargs):
        return False
    test_func('hello','world')

