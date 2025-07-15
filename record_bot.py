from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import json
from datetime import datetime
import traceback

def parse_date(date_str):
    return datetime.strptime(date_str, "%d.%m.%Y")

def send_telegram_message(message):
    bot_token = "     "
    chat_id = "  "
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Ошибка отправки в Telegram:", e)

# Загрузка настроек
try:
    with open("settings.json", "r") as f:
        settings = json.load(f)
except Exception as e:
    print("❌ Ошибка загрузки settings.json:", e)
    exit(1)

# Настройки Chrome
try:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
except Exception as e:
    print("❌ Ошибка инициализации WebDriver:")
    traceback.print_exc()
    exit(1)

# Основной цикл
while True:
    success = False
    try:
        print("🌐 Открываю сайт...")
        driver.get("https://lekar.medtut.by/cgi-bin/is10_08?sSd_=0&sfil_n=1&svid_=5&stst_=0&sgr_l=170&shead_=0&sit_l=210&style_=1&app_=0")

        print("🔐 Ввод логина/пин...")
        login_input = wait.until(EC.presence_of_element_located((By.ID, "n_id")))
        login_input.send_keys(settings["login"])

        pin_input = wait.until(EC.presence_of_element_located((By.ID, "n_pin")))
        pin_input.send_keys(settings["pin"])

        wait.until(EC.element_to_be_clickable((By.XPATH, "//font[contains(text(), 'Войти в личный кабинет')]/.."))).click()

        print("📋 Переход к врачу...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//th[.//font[contains(text(), 'Записаться на прием')]]"))).click()
        print("Записаться на прием")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//td[.//font[contains(text(), 'Гомельская городская клиническая поликлиника N3')]]"))).click()
        print("Гомельская городская клиническая поликлиника N3")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//th[contains(text(), 'Врач - хирург')]"))).click()
        print("Врач - хирург")
        doctor_name = settings['doctor']
        xpath_doctor = f"//p[contains(normalize-space(.), '{doctor_name}')]"
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_doctor))).click()

        print("📅 Проверка указанных дат...")
        for date in settings["dates"]:
            try:
                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, f"//th[contains(text(), '{date}')]")
                ))
                element.click()

                for time_str in settings["times"]:
                    try:
                        xpath = f"//input[@type='button' and contains(@value, '{time_str}') and contains(@onclick, 'save_it')]"
                        btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        btn.click()

                        alert_text = ""
                        try:
                            WebDriverWait(driver, 3).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            alert.accept()
                        except:
                            pass

                        try:
                            WebDriverWait(driver, 3).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            alert.accept()
                        except:
                            pass

                        success = True
                        send_telegram_message(f"✅ Успешная запись на {date} {time_str}:\n{alert_text or 'Без текста'}")
                        break
                    except:
                        continue
                if success:
                    break
            except:
                continue

        if not success:
            print("📆 Проверка ближайших доступных дат...")
            try:
                available_dates = driver.find_elements(By.XPATH, f"//th[contains(@onclick, '{settings['doctor']}')]")
                if available_dates:
                    sorted_dates = sorted(
                        [(el.text.strip(), el) for el in available_dates if el.text.strip()],
                        key=lambda x: parse_date(x[0])
                    )
                    closest_date_text, el = sorted_dates[0]
                    el.click()
                    print(f"ℹ️ Ближайшая дата: {closest_date_text}")

                    available_times = driver.find_elements(By.XPATH, "//input[@type='button' and contains(@onclick, 'save_it')]")
                    if available_times:
                        available_times[0].click()

                        alert_text = ""
                        try:
                            WebDriverWait(driver, 3).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            alert.accept()
                        except:
                            pass

                        try:
                            WebDriverWait(driver, 3).until(EC.alert_is_present())
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            alert.accept()
                        except:
                            pass

                        success = True
                        send_telegram_message(f"✅ Запись на ближайшую дату {closest_date_text}:\n{alert_text or 'Без текста'}")
            except Exception as e:
                print("⚠️ Ошибка при попытке найти ближайшую дату:", e)

    except Exception as e:
        print("❌ Общая ошибка:")
        traceback.print_exc()

    if success:
        print("🏁 Успешная запись — выход.")
        break
    else:
        print("🔁 Повтор через 30 секунд...")
        time.sleep(30)
        try:
            driver.refresh()
        except:
            pass
        time.sleep(3)

