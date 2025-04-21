from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/minimize_dfa', methods=['POST'])
def minimize_dfa():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Пустой или неверный JSON'}), 400
    except Exception:
        return jsonify({'error': 'Неверный JSON'}), 400

    input_json = json.dumps(data)

    # Получаем директорию, где находится server.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Формируем полный путь к dfa_minimizer
    dfa_minimizer_path = os.path.join(current_dir, 'dfa_minimizer')

    # Проверяем, существует ли файл
    if not os.path.isfile(dfa_minimizer_path):
        return jsonify({'error': f'Файл {dfa_minimizer_path} не найден'}), 500

    try:
        result = subprocess.run(
            [dfa_minimizer_path],
            input=input_json,
            text=True,
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Ошибка при вызове минимизатора', 'details': e.stderr}), 500
    except FileNotFoundError:
        return jsonify({'error': f'Файл {dfa_minimizer_path} не является исполняемым или не найден'}), 500

    try:
        output_json = result.stdout.strip()
        json.loads(output_json)
    except json.JSONDecodeError:
        return jsonify({'error': 'Минимизатор вернул невалидный JSON'}), 500

    return output_json, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)