import re
from collections import defaultdict
from datetime import datetime
import graphviz

# -------------------------------
# Configuration
# -------------------------------

OUTPUT_DIR = #output path for your graph
OUTPUT_NAME = #name of the file for the graph
LOG_FILE = #path to your syslogs files

# Known parent relationships — expanded to cover processes found in this log
PARENT_MAP = {
    "kernel":                   None,
    "systemd":                  "kernel",
    "systemd-journald":         "systemd",
    "systemd-udevd":            "systemd",
    "systemd-networkd":         "systemd",
    "systemd-resolved":         "systemd",
    "systemd-logind":           "systemd",
    "systemd-timesyncd":        "systemd",
    "systemd-tmpfiles":         "systemd",
    "systemd-modules-load":     "systemd",
    "systemd-fsck":             "systemd",
    "systemd-shutdown":         "systemd",
    "rsyslogd":                 "systemd",
    "sshd":                     "systemd",
    "sudo":                     "systemd",
    "cron":                     "systemd",
    "CRON":                     "systemd",
    "anacron":                  "systemd",
    "dbus-daemon":              "systemd",
    "NetworkManager":           "systemd",
    "snapd":                    "systemd",
    "snapd-apparmor":           "systemd",
    "polkitd":                  "systemd",
    "accounts-daemon":          "systemd",
    "avahi-daemon":             "systemd",
    "rtkit-daemon":             "systemd",
    "dnsmasq":                  "systemd",
    "dnsmasq-dhcp":             "dnsmasq",
    "sddm":                     "systemd",
    "sddm-greeter":             "sddm",
    "sddm-helper":              "sddm",
    "wpa_supplicant":           "systemd",
    "ModemManager":             "systemd",
    "PackageKit":               "systemd",
    "packagekitd":              "systemd",
    "polkitd":                  "systemd",
    "udisksd":                  "systemd",
    "fwupd":                    "systemd",
    "fwupdmgr":                 "fwupd",
    "libvirtd":                 "systemd",
    "lxd.daemon":               "systemd",
    "lxd.activate":             "systemd",
    "multipathd":               "systemd",
    "whoopsie":                 "systemd",
    "cloud-init":               "systemd",
    "pipewire":                 "systemd",
    "wireplumber":              "systemd",
    "spice-vdagent":            "systemd",
    "cups-browsed":             "systemd",
    "login":                    "systemd",
    "su":                       "systemd",
    "passwd":                   "systemd",
    "useradd":                  "systemd",
    "usermod":                  "systemd",
    "adduser":                  "systemd",
    "addgroup":                 "systemd",
    "groupadd":                 "systemd",
    "chfn":                     "systemd",
    "obexd":                    "systemd",
    "gnome-keyring-daemon":     "systemd",
    "pollinate":                "systemd",
    "udevadm":                  "systemd-udevd",
    "alsactl":                  "systemd",
    "sensors":                  "systemd",
    "apparmor.systemd":         "systemd",
    "apt.systemd.daily":        "systemd",
    "apt-helper":               "systemd",
    "lvm":                      "systemd",
    "blkdeactivate":            "systemd",
    "finalrd":                  "systemd",
    "mtp-probe":                "systemd",
    "kscreen_backend_launcher": "systemd",
    "xdg-document-portal":      "systemd",
    "gvfsd-network":            "systemd",
    "gvfsd-wsdd":               "systemd",
    "io.snapcraft.Settings":    "snapd",
    "org.kde.kcookiejar5":      "systemd",
    "org.freedesktop.impl.portal.desktop.lxqt": "systemd",
    "libvirt-guests.sh":        "libvirtd",
    "dbus-send":                "dbus-daemon",
    "unknown":                  "systemd",
}

# Event classification keywords
EVENT_COLORS = {
    "error":    "#d32f2f",   # deep red
    "denied":   "#e65100",   # deep orange
    "auth":     "#6a1b9a",   # purple
    "started":  "#2e7d32",   # dark green
    "starting": "#1565c0",   # dark blue
    "other":    "#546e7a",   # blue-grey
}

EVENT_LABELS = {
    "error":    "Error/Failed",
    "denied":   "Denied",
    "auth":     "Auth/PAM",
    "started":  "Started",
    "starting": "Starting",
    "other":    "Other",
}

# -------------------------------
# Parsing  — matches syslog format:
#   Apr 20 17:54:31 hostname process[pid]: message
#   Apr 20 17:54:31 hostname process: message   (no pid)
# -------------------------------

# Matches ISO 8601 format: 2026-05-12T00:00:42.319275+00:00 hostname process[pid]: message
LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'  # timestamp (up to seconds)
    r'[\d.+:Z]*\s+'                              # fractional seconds + timezone offset
    r'\S+\s+'                                    # hostname (skip)
    r'(\S+?)(?:\[(\d+)\])?:\s+'                  # process + optional [pid]
    r'(.*)$'                                     # message
)

