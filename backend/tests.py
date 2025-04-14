import subprocess
import json
import os
import sys

def run_dfa_minimizer(input_data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dfa_minimizer_path = os.path.join(current_dir, 'dfa_minimizer')

    if not os.path.exists(dfa_minimizer_path):
        return None, f"Ошибка: Исполняемый файл не найден по пути '{dfa_minimizer_path}'"
    if not os.access(dfa_minimizer_path, os.X_OK):
         return None, f"Ошибка: Нет прав на выполнение файла '{dfa_minimizer_path}'"

    try:
        process = subprocess.run(
            [dfa_minimizer_path],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            check=False
        )
        
        if process.returncode != 0:
            return None, f"Ошибка выполнения C++ программы (код {process.returncode}): {process.stderr}"
        try:
            stdout_cleaned = process.stdout.strip()
            if not stdout_cleaned:
                 return None, "Ошибка: Получен пустой вывод от C++ программы."
            output = json.loads(stdout_cleaned)
            return output, None
        except json.JSONDecodeError as e:
            return None, f"Ошибка декодирования JSON: {e}\nПолучено: '{process.stdout}'"

    except Exception as e:
         return None, f"Неожиданная ошибка при запуске C++ программы: {e}"


# Вспомогательная функция для сравнения DFA
def compare_dfa(output, expected):
    # Сравнение полей верхнего уровня
    if output.get("num_states") != expected.get("num_states"):
        return False, f"Разное количество состояний: получено {output.get('num_states')}, ожидалось {expected.get('num_states')}"
    if output.get("start_state") != expected.get("start_state"):
         return False, f"Разное начальное состояние: получено {output.get('start_state')}, ожидалось {expected.get('start_state')}"

    # Сравнение множеств (порядок не важен)
    if set(output.get("alphabet", [])) != set(expected.get("alphabet", [])):
        return False, f"Разный алфавит: получено {output.get('alphabet', [])}, ожидалось {expected.get('alphabet', [])}"
    if set(output.get("final_states", [])) != set(expected.get("final_states", [])):
        return False, f"Разные финальные состояния: получено {output.get('final_states', [])}, ожидалось {expected.get('final_states', [])}"

    # Сравнение переходов (порядок не важен, но содержимое важно)
    # Преобразуем список словарей в множество кортежей для сравнения
    try:
        output_transitions = set(tuple(sorted(t.items())) for t in output.get("transitions", []))
        expected_transitions = set(tuple(sorted(t.items())) for t in expected.get("transitions", []))
        if output_transitions != expected_transitions:
             return False, f"Разные переходы:\nПолучено: {sorted(list(output_transitions))}\nОжидалось: {sorted(list(expected_transitions))}"
    except TypeError:
        return False, "Не удалось сравнить переходы из-за типов данных"

    return True, "DFA совпадают"


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
        print(f"Тест 'Простой DFA' не пройден: {error}", file=sys.stderr)
        assert False, f"Ошибка выполнения: {error}"

    are_equal, reason = compare_dfa(output, expected_output)
    if are_equal:
        print("Тест 'Простой DFA с двумя состояниями' пройден успешно")
        assert True
    else:
        print("Тест 'Простой DFA' не пройден: выход не совпадает с ожидаемым", file=sys.stderr)
        print(f"Причина: {reason}", file=sys.stderr)
        print(f"Получено: {json.dumps(output, indent=2)}", file=sys.stderr)
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}", file=sys.stderr)
        assert False, f"Выход не совпадает с ожидаемым: {reason}"

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
            {"from": 2, "input": "0", "to": 2}, # Недостижимо
            {"from": 2, "input": "1", "to": 2}  # Недостижимо
        ],
        "start_state": 0,
        "final_states": [1]
    }
    # Ожидаем только состояния {0, 1}
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
        print(f"Тест 'Недостижимые состояния' не пройден: {error}", file=sys.stderr)
        assert False, f"Ошибка выполнения: {error}"

    are_equal, reason = compare_dfa(output, expected_output)
    if are_equal:
        print("Тест 'DFA с недостижимыми состояниями' пройден успешно")
        assert True
    else:
        print("Тест 'Недостижимые состояния' не пройден: выход не совпадает с ожидаемым", file=sys.stderr)
        print(f"Причина: {reason}", file=sys.stderr)
        print(f"Получено: {json.dumps(output, indent=2)}", file=sys.stderr)
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}", file=sys.stderr)
        assert False, f"Выход не совпадает с ожидаемым: {reason}"

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
    # Ожидаемый результат после минимизации {0,2}, {1}, {3} -> 0', 1', 2'
    expected_output = {
        "num_states": 3,
        "alphabet": ["a", "b"],
        "transitions": [
            # Переходы от класса {0,2} (новое состояние 0)
            {"from": 0, "input": "a", "to": 1}, # в класс {1} (новое 1)
            {"from": 0, "input": "b", "to": 0}, # в класс {0,2} (новое 0)
            # Переходы от класса {1} (новое состояние 1)
            {"from": 1, "input": "a", "to": 1}, # в класс {1} (новое 1)
            {"from": 1, "input": "b", "to": 2}, # в класс {3} (новое 2)
            # Переходы от класса {3} (новое состояние 2)
            {"from": 2, "input": "a", "to": 1}, # в класс {1} (новое 1)
            {"from": 2, "input": "b", "to": 0}  # в класс {0,2} (новое 0)
        ],
        "start_state": 0, # Класс {0,2} содержит исходное начальное 0
        "final_states": [1, 2] # Классы {1} и {3} содержат исходные финальные 1 и 3
    }
    output, error = run_dfa_minimizer(input_data)
    if error:
        print(f"Тест 'Минимизируемый DFA' не пройден: {error}", file=sys.stderr)
        assert False, f"Ошибка выполнения: {error}"

    are_equal, reason = compare_dfa(output, expected_output)
    if are_equal:
        print("Тест 'DFA, который можно минимизировать' пройден успешно")
        assert True
    else:
        print("Тест 'Минимизируемый DFA' не пройден: выход не совпадает с ожидаемым", file=sys.stderr)
        print(f"Причина: {reason}", file=sys.stderr)
        print(f"Получено: {json.dumps(output, indent=2)}", file=sys.stderr)
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}", file=sys.stderr)
        assert False, f"Выход не совпадает с ожидаемым: {reason}"


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
        print(f"Тест 'Одно состояние' не пройден: {error}", file=sys.stderr)
        assert False, f"Ошибка выполнения: {error}"

    are_equal, reason = compare_dfa(output, expected_output)
    if are_equal:
        print("Тест 'DFA с одним состоянием' пройден успешно")
        assert True
    else:
        print("Тест 'Одно состояние' не пройден: выход не совпадает с ожидаемым", file=sys.stderr)
        print(f"Причина: {reason}", file=sys.stderr)
        print(f"Получено: {json.dumps(output, indent=2)}", file=sys.stderr)
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}", file=sys.stderr)
        assert False, f"Выход не совпадает с ожидаемым: {reason}"

