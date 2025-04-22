import pytest
import subprocess
import json
import os
import sys

# -----------------------
# Utility: run the C++ minimizer
# -----------------------
def run_dfa_minimizer(input_data):
    # Путь к исполняемому файлу относительно этого теста
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dfa_minimizer_path = os.path.join(current_dir, "dfa_minimizer")

    if not os.path.exists(dfa_minimizer_path):
        pytest.skip(f"Исполняемый файл не найден: {dfa_minimizer_path}")
    if not os.access(dfa_minimizer_path, os.X_OK):
        pytest.skip(f"Нет прав на выполнение: {dfa_minimizer_path}")

    proc = subprocess.run(
        [dfa_minimizer_path],
        input=json.dumps(input_data),
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None, proc.stderr.strip()

    out = proc.stdout.strip()
    if not out:
        return None, "Пустой вывод от C++ программы"
    try:
        return json.loads(out), None
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError: {e}\nВывод: {out!r}"

# -----------------------
# Utility: simulate DFA on a word
# -----------------------
def simulate_dfa(dfa, word):
    state = dfa["start_state"]
    # Построим карту переходов
    trans = {(t["from"], t["input"]): t["to"] for t in dfa["transitions"]}
    for ch in word:
        key = (state, ch)
        if key not in trans:
            return False
        state = trans[key]
    return state in set(dfa.get("final_states", []))

# -----------------------
# Utility: проверка эквивалентности двух DFA
# -----------------------
def check_equivalence(dfa1, dfa2, test_words):
    for w in test_words:
        acc1 = simulate_dfa(dfa1, w)
        acc2 = simulate_dfa(dfa2, w)
        if acc1 != acc2:
            return False, f"Разное поведение на слове {w!r}: {acc1} != {acc2}"
    return True, "Эквивалентны"

# Слова для тестирования эквивалентности
TEST_WORDS = [
    "", "a", "b", "aa", "ab", "ba", "bb",
    "aaa", "aab", "aba", "abb", "baa", "bba", "bbb"
]

# -----------------------
# Тестовые случаи
# -----------------------

TEST_CASES = [
    (
        "basic_merge",
        {
            "num_states": 4,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 2},
                {"from": 1, "input": "a", "to": 0},
                {"from": 1, "input": "b", "to": 3},
                {"from": 2, "input": "a", "to": 3},
                {"from": 2, "input": "b", "to": 0},
                {"from": 3, "input": "a", "to": 2},
                {"from": 3, "input": "b", "to": 1},
            ],
            "start_state": 0,
            "final_states": [0],
        },
        {
            "num_states": 4,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 2},
                {"from": 1, "input": "a", "to": 0},
                {"from": 1, "input": "b", "to": 3},
                {"from": 2, "input": "a", "to": 3},
                {"from": 2, "input": "b", "to": 0},
                {"from": 3, "input": "a", "to": 2},
                {"from": 3, "input": "b", "to": 1},
            ],
            "start_state": 0,
            "final_states": [0],
        },
    ),
    (
        "unreachable_state",
        {
            "num_states": 3,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 0},
                {"from": 2, "input": "a", "to": 2},
                {"from": 2, "input": "b", "to": 2},
            ],
            "start_state": 0,
            "final_states": [1],
        },
        {
            "num_states": 2,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 0},
            ],
            "start_state": 0,
            "final_states": [1],
        },
    ),
    (
        "equivalent_states",
        {
            "num_states": 3,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 2},
                {"from": 1, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 1},
                {"from": 2, "input": "a", "to": 2},
                {"from": 2, "input": "b", "to": 2},
            ],
            "start_state": 0,
            "final_states": [1, 2],
        },
        {
            "num_states": 2,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 1},
                {"from": 1, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 1},
            ],
            "start_state": 0,
            "final_states": [1],
        },
    ),
    # ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ:
    
    (
        "even_number_of_as",
        {
            "num_states": 3,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 0},
                {"from": 1, "input": "a", "to": 0},
                {"from": 1, "input": "b", "to": 1},
            ],
            "start_state": 0,
            "final_states": [0],
        },
        {
            "num_states": 2,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 0},
                {"from": 1, "input": "a", "to": 0},
                {"from": 1, "input": "b", "to": 1},
            ],
            "start_state": 0,
            "final_states": [0],
        },
    ),
    (
        "strings_ending_with_ab",
        {
            "num_states": 4,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 0},
                {"from": 1, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 2},
                {"from": 2, "input": "a", "to": 1},
                {"from": 2, "input": "b", "to": 0},
            ],
            "start_state": 0,
            "final_states": [2],
        },
        {
            "num_states": 3,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 0},
                {"from": 1, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 2},
                {"from": 2, "input": "a", "to": 1},
                {"from": 2, "input": "b", "to": 0},
            ],
            "start_state": 0,
            "final_states": [2],
        },
    ),
    (
        "at_least_one_a_and_one_b",
        {
            "num_states": 5,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 2},
                {"from": 1, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 3},
                {"from": 2, "input": "a", "to": 3},
                {"from": 2, "input": "b", "to": 2},
                {"from": 3, "input": "a", "to": 3},
                {"from": 3, "input": "b", "to": 3},
                {"from": 4, "input": "a", "to": 4},
                {"from": 4, "input": "b", "to": 4},
            ],
            "start_state": 0,
            "final_states": [3],
        },
        {
            "num_states": 4,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 1},
                {"from": 0, "input": "b", "to": 2},
                {"from": 1, "input": "a", "to": 1},
                {"from": 1, "input": "b", "to": 3},
                {"from": 2, "input": "a", "to": 3},
                {"from": 2, "input": "b", "to": 2},
                {"from": 3, "input": "a", "to": 3},
                {"from": 3, "input": "b", "to": 3},
            ],
            "start_state": 0,
            "final_states": [3],
        },
    ),
    (
        "only_bs",
        {
            "num_states": 3,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 2},
                {"from": 0, "input": "b", "to": 1},
                {"from": 1, "input": "a", "to": 2},
                {"from": 1, "input": "b", "to": 1},
                {"from": 2, "input": "a", "to": 2},
                {"from": 2, "input": "b", "to": 2},
            ],
            "start_state": 0,
            "final_states": [0, 1],
        },
        {
            "num_states": 3,
            "alphabet": ["a", "b"],
            "transitions": [
                {"from": 0, "input": "a", "to": 2},
                {"from": 0, "input": "b", "to": 1},
                {"from": 1, "input": "a", "to": 2},
                {"from": 1, "input": "b", "to": 1},
                {"from": 2, "input": "a", "to": 2},
                {"from": 2, "input": "b", "to": 2},
            ],
            "start_state": 0,
            "final_states": [0, 1],
        },
    ),
]

# -----------------------
# Параметризованный тест
# -----------------------
@pytest.mark.parametrize("name,input_data,expected", TEST_CASES)
def test_dfa_minimization(name, input_data, expected):
    output, error = run_dfa_minimizer(input_data)
    assert error is None, f"[{name}] ошибка выполнения: {error}"
    are_eq, reason = check_equivalence(output, expected, TEST_WORDS)
    assert are_eq, f"[{name}] неэквивалентны: {reason}"
