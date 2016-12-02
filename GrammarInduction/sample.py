import networkx as nx
import random

def traverse(label, children):
    # print('traverse({})'.format(label))
    # print(children)
    if children == {}:
        # print('{} is terminal'.format(label))
        return [label]

    is_or = 'label' in children[children.keys()[0]][0]

    if is_or:
        # print('{} is or'.format(label))
        cumul_sum = 0.
        sampled_val = None
        r = random.random()
        for child_label, edges in children.items():
            for _, edge_prop in edges.items():
                weight = float(edge_prop['label'].replace('"', ''))
                cumul_sum += weight
                # print('cumul_sum', cumul_sum)
                if r < cumul_sum:
                    sampled_val = child_label
                    break
            if sampled_val is not None:
                break
        # print('r = {}. sampled {}'.format(r, sampled_val))
        return traverse(sampled_val, G[sampled_val])
    else:
        # print('{} is and'.format(label))
        sentence = []
        for child_label, child_props in children.items():
            sentence += traverse(child_label, G[child_label])
        return sentence


if __name__=='__main__':
    G = nx.drawing.nx_pydot.read_dot('grammar.dot')
    sentence = traverse('64', G['64'])
    print(sentence)
