#ifndef DFA_HPP
#define DFA_HPP

#include <iostream>
#include <vector>
#include <map>
#include <set>

class DFA {
public:
    int num_states;
    std::set<char> alphabet;
    std::map<std::pair<int, char>, int> transitions;
    int start_state;
    std::set<int> final_states;

    void console_input();
    void print();
};

#endif
