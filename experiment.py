import networkx as nx
import matplotlib.pyplot as plt

date = 1
current_balance = 10
pantry = set()
will_be_ready = {}

state_graph_edges = {}
state_graph_nodes = {}
state_graph = nx.DiGraph()

priorities = {"C": 2}

outputs = {
    "R1": "B",
    "R2": "C",
    "R3": "E"
}
recipe_for = {v: [k] for k, v in outputs.items()}
# todo: eventually multiple recipes will make the same thing so this won't work generically


inputs = {
    "R1": [("A", 1)],
    "R2": [("B", 1)],
    "R3": [("B", 1), ("D", 2)]
}

costs = {
    "R1": 2,
    "R2": 5,
    "R3": 10
}

creators = {"A": 3, "D": 1}
customers = {"E": 8, "C": 4, "B": 3}

while date < 30:
    print(state_graph_nodes)

    print(f"DATE: {date}")
    print("current_balance", current_balance)
    print(f"pantry = {sorted(list(pantry))}")
    print(f"cook finishes = {will_be_ready}")

    fig, ax = plt.subplots()
    nx.draw(state_graph, with_labels=True)
    ax.set_title(date)
    plt.show()

    # simulate creators
    for ingredient, frequency in creators.items():
        if date % frequency == 0:
            for i in range(frequency):
                pantry.add((ingredient, date-i))

    # simulate orders
    for ingredient, frequency in customers.items():
        if date % frequency == 0:
            state_graph_nodes[(ingredient, date)] = "ordered"
            state_graph.add_node((ingredient, date))

    # do the magic
    new_nodes = {}
    for (ingredient, i), state in state_graph_nodes.items():
        if state == "ordered":
            chosen_recipe = recipe_for[ingredient][0]
            for (input_ingredient, delta) in inputs.get(chosen_recipe, []):
                for d in range(delta+1):
                    this_input = (input_ingredient, i - d)
                    if this_input not in pantry and this_input not in state_graph_nodes:
                        new_nodes[this_input] = "needed"
                        state_graph.add_node(this_input)
                    state_graph.add_edge(this_input, (ingredient, i))
    state_graph_nodes.update(new_nodes)

    # add all the dependent nodes
    while True:
        update = False
        new_nodes = {}
        for (ingredient, i), state in state_graph_nodes.items():
            if state == "needed" and state_graph.in_degree[(ingredient, i)] == 0 and ingredient in recipe_for:
                update = True
                chosen_recipe = recipe_for[ingredient][0]
                for (input_ingredient, delta) in inputs[chosen_recipe]:
                    for d in range(delta+1):
                        this_input = (input_ingredient, i - d)
                        if this_input not in pantry and this_input not in state_graph_nodes:
                            new_nodes[this_input] = "needed"
                            state_graph.add_node(this_input)
                        state_graph.add_edge(this_input, (ingredient, i))
        state_graph_nodes.update(new_nodes)
        if not update:
            break

    # clean all nodes that are in the pantry
    met_requirements = {}
    for (ingredient, i) in state_graph.nodes():
        if (ingredient, i) in pantry:
            for dependent_node in list(state_graph.successors((ingredient, i))):
                if dependent_node in met_requirements:
                    met_requirements[dependent_node].add(ingredient)
                else:
                    met_requirements[dependent_node] = {ingredient}
    nodes_to_remove = []
    for node, met_set in met_requirements.items():
        for input_node in state_graph.predecessors(node):
            if input_node[0] in met_set:
                nodes_to_remove.append(input_node)
    for input_node in nodes_to_remove:
        if input_node in state_graph.nodes:
            state_graph.remove_node(input_node)
        if input_node in state_graph_nodes:
            del state_graph_nodes[input_node]

    # NOW CHOOSE WHAT TO COOK
    ready_to_cook_nodes = [node for node in state_graph.nodes if state_graph.in_degree[node] == 0]
    ready_to_cook_nodes.sort(key=lambda node: (priorities.get(node[0], 1), state_graph.out_degree[node]))

    for node in ready_to_cook_nodes[::-1]:
        if current_balance > 0 and node not in will_be_ready:
            if node[0] in recipe_for:
                chosen_recipe = recipe_for[node[0]][0]
                current_balance -= costs[chosen_recipe]
                state_graph_nodes[node] = "cooking"
                will_be_ready[node] = date + costs[chosen_recipe]

    # simulate items getting cooked
    for (ingredient, i), ready_date in will_be_ready.items():
        if ready_date == date:
            if (ingredient, i) in state_graph_nodes:
                del state_graph_nodes[(ingredient, i)]
            if (ingredient, i) in state_graph.nodes:
                state_graph.remove_node((ingredient, i))
            pantry.add((ingredient, i))
            chosen_recipe = recipe_for[ingredient][0]
            current_balance += costs[chosen_recipe]

    # clean up the will be ready list
    will_be_ready = {k: v for k, v in will_be_ready.items() if v > date}

    print("-"*80)
    date += 1


# todo: if an input is satisfied by something already cooking... don't schedule a different input anyway
# todo: satisfy the scheduling with repeats problem... schedule collections (like the F-corona modeling repeat problem)
