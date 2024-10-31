from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

CHROMEDRIVER_PATH = r"app-python-web\chromedriver.exe"


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

    result_text = ""

    try:
        driver.get("https://opendata.hsc.gov.ua/check-driver-license/")

        driver.find_element(By.ID, "seria").send_keys(series)
        driver.find_element(By.ID, "number").send_keys(number)
        driver.find_element(By.ID, "birthday_system").send_keys(birthday)
        driver.find_element(By.XPATH, "//input[@value='ПЕРЕВІРИТИ | CHECK']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container-fluid"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        result_container = soup.find("div", class_="container-fluid")
        if result_container:
            # Парсинг имени
            name = result_container.find("a", {"data-i18n": "_info"}).text.strip()
            result_text += f"Документ на ім'я: {name}\n\n"

            # Парсинг информации с номерами строк
            rows = result_container.find_all("tr")
            for row in rows:
                cols = row.find_all("th")
                if len(cols) == 3:
                    row_num = cols[0].text.strip()
                    label = cols[1].text.strip()
                    value = cols[2].text.strip()
                    result_text += f"{row_num}    {label}    {value}\n"
                elif len(cols) == 4 and "Категорія" in cols[2].text:
                    # Обработка категорий
                    row_num = cols[0].text.strip()
                    category = cols[2].text.strip()
                    date = cols[3].text.strip()
                    result_text += f"{row_num}    {category}:    {date}\n"

            # Парсинг ограничений
            restrictions_row = result_container.find("th", string="Обмеження:")
            if restrictions_row:
                restrictions = restrictions_row.find_next_sibling("th").text.strip()
                result_text += f"\n{restrictions}\n"

    except Exception as e:
        result_text = f"Ошибка: {str(e)}"

    finally:
        driver.quit()

    return render_template("form.html", result=result_text)


if __name__ == "__main__":
    app.run(debug=True)
