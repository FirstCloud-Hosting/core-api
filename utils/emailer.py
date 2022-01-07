import os
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate
from string import Template


class emailer():

    def __init__(self, server_host, server_port, username, password, tls=False, app_url="linufy.app"):
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.password = password
        self.tls = tls
        self.app_url = app_url

    def connect(self):
        self.connection = smtplib.SMTP(host=str(self.server_host), port=int(self.server_port))
        if self.tls.lower() == "true":
            self.connection.starttls()
        self.connection.ehlo()
        self.connection.login(str(self.username), str(self.password))

    def disconnect(self):
        self.connection.quit()

    def read_template(self, filename):
        """
        Returns a Template object comprising the contents of the
        file specified by filename.
        """
        with io.open('%s/../files/email/%s.html' % (os.path.split(__file__)[0], filename), 'r', encoding="utf-8") as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    def sendLostPassword(self, src_address, dst_address, title, lostPasswordKey):
        msg = MIMEMultipart()
        msg['From'] = src_address
        msg['To'] = dst_address
        msg['Subject'] = title
        msg['Date'] = formatdate(localtime=1)
        msg['Message-ID'] = make_msgid()
        message_template = self.read_template('lostPassword')
        message = message_template.substitute(TITLE=title, KEY=lostPasswordKey, APP_URL=self.app_url)
        msg.attach(MIMEText(message, 'html', "utf-8"))
        plain = """Hello,

        You have requested a new password for your LinuFy account. Please use the following link to https://%s/lostpassword?key=%s.
        If you did not request this password change please feel free to ignore it. Only a person with access to your email can reset your account password.
        If you have any questions, please don't hesitate to reach use a support@linufy.app
        Please do not reply to this email.
        Sincerly,
        The FirstCloud-Hosting Team
        """ % (self.app_url, lostPasswordKey)
        msg.attach(MIMEText(plain, 'plain'))
        message = msg.as_string()
        self.connect()
        self.connection.sendmail(src_address, dst_address, message)
        self.disconnect()
        del msg

    def sendConfirmSignUp(self, src_address, dst_address, title, confirmationKey):
        msg = MIMEMultipart()
        msg['From'] = src_address
        msg['To'] = dst_address
        msg['Subject'] = title
        msg['Date'] = formatdate(localtime=1)
        msg['Message-ID'] = make_msgid()
        message_template = self.read_template('confirmSignUp')
        message = message_template.substitute(TITLE=title, EMAIL=dst_address, KEY=confirmationKey, APP_URL=self.app_url)
        msg.attach(MIMEText(message, 'html', "utf-8"))
        plain = """Hello,

        Please confirm your email address by clicking the link below. We may need to send you critical information about our service and it is important that we have an accurate email address. Please use the following link to https://%s/confirm?email=%s&key=%s.
        If you have any questions, please don't hesitate to reach use a support@linufy.app
        Please do not reply to this email.
        Sincerly,
        The FirstCloud-Hosting Team
        """ % (self.app_url, dst_address, confirmationKey)
        msg.attach(MIMEText(plain, 'plain'))
        message = msg.as_string()
        self.connect()
        self.connection.sendmail(src_address, dst_address, message)
        self.disconnect()
        del msg

    def sendNewPassword(self, src_address, dst_address, title, username, newPassword):
        msg = MIMEMultipart()
        msg['From'] = src_address
        msg['To'] = dst_address
        msg['Subject'] = title
        msg['Date'] = formatdate(localtime=1)
        msg['Message-ID'] = make_msgid()
        message_template = self.read_template('newPassword')
        message = message_template.substitute(TITLE=title, USERNAME=username, EMAIL=dst_address, PASSWORD=newPassword, APP_URL=self.app_url)
        msg.attach(MIMEText(message, 'html', "utf-8"))
        plain = """Dear %s,

        You have requested a new password for your LinuFy account. Please use the new password %s
        If you have any questions, please don't hesitate to reach use a support@linufy.app
        Please do not reply to this email.
        Sincerly,
        The FirstCloud-Hosting Team
        """ % (username, newPassword)
        msg.attach(MIMEText(plain, 'plain'))
        message = msg.as_string()
        self.connect()
        self.connection.sendmail(src_address, dst_address, message)
        self.disconnect()
        del msg

    def sendWebinarSignUp(self, src_address, dst_address, title, firstname, link, date, time):
        msg = MIMEMultipart()
        msg['From'] = src_address
        msg['To'] = dst_address
        msg['Subject'] = title
        msg['Date'] = formatdate(localtime=1)
        msg['Message-ID'] = make_msgid()
        message_template = self.read_template('webinarSignUp')
        message = message_template.substitute(TITLE=title, FIRSTNAME=firstname, EMAIL=dst_address, LINK=link, DATE=date, TIME=time)
        plain = """Dear %s,

        You want to register to our webinar for LinuFy. Please use this link : %s the %s at %s
        If you have any questions, please don't hesitate to reach use a support@linufy.app
        Please do not reply to this email.
        Sincerly,
        The FirstCloud-Hosting Team
        """ % (firstname, link, date, time)
        msg.attach(MIMEText(plain, 'plain'))
        message = msg.as_string()
        self.connect()
        self.connection.sendmail(src_address, dst_address, message)
        self.disconnect()
        del msg
