#include "minimize.hpp"
#include <unordered_set>
#include <unordered_map>
#include <queue>
#include <vector>
#include <algorithm>

using namespace std;

void minimize_dfa(DFA& dfa) {
    // 1. Поиск достижимых состояний с помощью BFS
    unordered_set<int> reachable;
    queue<int> q;
    q.push(dfa.start_state);
    reachable.insert(dfa.start_state);
    
    while (!q.empty()) {
        int cur = q.front();
        q.pop();
        for (char symbol : dfa.alphabet) {
            auto it = dfa.transitions.find({cur, symbol});
            if (it != dfa.transitions.end()) {
                int next = it->second;
                if (reachable.insert(next).second) {
                    q.push(next);
                }
            }
        }
    }
    
    // 2. Начальное разбиение на финальные и нефинальные состояния
    unordered_set<int> finalStates;
    unordered_set<int> nonFinalStates;
    for (int state : reachable) {
        if (dfa.final_states.find(state) != dfa.final_states.end()) {
            finalStates.insert(state);
        } else {
            nonFinalStates.insert(state);
        }
    }
    
    vector<unordered_set<int>> partitions;
    if (!nonFinalStates.empty())
        partitions.push_back(move(nonFinalStates));
    if (!finalStates.empty())
        partitions.push_back(move(finalStates));
    
    // 3. Присвоение классов состояниям (индекс в partitions)
    vector<int> stateClass(dfa.num_states, -1);
    for (size_t i = 0; i < partitions.size(); ++i) {
        for (int state : partitions[i]) {
            stateClass[state] = i;
        }
    }
    
    // 4. Алгоритм Хопкрофта
    queue<pair<unordered_set<int>, char>> splitterQueue;
    const auto& smallerSet = (finalStates.size() <= nonFinalStates.size()) ? finalStates : nonFinalStates;
    for (char symbol : dfa.alphabet) {
        if (!smallerSet.empty())
            splitterQueue.push({smallerSet, symbol});
    }
    
    while (!splitterQueue.empty()) {
        auto [A, symbol] = move(splitterQueue.front());
        splitterQueue.pop();
        
        vector<pair<size_t, unordered_set<int>>> splits;
        for (size_t i = 0; i < partitions.size(); ++i) {
            unordered_map<int, unordered_set<int>> transitionClasses;
            for (int state : partitions[i]) {
                auto it = dfa.transitions.find({state, symbol});
                int targetClass = -1;
                if (it != dfa.transitions.end() && reachable.count(it->second)) {
                    targetClass = stateClass[it->second];
                }
                transitionClasses[targetClass].insert(state);
            }
            for (const auto& [targetClass, states] : transitionClasses) {
                if (!states.empty() && states.size() < partitions[i].size()) {
                    splits.push_back({i, move(states)});
                }
            }
        }
        
        for (auto& [idx, X] : splits) {
            unordered_set<int> Y;
            for (int state : partitions[idx]) {
                if (X.find(state) == X.end())
                    Y.insert(state);
            }
            partitions[idx] = move(X);
            partitions.push_back(move(Y));
            int newIndex = partitions.size() - 1;
            for (int state : partitions.back()) {
                stateClass[state] = newIndex;
            }
            const auto& smaller = (partitions[idx].size() <= partitions.back().size()) ? partitions[idx] : partitions.back();
            for (char a : dfa.alphabet) {
                splitterQueue.push({smaller, a});
            }
        }
    }
    
    // 5. Инициализация минимизированного DFA
    DFA minimizedDFA;
    minimizedDFA.alphabet = dfa.alphabet;
    minimizedDFA.num_states = partitions.size();
    
    // Формирование переходов
    for (const auto& [key, target] : dfa.transitions) {
        int oldState = key.first;
        char symbol = key.second;
        if (reachable.count(oldState) && reachable.count(target)) {
            int newState = stateClass[oldState];
            int newTarget = stateClass[target];
            if (newState != -1 && newTarget != -1) {
                minimizedDFA.transitions[{newState, symbol}] = newTarget;
            }
        }
    }
    
    // Установка нового начального состояния
    minimizedDFA.start_state = stateClass[dfa.start_state];
    
    // Установка новых финальных состояний
    for (int state : dfa.final_states) {
        if (reachable.count(state) && stateClass[state] != -1) {
            minimizedDFA.final_states.insert(stateClass[state]);
        }
    }
    
    // Перезапись DFA
    dfa = move(minimizedDFA);
}