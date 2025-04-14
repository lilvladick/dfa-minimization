#include "minimize.hpp"
#include <vector>
#include <queue>
#include <set> 
#include <map> 
#include <algorithm>
#include <utility>


void minimize_dfa(DFA& dfa) {
    if (dfa.num_states <= 1) {
        // Автомат с 0 или 1 состоянием уже минимален.
        return;
    }
     if (dfa.start_state < 0 ) {
         // Невалидное начальное состояние. Можно вернуть ошибку или пустой автомат.
         dfa.num_states = 0;
         dfa.start_state = -1;
         dfa.transitions.clear();
         dfa.final_states.clear();
         dfa.alphabet.clear();
         return;
     }


    // 1. Поиск достижимых состояний с помощью BFS
    std::set<int> reachable; 
    std::queue<int> q;

    reachable.insert(dfa.start_state);
    q.push(dfa.start_state);

    while (!q.empty()) {
        int current_state = q.front();
        q.pop();

        for (char symbol : dfa.alphabet) {
            auto it = dfa.transitions.find({current_state, symbol});
            if (it != dfa.transitions.end()) {
                int next_state = it->second;
                // .second == true, если элемент был успешно вставлен (т.е. новый)
                if (reachable.insert(next_state).second) {
                    q.push(next_state);
                }
            }
        }
    }

    // Обработка случая, если начальное состояние недостижимо (или нет достижимых)
    if (reachable.empty() || reachable.find(dfa.start_state) == reachable.end()) {
         dfa.num_states = 0;
         dfa.start_state = -1;
         dfa.transitions.clear();
         dfa.final_states.clear();
         dfa.alphabet.clear();
         return;
     }

    std::map<int, std::map<char, std::set<int>>> rev_transitions;
    for (int state : reachable) {
        for (char symbol : dfa.alphabet) {
            auto it = dfa.transitions.find({state, symbol});
            if (it != dfa.transitions.end()) {
                int target_state = it->second;
                if (reachable.count(target_state)) {
                    rev_transitions[target_state][symbol].insert(state);
                }
            }
        }
    }

    // 2. Начальное разбиение на финальные и нефинальные состояния (только достижимые)
    std::vector<std::set<int>> partitions;
    std::set<int> initial_final;
    std::set<int> initial_non_final;

    for (int state : reachable) {
        if (dfa.final_states.count(state)) {
            initial_final.insert(state);
        } else {
            initial_non_final.insert(state);
        }
    }

    if (!initial_non_final.empty()) {
        partitions.push_back(std::move(initial_non_final));
    }
    if (!initial_final.empty()) {
        partitions.push_back(std::move(initial_final));
    }

    // 3. Присвоение классов состояниям (индекс в partitions)
    std::map<int, int> state_class;
    for (size_t i = 0; i < partitions.size(); ++i) {
        for (int state : partitions[i]) {
            state_class[state] = i;
        }
    }

    // 4. Алгоритм Хопкрофта
    std::set<int> worklist;
    if (partitions.size() > 1) {
        if (partitions[0].size() <= partitions[1].size()) {
            worklist.insert(0);
        } else {
            worklist.insert(1);
        }
    }

    while (!worklist.empty()) {
        int partition_index_A = *worklist.begin();
        worklist.erase(worklist.begin());
        const auto& A = partitions[partition_index_A];

        for (char symbol : dfa.alphabet) {
            std::set<int> X;
            for (int state_in_A : A) {
                auto rev_target_it = rev_transitions.find(state_in_A);
                if (rev_target_it != rev_transitions.end()) {
                    auto rev_symbol_it = rev_target_it->second.find(symbol);
                    if (rev_symbol_it != rev_target_it->second.end()) {
                        const auto& sources = rev_symbol_it->second;
                        X.insert(sources.begin(), sources.end());
                    }
                }
            }

            if (X.empty()) {
                continue;
            }
            for (int i = static_cast<int>(partitions.size()) - 1; i >= 0; --i) {
                if (partitions[i].empty()) continue; // Пропускаем пустые разделы

                auto& Y = partitions[i]; 
                std::set<int> Y_intersect;
                std::set<int> Y_diff;

                for (int state_in_Y : Y) {
                    if (X.count(state_in_Y)) {
                        Y_intersect.insert(state_in_Y);
                    } else {
                        Y_diff.insert(state_in_Y);
                    }
                }

                if (Y_intersect.empty() || Y_diff.empty()) {
                    continue;
                }

                int new_partition_index = partitions.size();

                if (Y_intersect.size() <= Y_diff.size()) {
                    partitions.push_back(std::move(Y_intersect)); // Меньшая -> новая
                    partitions[i] = std::move(Y_diff);            // Большая -> старая (Y=partitions[i])
                } else {
                    partitions.push_back(std::move(Y_diff));      // Меньшая -> новая
                    partitions[i] = std::move(Y_intersect);       // Большая -> старая (Y=partitions[i])
                }

                // Обновляем классы для состояний в новом разделе
                for (int state : partitions.back()) {
                    state_class[state] = new_partition_index;
                }

                if (worklist.count(i)) {
                    // Если старый раздел Y(i) был в worklist, заменяем его обоими новыми
                    worklist.erase(i);
                    worklist.insert(i);
                    worklist.insert(new_partition_index);
                } else {
                    // Иначе добавляем только меньший (который стал новым)
                    worklist.insert(new_partition_index);
                }
            }
        }
    }

    // 5. Построение минимизированного DFA
    DFA minimizedDFA;
    minimizedDFA.alphabet = dfa.alphabet; 
    minimizedDFA.num_states = partitions.size();

    // Находим новое начальное состояние
    auto start_class_it = state_class.find(dfa.start_state);
    if (start_class_it != state_class.end()) {
        minimizedDFA.start_state = start_class_it->second;
    } else {
         minimizedDFA.start_state = -1;
         minimizedDFA.num_states = 0;
         minimizedDFA.transitions.clear();
         minimizedDFA.final_states.clear();
         dfa = std::move(minimizedDFA);
         return;
    }

    // Формирование переходов и финальных состояний
    for (size_t i = 0; i < partitions.size(); ++i) {
        if (partitions[i].empty()) continue; 

        int representative_state = *partitions[i].begin();

        if (dfa.final_states.count(representative_state)) {
            minimizedDFA.final_states.insert(i);
        }

        for (char symbol : minimizedDFA.alphabet) {
            auto it = dfa.transitions.find({representative_state, symbol});
            if (it != dfa.transitions.end()) {
                int old_target_state = it->second;
                // Находим класс целевого состояния (оно должно быть достижимо и иметь класс)
                auto target_class_it = state_class.find(old_target_state);
                if (target_class_it != state_class.end()) {
                    int new_target_state_class = target_class_it->second;
                    minimizedDFA.transitions.insert({{i, symbol}, new_target_state_class});
                }
            }
        }
    }
    dfa = std::move(minimizedDFA);
}