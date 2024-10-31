from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit_form():
    series = request.form["series"]
    number = request.form["number"]
    birthday = request.form["birthday"]

    result_text = ""

    try:
        response = requests.post(
            "https://opendata.hsc.gov.ua/check-driver-license/",
            data={
                "seria": series,
                "number": number,
                "birthday_system": birthday,
            },
            verify=False,  # Отключение проверки сертификата
        )

        # Проверка на успешный ответ
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Парсинг HTML-ответа
            result_container = soup.find("div", class_="container-fluid")
            if result_container:
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
                        row_num = cols[0].text.strip()
                        category = cols[2].text.strip()
                        date = cols[3].text.strip()
                        result_text += f"{row_num}    {category}:    {date}\n"

                # Парсинг ограничений
                restrictions_row = result_container.find("th", string="Обмеження:")
                if restrictions_row:
                    restrictions = restrictions_row.find_next_sibling("th").text.strip()
                    result_text += f"\n{restrictions}\n"
                    print(result_text)
        else:
            result_text = "Не удалось получить данные с сайта."

    except Exception as e:
        result_text = f"Ошибка: {str(e)}"

    return render_template("form.html", result=result_text)


if __name__ == "__main__":
    app.run(debug=True)
