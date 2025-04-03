#include <iostream>
#include "dfa.hpp"
#include "minimize.hpp"

using namespace std;


int main() {
    DFA dfa;
    dfa.console_input();
    dfa.print();

    minimizeDFA(dfa);
    dfa.print();

    return 0;
}