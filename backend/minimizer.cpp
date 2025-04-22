#include "minimize.hpp"
#include "dfa.hpp"
#include <iostream>
#include <string>
#include <nlohmann/json.hpp> //(https://github.com/nlohmann/json)

using json = nlohmann::json;

int main() {
    std::string input;
    std::string line;
    while (std::getline(std::cin, line)) {
        input += line;
    }

    try {
        json j = json::parse(input);
        DFA dfa;
        dfa.num_states = j["num_states"];
        for (const auto& sym : j["alphabet"]) {
            std::string s = sym.get<std::string>();
            if (s.empty()) continue;
            dfa.alphabet.insert(s[0]);
        }
        for (const auto& t : j["transitions"]) {
            int from = t["from"];
            std::string input = t["input"].get<std::string>();
            int to = t["to"];
            if (!input.empty()) {
                dfa.transitions[{from, input[0]}] = to;
            }
        }
        dfa.start_state = j["start_state"];
        for (const auto& f : j["final_states"]) {
            dfa.final_states.insert(f.get<int>());
        }
        minimize_dfa(dfa);
        json output;
        output["num_states"] = dfa.num_states;
        output["alphabet"] = std::vector<std::string>();
        for (char c : dfa.alphabet) {
            output["alphabet"].push_back(std::string(1, c));
        }
        output["transitions"] = json::array();
        for (const auto& t : dfa.transitions) {
            int from = t.first.first;
            char input = t.first.second;
            int to = t.second;
            output["transitions"].push_back({
                {"from", from},
                {"input", std::string(1, input)},
                {"to", to}
            });
        }
        output["start_state"] = dfa.start_state;
        output["final_states"] = std::vector<int>(dfa.final_states.begin(), dfa.final_states.end());

        std::cout << output.dump() << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}