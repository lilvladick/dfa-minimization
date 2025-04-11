#include "dfa.hpp"

using namespace std;

void DFA::console_input() {
    cout << "Enter the number of states: ";
    cin >> num_states;

    int alphabet_size;
    cout << "Enter the number of characters in the alphabet: ";
    cin >> alphabet_size;

    cout << "Enter the characters in the alphabet: ";
    for (int i = 0; i < alphabet_size; i++) {
        char c;
        cin >> c;
        alphabet.insert(c);
    }

    cout << "Enter the number of transitions: ";
    int num_transitions;
    cin >> num_transitions;

    cout << "Enter the transitions (state, input, next_state): ";
    for (int i = 0; i < num_transitions; i++) {
        int from, to;
        char input;
        cin >> from >> input >> to;
        transitions[{from, input}] = to;
    }

    cout << "Enter the starting state: ";
    cin >> start_state;

    int final_count;
    cout << "Enter the number of final states: ";
    cin >> final_count;

    cout << "Enter the final states: ";
    for (int i = 0; i < final_count; i++) {
        int state;
        cin >> state;
        final_states.insert(state);
    }
}

void DFA::print() {
    cout << "DFA: \n";
    cout << "Number of states: " << num_states << "\n";
    cout << "Alphabet: ";
    for (char c : alphabet) cout << c << " ";
    cout << "\nTransitions:\n";
    for (auto& t : transitions) {
        cout << "(" << t.first.first << ", " << t.first.second << ") -> " << t.second << "\n";
    }
    cout << "Start state: " << start_state << "\n";
    cout << "Final states: ";
    for (int state : final_states) cout << state << " ";
    cout << endl;
}
