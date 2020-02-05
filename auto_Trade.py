import numpy as np
import pandas as pd
import time
import bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 전역 변수들
import private_info # 개인정보있는 파일
my_ID = private_info.my_ID
my_PW = private_info.my_PW

prev_my_Money = 0
my_Money = 0
start_invest_money = 1000 # KRW
martin_process = [start_invest_money]
current_invest_money = start_invest_money
current_martin = 0
invested_res = 0

df = pd.read_csv('./result.csv')

bitb_price = { 1:500000, 2:100000, 3:50000, 4:10000, 5:5000, 6:1000 } # css select순 금액

# 마틴을 순차적으로 어떤 금액을 걸지 정한다.
for i in range(1,12): # 최대 거래가능 금액 250000
    count = 0
    loss = -1*sum(martin_process[:i])
    while loss<1000:
        loss += 1000
        count+=1
    martin_process.append( 1000*count )
print(F"마틴은 이렇게 진행합니다. \n{martin_process}")

# 웹 드라이버를 켠다
driver = webdriver.Chrome("./chromedriver")
driver.implicitly_wait(1)

# 사이트 접속
driver.get("http://www.bitb.kr/")

# 로딩 대기
wait = WebDriverWait(driver, 10)


def waiting(_type, name):
    try:
        if _type == "class":
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, name)))
        elif _type == "id":
            element = wait.until(EC.element_to_be_clickable((By.ID, name)))
        else:
            print("type error", _type, " cannot resolve")
    except Exception as e:
        driver.refresh()
        time.sleep(1)
        print(e, "\n Cannot find that element")


def site_setting():

    waiting("class", "login-btn-box")

    # 로그인 버튼 클릭
    driver.find_element_by_class_name("login-btn").click()

    waiting("id", "email")

    # 아이디, 비밀번호 입력
    driver.find_element_by_id("email").send_keys(my_ID)
    driver.find_element_by_id("password").send_keys(my_PW)

    # 모의 투자로 전환
    driver.find_element_by_xpath('//*[@id="account_type"]/option[2]').click()

    # 로그인
    driver.find_element_by_class_name("login-member").click()

    waiting("class", "login-btn")

    # 거래소 접속
    driver.find_element_by_class_name("nav-link").click()
    driver.find_element_by_css_selector('#navbarSupportedContent > ul > li.nav-item.dropdown.show > div > a:nth-child(1)').click()

    waiting("id", "open_price_div2")
    return

# 전값을 찾는다.
def find_previous_result(previous_contract_number):
    all_text = driver.find_element_by_tag_name('body').get_attribute("innerHTML")
    key_word = F"<tspan>{previous_contract_number}"
    text_pos = all_text.find(key_word)

    summary_text = all_text[text_pos: text_pos+100]

    if( "매도" in summary_text ):
        return "매도"
    elif( "매수" in summary_text ):
        return "매수"
    else:
        return 0

# 체결까지 남은시간 추출
def get_remain_time():
    remain_time = driver.find_element_by_id("left_rent_time_div").get_attribute("innerText")
    minute = remain_time[:2]
    hour = remain_time[3:]
    return (minute, hour)

# 체결할때 팝업창 제거
def click_popUp():
    driver.implicitly_wait(5)
    driver.switch_to.alert.accept()
    driver.implicitly_wait(5)
    driver.switch_to.alert.accept()

# 어떻게 체결할것인가
def buy(up_or_down, amount):

    # 마틴투자 금액별 클릭순서
    martin_info = {"1000": [0],
                   "2000": [0,0],
                   "4000": [0,0,0,0],
                   "7000": [1,0,0],
                   "13000": [2,0,0,0],
                   "24000": [2,2,0,0,0,0],
                   "45000": [2,2,2,2,1],
                   "84000": [3,2,2,2,0,0,0,0],
                   "156000": [4,3,1,0],
                   "290000": [4,4,3,2,2,2,2],
                   "539000": [5,2,2,2,1,0,0,0,0],
                   "1003000": [5,5,0,0,0]}

    driver.refresh()
    waiting("id", "left_rent_time_div")

    if (up_or_down == 1):
        for i in martin_info[F"{amount}"]:
            # driver.refresh()
            # waiting("id", "left_rent_time_div")
            time.sleep(1)
            # driver.find_element_by_css_selector(f"#nav-11 > div > table > tbody > tr:nth-child({abs(i-6)}) > td:nth-child(2) > a").click()
            # alert = driver.switch_to.alert
            # alert.accept()
            driver.find_element_by_css_selector(
                f"#nav-11 > div > table > tbody > tr:nth-child({abs(i - 6)}) > td:nth-child(2) > a").click()
            alert = driver.switch_to.alert
            alert.accept()
            for _ in range(3):
                time.sleep(1)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except Exception as e:
                    print(e)
            # click_popUp()
    elif (up_or_down == -1):
        for i in martin_info[F"{amount}"]:
            # driver.refresh()
            # waiting("id", "left_rent_time_div")
            time.sleep(1)
            # driver.find_element_by_css_selector(f"#nav-11 > div > table > tbody > tr:nth-child({abs(i-6)}) > td:nth-child(4) > a").click()
            # try:
            #     alert = driver.switch_to.alert
            # except:
            #     alert = driver.switch_to.alert
            # alert.accept()
            driver.find_element_by_css_selector(
                f"#nav-11 > div > table > tbody > tr:nth-child({abs(i - 6)}) > td:nth-child(4) > a").click()
            alert = driver.switch_to.alert
            alert.accept()
            for _ in range(3):
                time.sleep(1)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except Exception as e:
                    print(e)
    else:
        print(up_or_down, "인수가 잘못되었습니다.")
    # 체결 완료


