#include "minimize.hpp"


using namespace std;

void minimizeDFA(DFA& dfa) {
    // To find reachable states use BFS
    set<int> reachable;
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
                if (reachable.find(next) == reachable.end()) {
                    reachable.insert(next);
                    q.push(next);
                }
            }
        }
    }
    
    // Leave reachable states
    vector<int> reachableStates(reachable.begin(), reachable.end());
    
    // Initial split table into 1 and 2 groups, where 1 is final and 2 is not
    set<int> finalStates;
    set<int> nonFinalStates;
    for (int state : reachableStates) {
        if (dfa.final_states.find(state) != dfa.final_states.end()) {
            finalStates.insert(state);
        } else {
            nonFinalStates.insert(state);
        }
    }
    
    vector<set<int>> partitions;
    if (!nonFinalStates.empty())
        partitions.push_back(nonFinalStates);
    if (!finalStates.empty())
        partitions.push_back(finalStates);
    
    // Assign each state a class (index in partitions)
    int maxState = 0;
    for (int state : reachableStates)
        if (state > maxState) maxState = state;
    vector<int> stateClass(maxState + 1, -1);
    for (int i = 0; i < partitions.size(); i++) {
        for (int state : partitions[i]) {
            stateClass[state] = i;
        }
    }
    
    // Hopcroft's algorithm
    queue<pair<set<int>, char>> splitterQueue;
    for (char symbol : dfa.alphabet) {
        if (!finalStates.empty())
            splitterQueue.push({finalStates, symbol});
    }
    
    while (!splitterQueue.empty()) {
        auto [A, symbol] = splitterQueue.front();
        splitterQueue.pop();
        
        vector<pair<int, set<int>>> splits;
        for (int i = 0; i < partitions.size(); i++) {
            set<int> X;
            for (int state : partitions[i]) {
                auto it = dfa.transitions.find({state, symbol});
                if (it != dfa.transitions.end() && A.find(it->second) != A.end()) {
                    X.insert(state);
                }
            }
            if (!X.empty() && X.size() < partitions[i].size()) {
                splits.push_back({i, X});
            }
        }
        
        for (auto& [idx, X] : splits) {
            set<int> Y;
            for (int state : partitions[idx]) {
                if (X.find(state) == X.end())
                    Y.insert(state);
            }
            partitions[idx] = X;
            partitions.push_back(Y);
            int newIndex = partitions.size() - 1;
            for (int state : Y) {
                stateClass[state] = newIndex;
            }
            for (char a : dfa.alphabet) {
                splitterQueue.push({X, a});
                splitterQueue.push({Y, a});
            }
        }
    }
    
    // Initialize minimized DFA
    DFA minimizedDFA;
    minimizedDFA.alphabet = dfa.alphabet;
    minimizedDFA.num_states = partitions.size();
    
    // Form transitions
    for (auto &transition : dfa.transitions) {
        int oldState = transition.first.first;
        char symbol = transition.first.second;
        int oldTarget = transition.second;

        // Add if both states are reachable
        if (reachable.find(oldState) != reachable.end() && reachable.find(oldTarget) != reachable.end()) {
            int newState = stateClass[oldState];
            int newTarget = stateClass[oldTarget];
            minimizedDFA.transitions[{newState, symbol}] = newTarget;
        }
    }
    
    // Initialize new start state
    minimizedDFA.start_state = stateClass[dfa.start_state];
    
    // initialize new final states
    for (int state : dfa.final_states) {
        // Add if both states are reachable
        if (reachable.find(state) != reachable.end())
            minimizedDFA.final_states.insert(stateClass[state]);
    }
    
    // Rewrite DFA
    dfa = minimizedDFA;
    
    cout << "Minimization Complete!\n";
}
