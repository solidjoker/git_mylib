
# coding: utf-8

# # AiohttpFrame_Login

# In[1]:


"""
support tools for aiohttpframe, see the docs in the Class AiohttpFrame_Login for detail
    - tool_name: AiohttpFrame_Login
    - version: 0.0.2
    - update date: 2019-05-15
    - import: from mytools_aiohttpframe import AiohttpFrame_Login
"""

import time

from mytools_aiohttpframe.AiohttpFrame_Browser import AiohttpFrame_Browser


# In[ ]:


class AiohttpFrame_Login(AiohttpFrame_Browser):
    """
    support tools for aiohttpframe, see the docs in the Class AiohttpFrame_Login for detail
        - tool_name: AiohttpFrame_Login
        - version: 0.0.2
        - update date: 2019-05-15
        - import: from mytools_aiohttpframe import AiohttpFrame_Login
        - need inherit class and delegate the method, example:
            --------------------------------------------------------------------
            print('Test for inherit the class AiohttpFrame_Login to login baidu')
            print('='*40)
            class BaiduLogin(AiohttpFrame_Login):
                def __init__(self):
                    super(BaiduLogin,self).__init__()
                    self.check_login_url = 'https://passport.baidu.com/center'


                def delegate_check_login_status(self,result=None):
                    if '登录历史' in result.content.decode('utf-8'):
                        return True

                def delegate_mannual_login(self):
                    print('mannul login')
                    url = 'https://passport.baidu.com/center'
                    while not self.browser.current_url == url: # self.browser inherit from parent class
                        print(self.browser.current_url)
                        time.sleep(5)
                    return True

            baidulogin = BaiduLogin()
            baidulogin.al_keep_login(check_login_url=baidulogin.check_login_url,
                                     mannual_login_url=baidulogin.check_login_url)
                                     
            --------------------------------------------------------------------            
    
    """
    
    def __init__(self,chrome_path=None,cookies_jsonfile=None,headers=None):  
        """
        init the class and get the setting of chrome browser
        :param chrome_path: chrome_path, or AiohttpFrame_Config.chrome_path if None
        :param cookies_jsonfile: cookies_jsonfile, or AiohttpFrame_Config.cookies_jsonfile if None
        :param headers: headers, or AiohttpFrame_Config.headers if None        
        """   
        super(AiohttpFrame_Login,self).__init__(chrome_path=headers,
                                                cookies_jsonfile=cookies_jsonfile,
                                                headers=headers)
    
    def al_keep_login(self,check_login_url=None,mannual_login_url=None):
        """
        keep the login status 
        :param check_login_url: check_login_url for check the login status
        :param mannual_login_url: mannual_login_url to login
        :return: True
        """   
        while not self.al_check_login_status(check_login_url):
            if self.al_mannual_login(mannual_login_url):
                print(f'mannual login successfully!')
                break
        print(f'logged in and {self.cookies_jsonfile} is availabe!')
        return True
    
    def al_check_login_status(self,check_login_url=None):
        """
        check the login status 
        :param check_login_url: check_login_url for check the login status
        :return: True
        need rewrite the delegate_check_login_status
        """   
        result = self.ab_get_session_data_with_cookies(check_login_url)
        if self.delegate_check_login_status(result=result):
            return True
        
    def al_mannual_login(self,mannual_login_url=None):
        """
        mannual_login
        :param mannual_login_url: mannual_login_url to login
        :return: True
        need rewrite the delegate_check_login_status
        """   
        self.ab_init_chrome_browser()
        self.browser.get(mannual_login_url)
        if self.delegate_mannual_login():
            self.ab_dump_cookies()
            self.ab_close_browser()
            return True
    
    def delegate_check_login_status(self,result=None):
        raise NotImplementedError
    
    def delegate_mannual_login(self):
        raise NotImplementedError


# In[ ]:


if __name__ == '__main__':
    print('Test for inherit the class AiohttpFrame_Login to login baidu')
    print('='*40)
    class BaiduLogin(AiohttpFrame_Login):
        def __init__(self):
            super(BaiduLogin,self).__init__()
            self.check_login_url = 'https://passport.baidu.com/center'
        
        
        def delegate_check_login_status(self,result=None):
            if '登录历史' in result.content.decode('utf-8'):
                return True
            
        def delegate_mannual_login(self):
            print('mannul login')
            url = 'https://passport.baidu.com/center'
            while not self.browser.current_url == url: # self.browser inherit from parent class
                print(self.browser.current_url)
                time.sleep(5)
            return True

    baidulogin = BaiduLogin()
    baidulogin.al_keep_login(check_login_url=baidulogin.check_login_url,
                             mannual_login_url=baidulogin.check_login_url)

