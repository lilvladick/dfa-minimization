import subprocess
import json
import os

# Функция для запуска программы и получения вывода
def run_dfa_minimizer(input_data):
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dfa_minimizer_path = os.path.join(current_dir, 'dfa_minimizer')
    process = subprocess.run(
        [dfa_minimizer_path],
        input=json.dumps(input_data),
        text=True,
        capture_output=True
    )
    if process.returncode != 0:
        return None, process.stderr
    try:
        output = json.loads(process.stdout)
        return output, None
    except json.JSONDecodeError:
        return None, "Ошибка декодирования JSON"

# Тест 1: Простой DFA с двумя состояниями
def test_simple_dfa():
    input_data = {
        "num_states": 2,
        "alphabet": ["a", "b"],
        "transitions": [
            {"from": 0, "input": "a", "to": 1},
            {"from": 0, "input": "b", "to": 0},
            {"from": 1, "input": "a", "to": 1},
            {"from": 1, "input": "b", "to": 1}
        ],
        "start_state": 0,
        "final_states": [1]
    }
    expected_output = {
        "num_states": 2,
        "alphabet": ["a", "b"],
        "transitions": [
            {"from": 0, "input": "a", "to": 1},
            {"from": 0, "input": "b", "to": 0},
            {"from": 1, "input": "a", "to": 1},
            {"from": 1, "input": "b", "to": 1}
        ],
        "start_state": 0,
        "final_states": [1]
    }
    output, error = run_dfa_minimizer(input_data)
    if error:
        print(f"Тест не пройден: {error}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, f"Ошибка выполнения: {error}"
    elif output == expected_output:
        print("Тест 'Простой DFA с двумя состояниями' пройден успешно")
        assert True
    else:
        print("Тест не пройден: выход не совпадает с ожидаемым")
        print(f"Получено: {json.dumps(output, indent=2)}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, "Выход не совпадает с ожидаемым"

# Тест 2: DFA с недостижимыми состояниями
def test_unreachable_states():
    input_data = {
        "num_states": 3,
        "alphabet": ["0", "1"],
        "transitions": [
            {"from": 0, "input": "0", "to": 1},
            {"from": 0, "input": "1", "to": 1},
            {"from": 1, "input": "0", "to": 1},
            {"from": 1, "input": "1", "to": 1},
            {"from": 2, "input": "0", "to": 2},
            {"from": 2, "input": "1", "to": 2}
        ],
        "start_state": 0,
        "final_states": [1]
    }
    expected_output = {
        "num_states": 2,
        "alphabet": ["0", "1"],
        "transitions": [
            {"from": 0, "input": "0", "to": 1},
            {"from": 0, "input": "1", "to": 1},
            {"from": 1, "input": "0", "to": 1},
            {"from": 1, "input": "1", "to": 1}
        ],
        "start_state": 0,
        "final_states": [1]
    }
    output, error = run_dfa_minimizer(input_data)
    if error:
        print(f"Тест не пройден: {error}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, f"Ошибка выполнения: {error}"
    elif output == expected_output:
        print("Тест 'DFA с недостижимыми состояниями' пройден успешно")
        assert True
    else:
        print("Тест не пройден: выход не совпадает с ожидаемым")
        print(f"Получено: {json.dumps(output, indent=2)}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, "Выход не совпадает с ожидаемым"

# Тест 3: DFA, который можно минимизировать
def test_minimizable_dfa():
    input_data = {
        "num_states": 4,
        "alphabet": ["a", "b"],
        "transitions": [
            {"from": 0, "input": "a", "to": 1},
            {"from": 0, "input": "b", "to": 2},
            {"from": 1, "input": "a", "to": 1},
            {"from": 1, "input": "b", "to": 3},
            {"from": 2, "input": "a", "to": 1},
            {"from": 2, "input": "b", "to": 2},
            {"from": 3, "input": "a", "to": 1},
            {"from": 3, "input": "b", "to": 2}
        ],
        "start_state": 0,
        "final_states": [1, 3]
    }
    expected_output = {
        "num_states": 3,
        "alphabet": ["a", "b"],
        "transitions": [
            {"from": 0, "input": "a", "to": 1},
            {"from": 0, "input": "b", "to": 2},
            {"from": 1, "input": "a", "to": 1},
            {"from": 1, "input": "b", "to": 2},
            {"from": 2, "input": "a", "to": 1},
            {"from": 2, "input": "b", "to": 2}
        ],
        "start_state": 0,
        "final_states": [1]
    }
    output, error = run_dfa_minimizer(input_data)
    if error:
        print(f"Тест не пройден: {error}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, f"Ошибка выполнения: {error}"
    elif output == expected_output:
        print("Тест 'DFA, который можно минимизировать' пройден успешно")
        assert True
    else:
        print("Тест не пройден: выход не совпадает с ожидаемым")
        print(f"Получено: {json.dumps(output, indent=2)}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, "Выход не совпадает с ожидаемым"

# Тест 4: DFA с одним состоянием
def test_single_state_dfa():
    input_data = {
        "num_states": 1,
        "alphabet": ["a"],
        "transitions": [
            {"from": 0, "input": "a", "to": 0}
        ],
        "start_state": 0,
        "final_states": [0]
    }
    expected_output = {
        "num_states": 1,
        "alphabet": ["a"],
        "transitions": [
            {"from": 0, "input": "a", "to": 0}
        ],
        "start_state": 0,
        "final_states": [0]
    }
    output, error = run_dfa_minimizer(input_data)
    if error:
        print(f"Тест не пройден: {error}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, f"Ошибка выполнения: {error}"
    elif output == expected_output:
        print("Тест 'DFA с одним состоянием' пройден успешно")
        assert True
    else:
        print("Тест не пройден: выход не совпадает с ожидаемым")
        print(f"Получено: {json.dumps(output, indent=2)}")
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}")
        assert False, "Выход не совпадает с ожидаемым"

# Тест 5: DFA с пустым алфавитом
def test_empty_alphabet_dfa():
    input_data = {
        "num_states": 2,
        "alphabet": [],
        "transitions": [],
        "start_state": 0,
        "final_states": [1]
    }
    output, error = run_dfa_minimizer(input_data)
    if error:
        print("Тест 'DFA с пустым алфавитом' пройден успешно: ожидалась ошибка")
        assert True
    else:
        print("Тест не пройден: ожидалась ошибка, но получен выход")
        print(f"Получено: {json.dumps(output, indent=2)}")
        assert False, "Ожидалась ошибка, но получен корректный вывод"