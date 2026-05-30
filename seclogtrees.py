import re
from collections import defaultdict
from datetime import datetime
import graphviz

# -------------------------------
# Configuration
# -------------------------------

OUTPUT_DIR = #output directory for the graph created
OUTPUT_NAME = #name for the file for the graph created
LOG_FILE = #path for the seclogs you want to create the graphs for

# Known parent relationships in Linux boot chain
PARENT_MAP = {
    "kernel": None,
    "systemd": "kernel",
    "systemd-journald": "systemd",
    "systemd-udevd": "systemd",
    "systemd-networkd": "systemd",
    "systemd-resolved": "systemd",
    "rsyslogd": "systemd",
    "sshd": "systemd",
    "sudo": "systemd",
    "cron": "systemd",
    "dbus-daemon": "systemd",
    "NetworkManager": "systemd",
    "snapd": "systemd",
    "polkitd": "systemd",
    "accounts-daemon": "systemd",
}

# Event classification keywords
EVENT_COLORS = {
    "error":   "red",
    "denied":  "orange",
    "auth":    "purple",
    "started": "green",
    "starting":"lightblue",
    "other":   "gray"
}

# -------------------------------
# Parsing
# -------------------------------

LOG_PATTERN = re.compile(
    r'^(\w{3}\s+\d+\s+[\d:]+)\s+\S+\s+(\S+?)(?:\[(\d+)\])?:\s+(.*)$'
)

def parse_line(line):
    m = LOG_PATTERN.match(line.strip())
    if not m:
        return None
    timestamp_str, process, pid, message = m.groups()
    try:
        # Add a dummy year for parsing
        ts = datetime.strptime(f"2024 {timestamp_str.strip()}", "%Y %b %d %H:%M:%S")
    except ValueError:
        return None
    return ts, process, pid or "?", message

def classify_event(message):
    msg = message.lower()
    if "error" in msg or "failed" in msg:
        return "error"
    elif "denied" in msg:
        return "denied"
    elif "session opened" in msg or "authentication" in msg or "pam" in msg:
        return "auth"
    elif "started" in msg:
        return "started"
    elif "starting" in msg:
        return "starting"
    else:
        return "other"

# -------------------------------
# Data Collection
# -------------------------------

# nodes: key = (process, pid)
nodes = {}
# edges: key = (parent_process, child_process)
edges = defaultdict(lambda: {"count": 0, "event_types": defaultdict(int)})

def get_or_create_node(process, pid):
    key = (process, pid)
    if key not in nodes:
        nodes[key] = {
            "count": 0,
            "first_seen": None,
            "last_seen": None,
            "event_types": defaultdict(int),
            "pids": set()
        }
    return nodes[key]

def get_parent(process):
    return PARENT_MAP.get(process, "systemd")  # default parent is systemd

# -------------------------------
# Log Processing
# -------------------------------

with open(LOG_FILE, "r") as f:
    for line in f:
        parsed = parse_line(line)
        if not parsed:
            continue

        ts, process, pid, message = parsed
        event = classify_event(message)

        node = get_or_create_node(process, pid)
        node["count"] += 1
        node["pids"].add(pid)
        node["event_types"][event] += 1
        if node["first_seen"] is None:
            node["first_seen"] = ts
        node["last_seen"] = ts

        # Register edge from parent to this process
        parent = get_parent(process)
        if parent and parent != process:
            edge = edges[(parent, process)]
            edge["count"] += 1
            edge["event_types"][event] += 1

# -------------------------------
# Graph Rendering
# -------------------------------

dot = graphviz.Digraph(graph_attr={"rankdir": "TB", "splines": "ortho"})

for (process, pid), data in nodes.items():
    # Dominant event type for color
    dominant = max(data["event_types"], key=data["event_types"].get) if data["event_types"] else "other"
    color = EVENT_COLORS.get(dominant, "gray")

    first = data["first_seen"].strftime("%H:%M:%S") if data["first_seen"] else "?"
    last  = data["last_seen"].strftime("%H:%M:%S")  if data["last_seen"]  else "?"

    label = (
        f"{process}\n"
        f"PID(s): {pid}\n"
        f"Events: {data['count']}\n"
        f"{first} → {last}"
    )

    dot.node(
        f"{process}_{pid}",
        label=label,
        style="filled",
        fillcolor=color,
        fontcolor="white",
        shape="box"
    )

for (parent, child), data in edges.items():
    # Find representative child node key
    child_keys = [k for k in nodes if k[0] == child]
    parent_keys = [k for k in nodes if k[0] == parent]

    for pk in parent_keys:
        for ck in child_keys:
            dominant = max(data["event_types"], key=data["event_types"].get) if data["event_types"] else "other"
            color = EVENT_COLORS.get(dominant, "black")
            dot.edge(
                f"{pk[0]}_{pk[1]}",
                f"{ck[0]}_{ck[1]}",
                label=str(data["count"]),
                color=color
            )

output_path = dot.render(
    filename=OUTPUT_NAME,
    directory=OUTPUT_DIR,
    format="png",
    cleanup=True
)

print(f"Process tree saved to: {output_path}")