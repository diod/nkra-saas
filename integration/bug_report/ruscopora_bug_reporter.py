import urllib

from datetime import datetime
from smtplib import SMTP
from email.MIMEText import MIMEText

_has_fcntl = True
try:
    import fcntl
except ImportError:
    _has_fcntl = False


logFilePath = "./bug-reporter.log" #"/place/ruscorpora/logs/bug-reporter.log"
emailAddress = "ruscorpora-bugs@yandex.ru"
login = "ruscorpora-bugs@yandex.ru"      
password = "ruscorpora"


class Locker:
    def lock(self, path, mode):
        if _has_fcntl:
            self.__LockFile = file(path, mode)
            if mode == "w" or mode == "a":
                lockmode = fcntl.LOCK_EX
            else:
                lockmode = fcntl.LOCK_SH
            fcntl.lockf(self.__LockFile.fileno(), lockmode)
        else:
            self.__LockFile = open(path, mode)

    def write(self, text):
        self.__LockFile.write(text)

    def unLock(self):
        if _has_fcntl:
            fcntl.lockf(self.__LockFile.fileno(), fcntl.LOCK_UN)
        self.__LockFile.close()
        self.__LockFile = None


def mail(to, subject, text):
   msg = MIMEText(text)
   msg['From'] = login
   msg['To'] = to
   msg['Subject'] = subject
   mailServer = SMTP("smtp.yandex.ru", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(login, password)
   mailServer.sendmail(login, to, msg.as_string())
   mailServer.close()


def process_bug_report(msg, url):
    msg_line = msg.replace("\n", " // ")
    tm = datetime.today()

    text = str(tm) + "\t" + url + "\t" + msg_line + "\n"
    log = Locker()
    log.lock(logFilePath, 'a')
    log.write(text)
    log.unLock()

    subject = "Bug report"
    mailtext = urllib.unquote(msg) + '\n\n' + url
    mail (emailAddress, subject, mailtext)
