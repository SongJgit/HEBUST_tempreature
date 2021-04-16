from selenium import webdriver
from time import sleep
import time
import random
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import parser
import poplib


# 邮件发送
def send_MAIL(title, send_msg, receiver):
    """
    :param send_msg: 所要发送的内容
    :param title: 发送的标题
    :param receiver: 收件人
    :return:
    """
    # 发件人地址及密码
    send_address = "312091156@qq.com"  # 你的邮箱
    send_pwd = "rukfwyvtueizcagc" # 你邮箱的密码，不是真正的密码，是原邮箱生成的POP3内个

    # 服务器
    smtp_server = 'smtp.qq.com'

    try:
        # 所发送内容
        msg = MIMEText(send_msg, 'plain', 'utf-8')

        # 邮箱头信息
        msg['From'] = Header(send_address)
        msg['To'] = Header(receiver)
        msg['Subject'] = Header(title)

        server = smtplib.SMTP_SSL(host=smtp_server)
        server.connect(smtp_server, 465)
        server.login(send_address, password=send_pwd)
        server.sendmail(send_address, receiver, msg.as_string())
        server.quit()
    except:
        pass


# 常规项目：温度选择+体温填报
def temp_common(driver):
    driver.find_element_by_xpath('//*[@id="main"]/div[1]/label[2]').click()
    time.sleep(0.5)
    driver.find_element_by_xpath('//*[@id="main"]/div[4]/label[2]').click()
    time.sleep(0.5)
    temp = driver.find_elements_by_class_name("mdui-textfield-input")
    temp[0].clear()
    morning_temp = str(random.uniform(36.3, 36.7))[:4:]
    temp[0].send_keys(morning_temp)
    temp[1].clear()
    afternoon_temp = str(random.uniform(36.3, 36.7))[:4:]
    temp[1].send_keys(afternoon_temp)


# 特殊项目
def temp_special(driver):
    # 今日健康状况
    driver.find_element_by_xpath('//*[@id="main"]/div[7]/label[2]').click()
    time.sleep(0.3)
    # 目前状态
    driver.find_element_by_xpath('//*[@id="main"]/div[9]/label[2]').click()
    time.sleep(0.3)
    # 离校后是否已进行核算检测
    driver.find_element_by_xpath('//*[@id="main"]/div[10]/label[2]').click()
    time.sleep(0.3)
    # 核算检测结果
    driver.find_element_by_xpath('//*[@id="main"]/div[11]/label[2]').click()


# 读取用户账户密码
def get_usr_info(filePath):
    usr_info = None
    try:
        f = open(filePath, encoding='utf-8')
        usr_info = json.loads(f.read())
    except:
       print("出现了错误")
       pass
    return usr_info


def home(driver):
    div = driver.find_element_by_xpath('//*[@id="main"]/div[9]/label[1]').text
    home_text = '*共同生活家人是否出现新冠肺炎确诊、无症状感染、核酸检测阳性或与确诊疑似病例密接、次密接等情况'
    if div ==home_text:
        driver.find_element_by_xpath('//*[@id="main"]/div[9]/label[3]').click()


# 判断是否已经完成填报
def get_result(driver):
    # 未完成或无法获取则返回false，完成则返回true
    try:
        text = driver.find_element_by_class_name("mdui-list-item-content").text
        if text.split('\n')[1]=='未完成':
            return False
        else:
            return True
    except: 
        return False


# 填写脚本程序
def run_main(name, username, password, mail_address, achieve_count, correct_send_mail_count):
    """

    :param name: 填报人
    :param usrname: 填报人学号
    :param password: 密码
    :param mail_address: 填报人邮箱
    :return:
    """
    # 打开浏览器
    url = 'http://xscfw.hebust.edu.cn/survey/login'
    isRun = False

    try:
        driver.get(url)
        sleep(2)
        driver.find_element_by_name('user').send_keys(username)
        driver.find_element_by_name('pwd').send_keys(password)
        driver.find_element_by_id('login').click()
        sleep(2)

        if get_result(driver):
            # 判断是否已完成
            achieve_count += 1
            correct_send_mail_count += 1
            
        else:
            try:
                driver.find_element_by_class_name("mdui-list-item-content").click()
            except:
                isRun = True
                send_MAIL(title="体温填报失败", send_msg="当前可能无法填报，您可以自行打开检查，或者等待填报成功的邮件", receiver=mail_address)

            # 常规项目填报
            temp_common(driver)
            # 近日健康状况
            driver.find_element_by_xpath('//*[@id="main"]/div[7]/label[2]').click()
            #time.sleep(0.3)
            # 非常规项目填报
            # temp_special(driver)
            
            try:
                # 家人项目填报
                home(driver)
            except:
                pass
            sleep(1)
            driver.find_element_by_id("save").click()
            sleep(2)

            try:
                # 判断是否填报成功
                driver.find_element_by_class_name("mdui-list-item-content").text
                if get_result(driver):
                    achieve_count += 1
                    correct_send_mail_count += 1
                    send_msg = "亲爱的" + name + ":体温填报完成！"
                    send_MAIL(title="体温填报成功", send_msg=send_msg, receiver=mail_address)
            except:
                sleep(5)
                send_MAIL(title="体温填报失败", send_msg="当前的填报项目可能出现了变化，建议您自行填报", receiver=mail_address)
    except:
        sleep(5)
        send_MAIL(title="体温填报失败", send_msg="当前的填报项目可能出现了变化，建议您自行填报", receiver=mail_address)
    return achieve_count, correct_send_mail_count, isRun




if __name__ == '__main__':
    print("该程序每两分钟执行一次，检测当前时间是否在体温填报范围时间内。\n若在体温填报时间内，则开始填报，否则pass")
    filePath = "Username_Password.json"
    isRun = True
    achieve_count = 0
    correct_send_mail_count = 0
    driver = None
    while True:
        print("====================开始执行====================")
        now_time = time.strftime("%H:%M:%S", time.localtime())
        now_time = int(now_time.replace(':', ''))
        if 113000 <= now_time <= 133000 and isRun:
            isRun = False
            usr_info = get_usr_info(filePath)
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
            achieve_count = 0
            correct_send_mail_count = 0
            for key in usr_info.keys():
                try:
                    achieve_count, correct_send_mail_count, isRun = run_main(name=usr_info[key]["name"],
                                                                      username=usr_info[key]["username"],
                                                                      password=usr_info[key]["password"],
                                                                      mail_address=usr_info[key]["mailAddress"],
                                                                      achieve_count=achieve_count,
                                                                      correct_send_mail_count=correct_send_mail_count)
                    if isRun == True:
                        break
                except:
                    print("error")
                    pass
            try:
                driver.close()
            except:
                pass
            send_MAIL(title="完成人数/总人数 = " + str(achieve_count) + "/" + str(len(usr_info)),
                      send_msg="完成人数/总人数 = " + str(achieve_count) + "/" + str(len(usr_info)) + "\n" +
                               "正确发送邮件" + str(correct_send_mail_count) + "封",
                      receiver="15562969068@163.com")  # <-输入你的邮箱，相当于管理员，每天接收总的填报情况

        elif 10000 <= now_time <= 100000:
            isRun = True
            time.sleep(3600)
        now_time = time.strftime("%H:%M:%S", time.localtime())
        print("当前时间" + str(now_time))
        print("====================本次执行结束====================")
        sleep(60)
