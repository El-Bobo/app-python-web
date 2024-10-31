from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)


CHROMEDRIVER_PATH = r"C:\Users\New\Desktop\app-python-web/chromedriver.exe"


@app.route("/")
def index():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit_form():

    series = request.form["series"]
    number = request.form["number"]
    birthday = request.form["birthday"]

    service = Service(CHROMEDRIVER_PATH)

    driver = webdriver.Chrome(service=service)

    try:
        driver.get("https://opendata.hsc.gov.ua/check-driver-license/")

        driver.find_element(By.ID, "seria").send_keys(series)
        driver.find_element(By.ID, "number").send_keys(number)
        driver.find_element(By.ID, "birthday_system").send_keys(birthday)

        driver.find_element(By.XPATH, "//input[@value='ПЕРЕВІРИТИ | CHECK']").click()

        result_text = "Результат не найден"
        try:
            result = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result_class_name"))
            )
            result_text = result.text
        except:
            result_text = "Ошибка: результат не найден"

    finally:
        driver.quit()

    return render_template("form.html", result=result_text)


if __name__ == "__main__":
    app.run(debug=True)
