from ast import main
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

def send_email(mail, subject, content):
    # 配置邮件服务器
    smtp_server = "smtp.sina.com"  # 根据实际使用的邮件服务器修改
    # TODO 如果使用qq邮箱，将会有不可预期的异常：(-1, b'\x00\x00\x00') 即使发送成功也是会有异常发生，不想处理，暂时用新浪邮箱来承载，要开通独立验证码的形态，不是设置邮箱密码
    # smtp_server = "smtp.qq.com"
    smtp_port = 587
    # 从当前的.env文件中获取邮件sender和密码
    sender_email = os.getenv("EMAIL_SENDER")
    logger.info(sender_email)
    # sender_password = "jwvfkpttebjpbiif" # 邮箱应用密码
    sender_password = os.getenv("EMAIL_PASSWORD")
    logger.info(sender_password)
    
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = mail
    msg['Subject'] = f'DT: - {subject}'
    
    # 添加邮件正文
    body = f"DT: {content} 祝好！"
    msg.attach(MIMEText(body, 'plain'))
    
    # 连接到SMTP服务器并发送邮件
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        logger.info(f"邮件已发送至 {mail}，主题：{subject}")
        
if __name__ == "__main__":
    send_email("alphachenx@sina.com", "测试", "这是一封测试邮件")
