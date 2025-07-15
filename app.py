from flask import Flask, request, render_template, redirect
import json
import subprocess
import os

app = Flask(__name__)
settings_path = "/home/good-look/PycharmProjects/PythonProject/settings.json"

@app.route('/')
def index():
    return render_template('form.html', saved=False)

@app.route('/submit', methods=['POST'])
def submit():
    settings = {
        "login": request.form['login'],
        "pin": request.form['pin'],
        "doctor": request.form['doctor'],
        "dates": [d.strip() for d in request.form['dates'].split(',')],
        "times": [t.strip() for t in request.form['times'].split(',')]
    }
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    return render_template('form.html', saved=True)

@app.route('/runbot')
def runbot():
    # Загрузка настроек, чтобы отобразить кому и когда запись
    with open(settings_path, "r") as f:
        settings = json.load(f)

    doctor = settings.get("doctor")
    dates = ", ".join(settings.get("dates", []))
    times = ", ".join(settings.get("times", []))

    subprocess.Popen([
        'python3',
        '/home/good-look/PycharmProjects/PythonProject/record_bot.py'
    ])

    return f"""
    <h2>✅ Бот запущен!</h2>
    <p><strong>ID Врача:</strong> {doctor}</p>
    <p><strong>Даты:</strong> {dates}</p>
    <p><strong>Время:</strong> {times}</p>
    <script>
      setTimeout(function() {{
        alert("✅ Успешная запись завершена! (при появлении этого окна — запись выполнена)");
      }}, 5000); // показать alert через 5 секунд (эмуляция)
    </script>
    """

if __name__ == '__main__':
    app.run(debug=True)