def parse_line(line):
    m = LOG_PATTERN.match(line.strip())
    if not m:
        return None
    timestamp_str, process, pid, message = m.groups()
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return ts, process.strip(), pid or "?", message

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

# Key: process name (no pid) — we collapse all PIDs of same process into one node
nodes = {}
# Key: (parent_process_name, child_process_name)
edges = defaultdict(lambda: {"count": 0, "event_types": defaultdict(int)})

def get_or_create_node(process):
    if process not in nodes:
        nodes[process] = {
            "count": 0,
            "first_seen": None,
            "last_seen": None,
            "event_types": defaultdict(int),
            "pids": set()
        }
    return nodes[process]

def get_parent(process):
    return PARENT_MAP.get(process, "systemd")  # default parent is systemd

# -------------------------------
# Log Processing
# -------------------------------

print(f"Reading {LOG_FILE} ...")
line_count = 0
parsed_count = 0

with open(LOG_FILE, "r", errors="replace") as f:
    for line in f:
        line_count += 1
        parsed = parse_line(line)
        if not parsed:
            continue
        parsed_count += 1

        ts, process, pid, message = parsed
        event = classify_event(message)

        node = get_or_create_node(process)
        node["count"] += 1
        node["pids"].add(pid)
        node["event_types"][event] += 1
        if node["first_seen"] is None:
            node["first_seen"] = ts
        node["last_seen"] = ts

        # Register edge from parent to this process
        parent = get_parent(process)
        if parent and parent != process:
            # Make sure parent node exists too
            get_or_create_node(parent)
            edge = edges[(parent, process)]
            edge["count"] += 1
            edge["event_types"][event] += 1

print(f"Lines read: {line_count:,}  |  Parsed: {parsed_count:,}  |  Unique processes: {len(nodes)}")

# -------------------------------
# Graph Rendering
# -------------------------------

dot = graphviz.Digraph(
    graph_attr={
        "rankdir":  "TB",
        "splines":  "polyline",
        "bgcolor":  "#1a1a2e",        # dark navy background
        "fontname": "Helvetica",
        "pad":      "0.5",
        "nodesep":  "0.4",
        "ranksep":  "0.7",
    },
    node_attr={
        "fontname": "Helvetica",
        "fontsize": "10",
        "penwidth": "1.5",
    },
    edge_attr={
        "fontname": "Helvetica",
        "fontsize": "9",
        "penwidth": "1.2",
        "arrowsize": "0.7",
    }
)

# Legend subgraph
with dot.subgraph(name="cluster_legend") as leg:
    leg.attr(
        label="Event Type Legend",
        style="filled",
        fillcolor="#16213e",
        fontcolor="white",
        fontsize="11",
        fontname="Helvetica Bold",
        color="#4a4e69",
        penwidth="1.5",
    )
    for etype, color in EVENT_COLORS.items():
        leg.node(
            f"_legend_{etype}",
            label=EVENT_LABELS[etype],
            style="filled",
            fillcolor=color,
            fontcolor="white",
            shape="box",
            width="1.6",
            height="0.4",
        )

for process, data in nodes.items():
    dominant = (
        max(data["event_types"], key=data["event_types"].get)
        if data["event_types"] else "other"
    )
    fill_color = EVENT_COLORS.get(dominant, "#546e7a")

    first = data["first_seen"].strftime("%H:%M:%S") if data["first_seen"] else "?"
    last  = data["last_seen"].strftime("%H:%M:%S")  if data["last_seen"]  else "?"

    pid_sample = sorted(data["pids"])[:3]
    pid_str = ", ".join(str(p) for p in pid_sample)
    if len(data["pids"]) > 3:
        pid_str += f" (+{len(data['pids'])-3})"

    label = (
        f"{process}\n"
        f"PIDs: {pid_str}\n"
        f"Events: {data['count']}\n"
        f"{first} → {last}"
    )

    dot.node(
        process,
        label=label,
        style="filled",
        fillcolor=fill_color,
        fontcolor="white",
        shape="box",
        color="white",
    )

for (parent, child), data in edges.items():
    dominant = (
        max(data["event_types"], key=data["event_types"].get)
        if data["event_types"] else "other"
    )
    edge_color = EVENT_COLORS.get(dominant, "#90a4ae")

    dot.edge(
        parent,
        child,
        label=str(data["count"]),
        color=edge_color,
        fontcolor="#eceff1",
    )

output_path = dot.render(
    filename=OUTPUT_NAME,
    directory=OUTPUT_DIR,
    format="png",
    cleanup=True,
)

print(f"Process tree saved to: {output_path}")