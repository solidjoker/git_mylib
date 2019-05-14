
# coding: utf-8

# In[1]:


import logging
from logging import handlers


# In[4]:


class MyLog():
    def __init__(self,filename=None,level=None,when=None,backCount=None,fmt=None):
        
        self.level_relations = {
            'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'crit':logging.CRITICAL
        }
        if not filename:
            filename = 'MyLog.log'
        if not level:
            level = 'info'
        if not when:
            when = 'D'
        if not backCount:
            backCount = 3
        if not fmt:
            fmt = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
        
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        self.sh = logging.StreamHandler()#往屏幕上输出
        self.sh.setFormatter(format_str) #设置屏幕上显示的格式
        self.th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')
        #往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        self.th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(self.sh) #把对象加到logger里
        self.logger.addHandler(self.th)
        
    def shutdown(self):
        while len(self.logger.handlers):
            self.logger.removeHandler(self.logger.handlers[0])
        logging.shutdown()


# In[6]:


if __name__ == '__main__':
    log = MyLog(level='warning')
    log.logger.debug('debug')
    log.logger.info('info')
    log.logger.warning('warning')
    log.logger.error('error')
    log.logger.critical('critical')
    log.shutdown()    

