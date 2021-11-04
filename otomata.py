import matplotlib.pyplot as plt
import networkx as nx
from sys import exit

directedGraph = nx.DiGraph()
directedGraph.add_edge(1, 2, label='|')


class Transition:
    def __init__(self, v1, v2, symbol) -> None:
        self.state_from = v1
        self.state_to = v2
        self.transition_symbol = symbol


class NFA:
    def __init__(self, *args) -> None:
        self.states = []
        self.transitions = []
        self.final_state = 0
        if len(args) == 1:
            if isinstance(args[0], int):
                self.setStateSize(args[0])
            elif isinstance(args[0], str):
                self.setStateSize(2)
                self.final_state = 1
                self.transitions.append(Transition(0, 1, args[0]))

    def setStateSize(self, size: int) -> None:
        for i in range(size):
            self.states.append(i)

    def display(self) -> None:
        t: Transition
        print("Final State: " + str(self.final_state))
        for t in self.transitions:
            print("(" + str(t.state_from) + ", \'" +
                  str(t.transition_symbol) + "\', " + str(t.state_to) + ")")


def kleene(n: NFA) -> NFA:
    result: NFA = NFA(len(n.states)+2)
    result.transitions.append(Transition(0, 1, 'E'))
    t: Transition
    for t in n.transitions:
        result.transitions.append(Transition(
            t.state_from+1, t.state_to+1, t.transition_symbol))
    result.transitions.append(Transition(len(n.states), len(n.states)+1, 'E'))
    result.transitions.append(Transition(len(n.states), 1, 'E'))
    result.transitions.append(Transition(0, len(n.states)+1, 'E'))
    result.final_state = len(n.states) + 1
    return result


def concat(n: NFA, m: NFA) -> NFA:
    m.states.remove(0)
    t: Transition
    for t in m.transitions:
        n.transitions.append(Transition(t.state_from + len(n.states) - 1,
                             t.state_to + len(n.states) - 1, t.transition_symbol))
    s: int
    for s in m.states:
        n.states.append(s+len(n.states) + 1)
    n.final_state = len(n.states) + len(m.states) - 2
    return n


def union(n: NFA, m: NFA) -> NFA:
    result = NFA(len(n.states) + len(m.states) + 2)
    result.transitions.append(Transition(0, 1, 'E'))
    t: Transition
    for t in n.transitions:
        result.transitions.append(Transition(
            t.state_from+1, t.state_to+1, t.transition_symbol))
    result.transitions.append(Transition(
        len(n.states), len(n.states)+len(m.states)+1, 'E'))
    for t in m.transitions:
        result.transitions.append(Transition(
            t.state_from + len(n.states) + 1, t.state_to + len(n.states) + 1, t.transition_symbol))
    result.transitions.append(Transition(
        len(m.states) + len(n.states), len(m.states) + len(n.states)+1, 'E'))
    result.final_state = len(n.states) + len(m.states) + 1
    return result


def alpha(ch: str) -> bool:
    return ch >= 'a' and ch <= 'z'


def alphabet(ch: str) -> bool:
    return alpha(ch) or (ch == "E")


def regexOp(ch: str) -> bool:
    return (ch == "(") or (ch == ")") or (ch == "*") or (ch == "|")


def regexChar(ch: str) -> bool:
    return alphabet(ch) or regexOp(ch)


def validRegex(regex: str) -> bool:
    if not regex:
        return False
    for ch in regex:
        if not regexChar(ch):
            return False
    return True


def compile(regex: str) -> NFA:
    if not validRegex(regex):
        print("Invalid Regular Expression Input")
        n = NFA("E")
        return n
    operators = []
    operands = []
    concat_stack = []

    concat_flag = False
    op: str
    c: str
    para_count = 0
    nfa1 = NFA()
    nfa2 = NFA()

    for c in regex:
        if alphabet(c):
            operands.append(NFA(c))
            if concat_flag:
                operators.append('.')
            else:
                concat_flag = True
        else:
            if c == ')':
                concat_flag = False
                if para_count == 0:
                    print("Unmatched Brackets")
                    exit(1)
                else:
                    para_count -= 1
                while(len(operators) > 0 and (operators[-1] != '(')):
                    op = operators.pop()
                    if op == '.':
                        nfa2 = operands.pop()
                        nfa1 = operands.pop()
                        operands.append(concat(nfa1, nfa2))
                    elif op == '|':
                        nfa2 = operands.pop()
                        if len(operators) > 0 and (operators[-1] == '.'):
                            concat_stack.append(operands.pop())
                            while len(operators) > 0 and (operators[-1] == '.'):
                                concat_stack.append(operands.pop())
                                operators.pop()
                            nfa1 = concat(concat_stack.pop(),
                                          concat_stack.pop())
                            while len(concat_stack) > 0:
                                nfa1 = concat(nfa1, concat_stack.pop())
                        else:
                            nfa1 = operands.pop()
                        operands.append(union(nfa1, nfa2))
            elif c == '*':
                operands.append(kleene(operands.pop()))
                concat_flag = True
            elif c == '(':
                operators.append(c)
                para_count += 1
            elif c == '|':
                operators.append(c)
                concat_flag = False
    while len(operators) > 0:
        if not operands:
            print("Operators Operands imbalance")
            exit(1)
        op = operators.pop()
        if op == '.':
            nfa2 = operands.pop()
            nfa1 = operands.pop()
            operands.append(concat(nfa1, nfa2))
        elif op == '|':
            nfa2 = operands.pop()
            if(len(operators) > 0 and operators[-1] == '.'):
                concat_stack.append(operands.pop())
                while (len(operators) > 0 and operators[-1] == '.'):
                    concat_stack.append(operands.pop())
                    operators.pop()
                nfa1 = concat(concat_stack.pop(), concat_stack.pop())
                while(len(concat_stack) > 0):
                    nfa1 = concat(nfa1, concat_stack.pop())
            else:
                nfa1 = operands.pop()
            operands.append(union(nfa1, nfa2))
    return operands.pop()


def nfaGraph(n: NFA):
    g = nx.DiGraph()
    t: Transition
    for t in n.transitions:
        g.add_edge(t.state_from, t.state_to, label=t.transition_symbol)
    return g


line = ""
while(True):
    print("Enter Regular Expression")
    line = input()
    if(line == ":q"):
        exit(0)
    nfa_input = compile(line)
    print("NFA:")
    nfa_input.display()
    g = nfaGraph(nfa_input)
    pos = nx.spring_layout(g)
    color_map = ['green' if node ==
                 nfa_input.final_state else 'blue' for node in g]
    nx.draw_networkx(g, pos, with_labels=True, node_color=color_map)
    edge_labels = dict([((n1, n2), d['label'])
                       for n1, n2, d in g.edges(data=True)])
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, label_pos=0.9,
                                 font_color='red', font_size=16, font_weight='bold')
    plt.show()
