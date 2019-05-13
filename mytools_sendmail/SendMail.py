
# coding: utf-8

# # SendMail
# 
# [参考1_python3：利用SMTP协议发送QQ邮件+附件](https://www.cnblogs.com/shapeL/p/9115887.html)
# 
# [参考2_利用Python+163邮箱授权码发送带附件的邮件](http://www.cnblogs.com/zhongfengshan/p/9769072.html)

# In[1]:


"""
send mail
- tool_name: SendMail
- version: 0.0.1
- update date: 2018-11-13
- import: from mytools_sendmail import SendMail
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# In[4]:


class SendMail():
    """
    send mail
    - tool_name: SendMail
    - version: 0.0.1
    - update date: 2018-11-13
    - import: from mytools_sendmail import SendMail
    - function:
    
        1. __init__
        
            init mail setting with host,account,password,encoding
        
        2. send_mail(self,receivers=None,subject=None,content=None,attachments=None)

            send mail to receivers
            :return: True if success, False if exception occurs
            
    """
    def __init__(self,host=None,account=None,password=None,encoding=None):
        """
        init mail setting with host,account,password,encoding
        :param host: hostname
        :param account: account
        :param password: password
        :param encoding: encoding
        """
        self.host = host
        self.account = account
        self.password = password
        self.encoding = encoding

    def send_mail(self,receivers=None,subject=None,content=None,attachments=None):
        """
        send mail to receivers
        :param receivers: receiver in list
        :param subject: mail subject
        :param content: mail content
        :param attachments: attachment list
        :return: True if success, False if exception occurs
        """
        # mail subject
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = self.account
        if not receivers:
            receivers = [self.account]
        message['To'] = ';'.join(receivers)
        
        # mail content
        if content:
            message.attach(MIMEText(content, 'plain', self.encoding)) 

        # mail attachment
        if attachments:
            for attachment in attachments:
                if os.path.exists(attachment):
                    att = MIMEText(open(attachment, 'rb').read(), 'base64', self.encoding)
                    att['Content-Type'] = 'application/octet-stream'
                    att.add_header('Content-Disposition','attachment',filename=(self.encoding,'',
                                                                                os.path.basename(attachment)))
                    message.attach(att)
        
        # send mail
        try:
            server = smtplib.SMTP_SSL(self.host,465) # 启用SSL发信, 端口一般是465
            #server.set_debuglevel(1)# 打印出和SMTP服务器交互的所有信息
            server.login(self.account,self.password)
            server.sendmail(self.account,receivers,message.as_string())
            server.close()
            print(f'{self.account} sent mail to {", ".join(map(str,receivers))}!')
            return True
        except smtplib.SMTPException as e:
            print(e)
            return False


# In[5]:


if __name__ == '__main__':
    from mytools_sendmail import SendMail_config
    mailQQ = SendMail_config.mailQQ
    SM = SendMail(**mailQQ)
    subject = 'SendMail Test Title'
    content = 'SendMail Test Content'
    attachments = [r'./testfiles/text.txt',r'./testfiles/中文.xlsx']
    SM.send_mail(subject=subject,content=content,attachments=attachments)

