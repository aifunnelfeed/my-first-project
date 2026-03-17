#!/usr/bin/env python3
"""
Agent Visualizer — state updater.

Usage:
  python viz/update.py --system copycraft --state RESEARCH
  python viz/update.py --system copycraft --agent A --status working --label "Сбор VOC..."
  python viz/update.py --system copycraft --agent A --status done --label "47 цитат"
  python viz/update.py --system research --state COLLECTION --agent B --status working
  python viz/update.py --system copycraft --project nutriciologia
  python viz/update.py --system copycraft --phase "PHASE C — COPY"
  python viz/update.py --reset
"""

import argparse
import json
import os
import ssl
import urllib.request
import urllib.error
from datetime import datetime

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
FIREBASE_URL = "https://copycraft-aef75-default-rtdb.asia-southeast1.firebasedatabase.app"

DEFAULTS = {
    "copycraft": {
        "project": None,
        "state": None,
        "phase": None,
        "block": None,
        "agents": {
            "A": {"status": "idle", "label": ""},
            "B": {"status": "idle", "label": ""},
            "C": {"status": "idle", "label": ""},
            "S": {"status": "idle", "label": ""},
            "H": {"status": "idle", "label": ""},
            "I": {"status": "idle", "label": ""},
            "J": {"status": "idle", "label": ""},
            "F": {"status": "idle", "label": ""},
            "G": {"status": "idle", "label": ""},
            "P": {"status": "idle", "label": ""},
            "Q": {"status": "idle", "label": ""},
            "R": {"status": "idle", "label": ""},
            "DR": {"status": "idle", "label": ""}
        }
    },
    "research": {
        "project": None,
        "state": None,
        "agents": {
            "A": {"status": "idle", "label": ""},
            "B": {"status": "idle", "label": ""},
            "C": {"status": "idle", "label": ""},
            "S": {"status": "idle", "label": ""},
            "T": {"status": "idle", "label": ""},
            "H": {"status": "idle", "label": ""},
            "U": {"status": "idle", "label": ""},
            "V": {"status": "idle", "label": ""},
            "W": {"status": "idle", "label": ""},
            "DR": {"status": "idle", "label": ""}
        }
    },
    "log": []
}


def load():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return json.loads(json.dumps(DEFAULTS))


def save(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Sync to Firebase
    try:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{FIREBASE_URL}/state.json",
            data=payload,
            method="PUT",
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5, context=SSL_CONTEXT)
    except (urllib.error.URLError, OSError):
        pass  # Firebase unavailable — local file still works


def add_log(data, system, message):
    ts = datetime.now().strftime("%H:%M:%S")
    data.setdefault("log", [])
    data["log"].append({"time": ts, "system": system, "message": message})
    # Keep last 100 entries
    if len(data["log"]) > 100:
        data["log"] = data["log"][-100:]


def main():
    parser = argparse.ArgumentParser(description="Update agent visualizer state")
    parser.add_argument("--system", "-s", choices=["copycraft", "research", "cc", "re"],
                        help="System: copycraft (cc) or research (re)")
    parser.add_argument("--state", help="Set current state (e.g. RESEARCH, EXECUTION)")
    parser.add_argument("--project", help="Set project name")
    parser.add_argument("--phase", help="Set phase (e.g. 'PHASE C — COPY')")
    parser.add_argument("--block", help="Set current block (e.g. Lead, Mechanism)")
    parser.add_argument("--agent", "-a", help="Agent ID (e.g. A, F, DR)")
    parser.add_argument("--status", choices=["idle", "working", "done", "error", "waiting"],
                        help="Agent status")
    parser.add_argument("--label", "-l", default="", help="Agent label text")
    parser.add_argument("--log", help="Add log message (auto-generated if not provided)")
    parser.add_argument("--reset", action="store_true", help="Reset all to defaults")
    parser.add_argument("--reset-agents", action="store_true",
                        help="Reset all agents in system to idle")

    args = parser.parse_args()

    # Normalize system name
    if args.system in ("cc", "copycraft"):
        system = "copycraft"
    elif args.system in ("re", "research"):
        system = "research"
    else:
        system = args.system

    # Reset
    if args.reset:
        save(json.loads(json.dumps(DEFAULTS)))
        print("Reset to defaults")
        return

    data = load()

    if not system and not args.reset:
        parser.error("--system is required (unless --reset)")

    sys_data = data.setdefault(system, {})

    # Reset agents
    if args.reset_agents:
        for aid in sys_data.get("agents", {}):
            sys_data["agents"][aid] = {"status": "idle", "label": ""}
        add_log(data, system, "All agents reset to idle")

    # Set project
    if args.project:
        sys_data["project"] = args.project

    # Set state
    if args.state:
        old = sys_data.get("state")
        sys_data["state"] = args.state
        msg = args.log or f"STATE → {args.state}"
        if old and old != args.state:
            msg = args.log or f"STATE: {old} → {args.state}"
        add_log(data, system, msg)

    # Set phase/block
    if args.phase is not None:
        sys_data["phase"] = args.phase or None
    if args.block is not None:
        sys_data["block"] = args.block or None

    # Update agent
    if args.agent:
        agents = sys_data.setdefault("agents", {})
        aid = args.agent.upper()
        if aid not in agents:
            agents[aid] = {"status": "idle", "label": ""}
        if args.status:
            agents[aid]["status"] = args.status
        if args.label:
            agents[aid]["label"] = args.label
        elif args.status == "idle":
            agents[aid]["label"] = ""

        # Auto-log for agent changes
        if args.status and not args.log and not args.state:
            status_labels = {
                "working": f"Dispatch: {aid}",
                "done": f"{aid} done",
                "error": f"{aid} ERROR",
                "waiting": f"{aid} waiting",
                "idle": f"{aid} idle"
            }
            msg = status_labels.get(args.status, f"{aid} → {args.status}")
            if args.label:
                msg += f" — {args.label}"
            add_log(data, system, msg)

    # Custom log
    if args.log and not args.state and not args.agent:
        add_log(data, system, args.log)

    save(data)

    # Compact output
    parts = []
    if args.state:
        parts.append(f"state={args.state}")
    if args.agent and args.status:
        parts.append(f"{args.agent}={args.status}")
    print("OK: " + ", ".join(parts) if parts else "OK")


if __name__ == "__main__":
    main()
