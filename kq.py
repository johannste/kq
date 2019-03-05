from selenium import webdriver
from PIL import Image
from pytesseract import image_to_string
from flask import Flask
from flask_mail import Mail, Message
import os
import datetime
import sys

app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'Enter your mail server here',
    "MAIL_PORT": 25,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": 'Enter your email here',
    "MAIL_PASSWORD": 'Enter your email\'s password here'
}
app.config.update(mail_settings)
mail = Mail(app)

now = datetime.datetime.now()


def get_user_and_pass():
    global user
    global pwd
    user = 'Enter your username here'
    pwd = 'Enter your password here'


def binarization(image, threshold):
    image = image.convert('L')
    table = []
    for i in range(256):
        if i > threshold:
            table.append(0)
        else:
            table.append(1)
    return image.point(table, '1')


def kq_success():
    with app.app_context():
        msg = Message('考勤正常', sender='Sender\'s email here', recipients=['Receiver\'s email here'])
        msg.html = '<div>' \
                   '<h1>' + str(now)[0:19] + '</h1>' \
                                             '<h1>Succeed</h1>' \
                                             '<div>' \
                                             '<p>Congratulation!</p>' \
                                             '</div>' \
                                             '</div>'
        mail.send(msg)


def kq_failed():
    with app.app_context():
        msg = Message('考勤异常', sender='Sender\'s email here', recipients=['Receiver\'s email here'])
        msg.html = '<div>' \
                   '<h1>Failed</h1>' \
                   '<div>' \
                   '<p>You must recheck it!</p>' \
                   '</div>' \
                   '</div>'
        mail.send(msg)


def do_kq():
    url = 'kq url here'
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        driver.get(url)
    except Exception as e:
        kq_failed()
        print(e)
        driver.close()
        sys.exit()

    text_field = driver.find_elements_by_class_name('textfield')
    text_field[0].send_keys(user)
    text_field[1].send_keys(pwd)

    driver.save_screenshot('login.png')
    image = Image.open('login.png')

    # 1600x900
    frame = image.crop((905, 350, 965, 373))
    frame.save('code.png')
    image = Image.open('code.png')

    code = image_to_string(binarization(image, threshold=127))
    driver.find_element_by_class_name('a').send_keys(code)

    os.remove('login.png')
    os.remove('code.png')

    try:
        driver.find_element_by_id('loginButton').click()
        driver.find_element_by_class_name('mr36').click()
        kq_success()
    except Exception as e:
        kq_failed()
        print(e)
        driver.close()
        sys.exit()

    driver.close()
    driver.quit()


def main():
    get_user_and_pass()

    do_kq()


if __name__ == '__main__':
    main()
