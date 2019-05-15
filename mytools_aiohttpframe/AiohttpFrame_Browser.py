
# coding: utf-8

# # AiohttpFrame_Browser

# In[1]:


"""
support tools for aiohttpframe, see the docs in the Class AiohttpFrame_Browser for detail
    - tool_name: AiohttpFrame_Browser
    - version: 0.0.2
    - update date: 2019-05-15
    - import: from mytools_aiohttpframe import AiohttpFrame_Browser
"""

import os
import json
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from mytools_aiohttpframe import AiohttpFrame_Config


# In[2]:


class AiohttpFrame_Browser:
    """
    support tools for aiohttpframe, see the docs in the Class AiohttpFrame_Browser for detail
        - tool_name: AiohttpFrame_Browser
        - version: 0.0.2
        - update date: 2019-05-15
        - import: from mytools_aiohttpframe import AiohttpFrame_Browser
    """

    def __init__(self, chrome_path=None,cookies_jsonfile=None,headers=None):
        """
        init the class and get the setting of chrome browser
        :param chrome_path: chrome_path, or AiohttpFrame_Config.chrome_path if None
        :param cookies_jsonfile: cookies_jsonfile, or AiohttpFrame_Config.cookies_jsonfile if None
        :param headers: headers, or AiohttpFrame_Config.headers if None        
        """    
        if not chrome_path:
            chrome_path = AiohttpFrame_Config.chrome_path
        self.chrome_path = chrome_path
        if not cookies_jsonfile:
            cookies_jsonfile = AiohttpFrame_Config.cookies_jsonfile
        self.cookies_jsonfile = cookies_jsonfile
        if not headers:
            headers = AiohttpFrame_Config.headers
        self.headers = headers
        if not os.path.exists(self.cookies_jsonfile):
            json.dump({},open(self.cookies_jsonfile,'w'))
            
    def ab_init_chrome_browser(self):
        """
        init the chrome browser    
        """            
        executable_path = self.chrome_path
        options = self.ab_set_chrome_options()
        # get the log of the browser
        desired = DesiredCapabilities.CHROME
        desired['loggingPrefs'] = {'performance':'ALL'}
        self.browser = webdriver.Chrome(executable_path=executable_path,
                                        options=options,
                                        desired_capabilities=desired)
        #  wait 1 second
        self.browser.implicitly_wait(1)
    
    def ab_set_chrome_options(self):
        """
        set the chrome browser    
        """  
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')    
        #options.add_argument('--window-position=0,0')
        options.add_argument('--start-maximized')
        options.add_argument('--force-device-scale-factor=1')
        prefs = {'profile.default_content_setting_values':{'notifications':2}}
        options.add_experimental_option('prefs',prefs)
        return options
    
    def ab_get_session_data_with_cookies(self,url=None):
        """
        get session url with cookies
        :url: param chrome_path: chrome_path, or AiohttpFrame_Config.chrome_path if None
        :return: content of the url        
        """           
        if url:
            session = requests.Session()
            cookies = self.ab_load_cookies()
            session.cookies.update(cookies)
            result = session.get(url,headers=self.headers)
            return result
    
    def ab_dump_cookies(self):
        """
        save the cookies as json into self.cookies_jsonfile      
        """  
        cookies = self.browser.get_cookies()
        cookies = {item['name']:item['value'] for item in cookies}
        json.dump(cookies,open(self.cookies_jsonfile,'w'))
    
    def ab_load_cookies(self):
        """
        load the cookies as json from self.cookies_jsonfile      
        """  
        try:
            cookies = json.load(open(self.cookies_jsonfile))
            return cookies
        except:
            traceback.print_exc()
        
    def ab_close_browser(self):
        """
        close the browser
        """  
        try:
            self.browser.quit()
            return True
        except:
            traceback.print_exc()
            return False


# In[3]:


if __name__ == '__main__':
    url = 'https://www.baidu.com'
    mybrowser = AiohttpFrame_Browser()
    mybrowser.ab_init_chrome_browser() # 打开selenium浏览器
    mybrowser.browser.get(url=url)
    mybrowser.ab_dump_cookies()
    print(mybrowser.ab_load_cookies())
    mybrowser.ab_close_browser()

