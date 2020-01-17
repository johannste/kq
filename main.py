import os
import sys
from _datetime import datetime

import cv2
import yaml
from PIL import Image
from flask import Flask
from flask_mail import Mail, Message
from pytesseract import image_to_string
from selenium import webdriver

app = Flask(__name__)
path = sys.path[0]
with open(path + '/setting.yml', encoding='utf-8') as f:
    setting = yaml.load(f, yaml.FullLoader)
    Driver = setting['driver']
    MAIL_SERVER = setting['mail']['mail_server']
    MAIL_PORT = setting['mail']['mail_port']
    MAIL_USE_TLS = setting['mail']['mail_use_tls']
    MAIL_USE_SSL = setting['mail']['mail_use_ssl']
    MAIL_USERNAME = setting['mail']['mail_username']
    MAIL_PASSWORD = setting['mail']['mail_password']
    SENDER = setting['mail']['sender']
    RECIPIENTS = setting['mail']['recipients']
    Frame = setting['frame']
    URL = setting['url']
    USERNAME = setting['user']['username']
    PASSWORD = setting['user']['password']

mail_settings = {
    "MAIL_SERVER": MAIL_SERVER,
    "MAIL_PORT": MAIL_PORT,
    "MAIL_USE_TLS": MAIL_USE_TLS,
    "MAIL_USE_SSL": MAIL_USE_SSL,
    "MAIL_USERNAME": MAIL_USERNAME,
    "MAIL_PASSWORD": MAIL_PASSWORD
}
app.config.update(mail_settings)
mail = Mail(app)


def get_driver():
    if Driver == 'chrome':
        return webdriver.Chrome()
    elif Driver == 'firefox':
        return webdriver.Firefox()


driver = get_driver()


def kq_success():
    with app.app_context():
        msg = Message('考勤正常', sender=SENDER, recipients=[RECIPIENTS])
        msg.html = '''
        <div>
            <h1 style='color:green'>''' + str(datetime.now())[0:19] + '''</h1>
            <h1 style='color:green'>Succeed</h1>
            <div>
                <p>Congratulations!</p>
            </div>
        </div>'''
        mail.send(msg)


def kq_failed(e):
    with app.app_context():
        msg = Message('考勤异常', sender=SENDER, recipients=[RECIPIENTS])
        msg.html = '''
        <div>
            <h1 style='color:red'>Failed</h1>
            <div>
                <p>You must recheck it!</p>
            </div>
            <h1 style='color:red'>''' + repr(e) + '''</h1>
        </div>'''
        mail.send(msg)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def get_code():
    driver.save_screenshot('login.png')
    image = Image.open('login.png')

    frame = image.crop(Frame)
    frame.save('code.png')

    image = cv2.imread('code.png', 0)
    tmp = Image.fromarray(cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)[1])
    code = image_to_string(tmp)

    if not (is_number(code) and len(code) == 4):
        driver.find_element_by_id('imgRandom').click()
        return get_code()
    driver.find_element_by_class_name('a').send_keys(code)

    os.remove('login.png')
    os.remove('code.png')


def do_kq():
    driver.maximize_window()
    driver.get(URL)

    text_field = driver.find_elements_by_class_name('textfield')
    text_field[0].send_keys(USERNAME)
    text_field[1].send_keys(PASSWORD)

    get_code()

    try:
        driver.find_element_by_id('loginButton').click()
        driver.find_element_by_class_name('mr36').click()
        kq_success()
    except Exception as e:
        kq_failed(e)
    finally:
        driver.close()
        driver.quit()
        sys.exit()


if __name__ == '__main__':
    do_kq()
