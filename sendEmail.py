import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

def qqEmail(infor):

    sender = '1371578298@qq.com'
    passWord = 'dmcxqularzjlgbei'
    mail_host = 'smtp.qq.com'

    receivers = ['cleroman@163.com']


    msg = MIMEMultipart()

    msg['Subject'] = 'huobi'

    msg['From'] = sender

    msg_content = infor
    msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))


    try:

        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.set_debuglevel(1)
        s.login(sender,passWord)

        for item in receivers:
            msg['To'] = to = item
            s.sendmail(sender,to,msg.as_string())
            # print('Success!')
        s.quit()
        # print ("All emails have been sent over!")
    except smtplib.SMTPException as e:
        print ("Falied,%s",e)