def main():
    site_setting()
    # driver.refresh()
    # waiting("id", "left_rent_time_div")
    while(1):
        driver.refresh()
        waiting("id", "left_rent_time_div")
        try:
            # 현재 시드머니 확인
            my_Money = driver.find_element_by_id("mybalance_div").get_attribute("innerText")
            print(F"현재 시드머니는 {my_Money} 입니다.")

            # 현재 차시 확인
            current_case = driver.find_element_by_id("basic_time_div").get_attribute("innerText")[:-4]
            print(F"현재 {current_case}차 입니다.")

            # 이전 차시 결과값 확인
            while(current_case == ''):
                print("현재차시를 못찾았습니다. 다시시도 합니다.")
                driver.refresh()
                waiting("id", "open_price_div2")
                current_case = driver.find_element_by_id("basic_time_div").get_attribute("innerText")[:-4]
                print(F"현재 {current_case}차 입니다.")

            prev_case = int(current_case)-1
            prev_prev_case = int(current_case)-2

            prev_res = find_previous_result(prev_case)
            prev_prev_res = find_previous_result(prev_prev_case)

            while( prev_res == 0 ):
                # 새로고침
                driver.refresh()
                waiting("id", "left_rent_time_div")
                prev_res = find_previous_result(prev_case)

                # # 남은시간 체크
                # remain_time = get_remain_time()
                # if( remain_time[0] == "00" and int(remain_time[1]) < 10 ): # 시간이 촉박할때까지 결과값이 안나오면 패스
                #     break #체결시간 다 지나도록 안나올때 처리 구현하기
            print(F"전 차시({prev_case}차)의 결과값은 ", prev_res)
            print(F"전전 차시({prev_prev_case}차)의 결과값은 ", prev_prev_res)

            if (prev_res == "매도"):
                prev_res = -1
            elif (prev_res == "매수"):
                prev_res = 1
            if (prev_prev_res == "매도"):
                prev_prev_res = -1
            elif (prev_prev_res == "매수"):
                prev_prev_res = 1

            # # 값을 반전시켜줌
            # prev_res = -1*prev_res

            try:
                if (len(df["case"].values) == 0):
                    df.loc[len(df)] = [prev_case, prev_res,0]
                    current_martin = 0
                elif( df["case"].values[-1] == prev_case ):
                    continue
                else:
                    df.loc[len(df)+1] = [prev_case, prev_res,0]

                    print(invested_res, prev_res)
                    # 실격이면
                    if (invested_res == 0):
                        pass
                    elif (invested_res != prev_res):  # 실격이면
                        current_martin = (current_martin + 1) % 1 # 마틴제한은 2단계까지
                        print("실격입니다.")
                    else: # 실격아니면
                        current_martin = 0
                        print('실현입니다.')
            except Exception as e:
                current_martin = 0
                driver.refresh()
                waiting("id", "left_rent_time_div")
                print(e)

            driver.refresh()
            waiting("id", "left_rent_time_div")
            time.sleep(2)

            # 체결 시도
            prev_my_Money = my_Money
            print("현재자산: ", my_Money)
            print("현재마틴: ", current_martin)
            print("투자할 금액: ", martin_process[current_martin])
            invested_res = prev_res
            print(f"전값인 {prev_res}에 투자")
            # print(f"전전값인 {prev_prev_res}에 투자")
            driver.refresh()
            waiting("id", "left_rent_time_div")
            df.to_csv('./result.csv')

            buy(prev_prev_res, martin_process[current_martin])
            # buy(prev_res, 1000)
            print("체결하였습니다")
            print()
            time.sleep(120)

        except Exception as e:
            print(e)
            driver.refresh()
            waiting("id", "left_rent_time_div")
            continue


if __name__ == '__main__':
    main()
