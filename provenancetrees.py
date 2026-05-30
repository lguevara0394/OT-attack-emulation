import os
import json
import networkx as nx
import matplotlib.pyplot as plt
import textwrap

file_path = #path to the json you want to create the graphs for

TACTIC_COLORS = {
    "discovery":      "#1f77b4",
    "collection":     "#ff7f0e",
    "execution":      "#2ca02c",
    "persistence":    "#d62728",
    "privilege-escalation": "#9467bd",
    "defense-evasion": "#8c564b",
    "credential-access": "#e377c2",
    "lateral-movement": "#7f7f7f",
    "command-and-control": "#bcbd22",
    "impact": "#17becf",
    "unknown": "#664A44",
}

default_color = "#cccccc"

# Dictionary: version → graph
graphs_by_version = {}

# ----------------------------------------------
# BUILD ALL GRAPHS (one per attack_version)
# ----------------------------------------------

for fname in os.listdir(file_path):
    if fname.endswith("Modbus_test2_event-logs.json"):
        full_path = os.path.join(file_path, fname)

        with open(full_path, "r") as f:
            events = json.load(f)

        for event in events:

            # Extract version, default to "unknown"
            version = event.get("attack_metadata", {}).get("attack_version", "unknown")

            # Create graph if it doesn't exist yet
            if version not in graphs_by_version:
                graphs_by_version[version] = nx.DiGraph()

            G = graphs_by_version[version]

            # Extract tactic
            tactic = event.get("attack_metadata", {}).get("tactic", "unknown")

            # Activity node
            activity = event["ability_metadata"]["ability_name"]
            G.add_node(activity, type="activity", tactic=tactic)

            # Used entities
            if "plaintext_command" in event:
                cmd = event["plaintext_command"]
                G.add_node(cmd, type="entity", tactic=tactic)
                G.add_edge(cmd, activity, relation="used")

            # Output generated
            output = event.get("command")
            if output:
                G.add_node(output, type="entity", tactic=tactic)
                G.add_edge(activity, output, relation="generated")

            # Ability description
            desc = event["ability_metadata"].get("ability_description")
            if desc:
                G.add_node(desc, type="entity", tactic=tactic)
                G.add_edge(activity, desc, relation="generated")


# ----------------------------------------------
# PLOTTING: Circular layout for each version
# ----------------------------------------------

def wrap(text, width=20):
    return "\n".join(textwrap.wrap(text, width=width))

for version, G in graphs_by_version.items():

    print(f"Rendering circular graph for ATT&CK version: {version}")

    # Use circular layout
    pos = nx.circular_layout(G)

    # Prepare node colors
    node_colors = [
        TACTIC_COLORS.get(data.get("tactic", "unknown"), default_color)
        for _, data in G.nodes(data=True)
    ]

    # Labels
    labels = {n: wrap(n, 20) for n in G.nodes()}

    plt.figure(figsize=(12, 12))
    plt.title(f"ATT&CK Version {version} — Circular Graph", fontsize=16)

    nx.draw(
        G,
        pos,
        labels=labels,
        node_color=node_colors,
        node_size=1600,
        edgecolors="black",
        font_size=10,
        linewidths=0.5,
    )

    # Draw edge labels if desired (can remove for cleaner visuals)
    edge_labels = {
        e: wrap(lbl, 10)
        for e, lbl in nx.get_edge_attributes(G, "relation").items()
    }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    plt.axis("off")
    plt.show()