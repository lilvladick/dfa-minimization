#include "minimize.hpp"
#include <iostream>
#include <map>
#include <set>
#include <vector>
#include <queue>
#include <algorithm>

void minimize_dfa(DFA& dfa) {
    // === Удаление недостижимых состояний и мёртвых состояний ===
    std::set<int> reachable;
    std::queue<int> q;
    q.push(dfa.start_state);
    reachable.insert(dfa.start_state);

    while (!q.empty()) {
        int current = q.front(); q.pop();
        for (char c : dfa.alphabet) {
            auto it = dfa.transitions.find({current, c});
            if (it != dfa.transitions.end()) {
                int next = it->second;
                if (!reachable.count(next)) {
                    reachable.insert(next);
                    q.push(next);
                }
            }
        }
    }

    std::map<int, std::vector<int>> reverse_graph;
    for (auto& [key, to] : dfa.transitions) {
        reverse_graph[to].push_back(key.first);
    }

    std::set<int> can_reach_final;
    std::queue<int> q2;
    for (int f : dfa.final_states) {
        q2.push(f);
        can_reach_final.insert(f);
    }

    while (!q2.empty()) {
        int current = q2.front(); q2.pop();
        for (int from : reverse_graph[current]) {
            if (!can_reach_final.count(from)) {
                can_reach_final.insert(from);
                q2.push(from);
            }
        }
    }

    std::set<int> useful_states;
    for (int s : reachable) {
        if (can_reach_final.count(s)) {
            useful_states.insert(s);
        }
    }

    std::map<std::pair<int, char>, int> filtered_transitions;
    for (auto& [key, to] : dfa.transitions) {
        int from = key.first;
        if (useful_states.count(from) && useful_states.count(to)) {
            filtered_transitions[key] = to;
        }
    }

    dfa.transitions = filtered_transitions;
    dfa.final_states = [&]() {
        std::set<int> fs;
        for (int f : dfa.final_states) {
            if (useful_states.count(f)) fs.insert(f);
        }
        return fs;
    }();
    dfa.num_states = useful_states.size();

    // === минимизация Хопкрофтом ===

    std::vector<std::set<int>> partitions;
    std::map<int, int> state_class;

    std::set<int> final, non_final;
    for (int s : useful_states) {
        if (dfa.final_states.count(s)) final.insert(s);
        else non_final.insert(s);
    }

    if (!final.empty()) partitions.push_back(final);
    if (!non_final.empty()) partitions.push_back(non_final);

    for (size_t i = 0; i < partitions.size(); ++i) {
        for (int state : partitions[i]) {
            state_class[state] = i;
        }
    }

    std::map<int, std::map<char, std::set<int>>> rev_transitions;
    for (auto& [key, to] : dfa.transitions) {
        int from = key.first;
        char symbol = key.second;
        rev_transitions[to][symbol].insert(from);
    }

    std::set<int> worklist;
    for (size_t i = 0; i < partitions.size(); ++i) worklist.insert(i);

    while (!worklist.empty()) {
        int A_index = *worklist.begin();
        worklist.erase(worklist.begin());
        std::set<int> A = partitions[A_index];

        for (char symbol : dfa.alphabet) {
            std::set<int> X;
            for (int state_in_A : A) {
                auto rev_state_it = rev_transitions.find(state_in_A);
                if (rev_state_it != rev_transitions.end()) {
                    auto symbol_it = rev_state_it->second.find(symbol);
                    if (symbol_it != rev_state_it->second.end()) {
                        X.insert(symbol_it->second.begin(), symbol_it->second.end());
                    }
                }
            }

            for (size_t i = 0; i < partitions.size(); ++i) {
                std::set<int> Y = partitions[i];
                std::set<int> intersect, diff;
                for (int state : Y) {
                    if (X.count(state)) intersect.insert(state);
                    else diff.insert(state);
                }

                if (!intersect.empty() && !diff.empty()) {
                    partitions[i] = intersect;
                    partitions.push_back(diff);
                    int new_index = partitions.size() - 1;

                    for (int state : partitions[new_index]) {
                        state_class[state] = new_index;
                    }

                    if (worklist.count(i)) {
                        worklist.insert(new_index);
                    } else {
                        if (intersect.size() <= diff.size()) {
                            worklist.insert(i);
                        } else {
                            worklist.insert(new_index);
                        }
                    }
                }
            }
        }
    }

    DFA minimized;
    minimized.num_states = partitions.size();
    minimized.alphabet = dfa.alphabet;

    std::map<std::pair<int, char>, int> new_trans;
    std::set<int> new_final_states;

    for (size_t i = 0; i < partitions.size(); ++i) {
        int representative = *partitions[i].begin();
        for (char c : dfa.alphabet) {
            auto it = dfa.transitions.find({representative, c});
            if (it != dfa.transitions.end()) {
                int dest = it->second;
                int from_class = i;
                int to_class = state_class[dest];
                new_trans[{from_class, c}] = to_class;
            }
        }

        for (int state : partitions[i]) {
            if (dfa.final_states.count(state)) {
                new_final_states.insert(i);
                break;
            }
        }
    }

    minimized.transitions = new_trans;
    minimized.start_state = state_class[dfa.start_state];
    minimized.final_states = new_final_states;

    dfa = minimized;
}