# Тест 5: DFA с пустым алфавитом
def test_empty_alphabet_dfa():
    input_data = {
        "num_states": 2,
        "alphabet": [],
        "transitions": [],
        "start_state": 0,
        "final_states": [1]
    }
    expected_output = {
        "num_states": 1,
        "alphabet": [],
        "transitions": [],
        "start_state": 0,
        "final_states": []
    }
    output, error = run_dfa_minimizer(input_data)

    if error:
        print(f"Тест 'Пустой алфавит' не пройден: получена ошибка '{error}'", file=sys.stderr)
        print(f"Ожидался выход: {json.dumps(expected_output, indent=2)}", file=sys.stderr)
        assert False, f"Ожидался корректный вывод, но получена ошибка: {error}"

    are_equal, reason = compare_dfa(output, expected_output)
    if are_equal:
        print("Тест 'DFA с пустым алфавитом' пройден успешно")
        assert True
    else:
        print("Тест 'Пустой алфавит' не пройден: выход не совпадает с ожидаемым", file=sys.stderr)
        print(f"Причина: {reason}", file=sys.stderr)
        print(f"Получено: {json.dumps(output, indent=2)}", file=sys.stderr)
        print(f"Ожидалось: {json.dumps(expected_output, indent=2)}", file=sys.stderr)
        assert False, f"Выход не совпадает с ожидаемым: {reason}"