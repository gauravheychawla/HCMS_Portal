"""
THRONE · CloudOps Platform
Python / Flask web application
"""

from flask import Flask, send_from_directory, jsonify, request
from datetime import datetime

app = Flask(__name__)


# ── Data ────────────────────────────────────────────────────────────────────

ESTATES = [
    {"id": "vmware",  "name": "VMware vSphere / VCF",   "kind": "Private cloud", "nodes": 412,  "vms": 6840,  "signals": 23, "health": 97.4, "region": "DC-East · DC-West"},
    {"id": "aws",     "name": "Amazon Web Services",      "kind": "Public cloud",  "nodes": 1840, "vms": 12410, "signals": 41, "health": 99.1, "region": "us-east-1 · eu-west-1"},
    {"id": "azure",   "name": "Microsoft Azure",          "kind": "Public cloud",  "nodes": 1320, "vms": 9180,  "signals": 28, "health": 98.6, "region": "eastus2 · westeurope"},
    {"id": "gcp",     "name": "Google Cloud",             "kind": "Public cloud",  "nodes": 560,  "vms": 3970,  "signals": 12, "health": 99.3, "region": "us-central1"},
    {"id": "oci",     "name": "Oracle Cloud (OCI)",       "kind": "Public cloud",  "nodes": 290,  "vms": 1840,  "signals": 9,  "health": 98.0, "region": "us-ashburn-1"},
    {"id": "hyperv",  "name": "Microsoft Hyper-V",        "kind": "Private cloud", "nodes": 188,  "vms": 2210,  "signals": 7,  "health": 96.8, "region": "DC-Central"},
]

AGENTS = [
    {"id": "a1", "name": "Compute Triage Agent",      "domain": "servers",  "state": "active",   "today": 184, "rate": 71, "mttr": "6m"},
    {"id": "a2", "name": "Storage Remediation Agent", "domain": "storage",  "state": "active",   "today": 96,  "rate": 68, "mttr": "9m"},
    {"id": "a3", "name": "Network Path Agent",        "domain": "network",  "state": "active",   "today": 142, "rate": 59, "mttr": "12m"},
    {"id": "a4", "name": "Security Posture Agent",    "domain": "netsec",   "state": "active",   "today": 73,  "rate": 64, "mttr": "8m"},
    {"id": "a5", "name": "Gateway Health Agent",      "domain": "gateway",  "state": "learning", "today": 51,  "rate": 47, "mttr": "14m"},
]

INCIDENTS = [
    {"id": "INC0421887", "title": "p99 disk latency spike on prod-sql-03",       "estate": "vmware", "domain": "storage",  "sev": "P2", "tier": "resolved", "confidence": 92, "source": "Dynatrace",  "age": "11m", "status": "Auto-resolved"},
    {"id": "INC0421902", "title": "BGP session flapping on edge-gw-2",            "estate": "aws",    "domain": "gateway",  "sev": "P1", "tier": "l2",       "confidence": 58, "source": "Grafana",    "age": "6m",  "status": "Escalated to L2"},
    {"id": "INC0421910", "title": "CPU ready time >12% across 9 hosts",           "estate": "vmware", "domain": "servers",  "sev": "P3", "tier": "l1",       "confidence": 81, "source": "BigPanda",   "age": "2m",  "status": "Resolving (L1)"},
    {"id": "INC0421888", "title": "NSG rule drift on payments subnet",            "estate": "azure",  "domain": "netsec",   "sev": "P2", "tier": "resolved", "confidence": 88, "source": "Defender",   "age": "34m", "status": "Auto-resolved"},
    {"id": "INC0421915", "title": "EBS volume nearing IOPS ceiling",              "estate": "aws",    "domain": "storage",  "sev": "P3", "tier": "l1",       "confidence": 77, "source": "CloudWatch", "age": "1m",  "status": "Resolving (L1)"},
    {"id": "INC0421860", "title": "Load balancer 5xx surge eu-west-1",            "estate": "aws",    "domain": "network",  "sev": "P1", "tier": "resolved", "confidence": 90, "source": "Datadog",    "age": "52m", "status": "Auto-resolved"},
    {"id": "INC0421921", "title": "OCI bastion unreachable us-ashburn-1",         "estate": "oci",    "domain": "gateway",  "sev": "P2", "tier": "l2",       "confidence": 49, "source": "Moogsoft",   "age": "4m",  "status": "Escalated to L2"},
    {"id": "INC0421799", "title": "Hyper-V cluster node memory pressure",         "estate": "hyperv", "domain": "servers",  "sev": "P3", "tier": "resolved", "confidence": 85, "source": "SCOM",       "age": "1h",  "status": "Auto-resolved"},
]

OPS_AGENTS = [
    {"id": "h1", "name": "Health Check Agent",      "category": "healthcheck", "cadence": "every 5 min",    "runs": 8640, "success_pct": 99,  "hours_saved": 210, "mode": "autonomous",     "status": "healthy"},
    {"id": "k1", "name": "Housekeeping Agent",       "category": "hygiene",     "cadence": "hourly",         "runs": 4320, "success_pct": 99,  "hours_saved": 118, "mode": "autonomous",     "status": "healthy"},
    {"id": "d1", "name": "Compliance Drift Agent",   "category": "compliance",  "cadence": "every 30 min",   "runs": 1440, "success_pct": 95,  "hours_saved": 84,  "mode": "autonomous",     "status": "healthy"},
    {"id": "c1", "name": "Capacity & Forecast Agent","category": "capacity",    "cadence": "daily",          "runs": 182,  "success_pct": 98,  "hours_saved": 96,  "mode": "autonomous",     "status": "attention"},
    {"id": "r1", "name": "Health Reporting Agent",   "category": "reporting",   "cadence": "daily + weekly", "runs": 204,  "success_pct": 100, "hours_saved": 140, "mode": "autonomous",     "status": "healthy"},
    {"id": "x1", "name": "Certificate & License Agent","category": "hygiene",   "cadence": "daily",          "runs": 182,  "success_pct": 99,  "hours_saved": 54,  "mode": "autonomous",     "status": "healthy"},
    {"id": "b1", "name": "Backup Verification Agent","category": "resilience",  "cadence": "weekly",         "runs": 48,   "success_pct": 91,  "hours_saved": 88,  "mode": "autonomous",     "status": "attention"},
    {"id": "p1", "name": "Patch Orchestration Agent","category": "patching",    "cadence": "monthly window", "runs": 14,   "success_pct": 96,  "hours_saved": 320, "mode": "needs approval", "status": "healthy"},
    {"id": "f1", "name": "Cost & Idle Resource Agent","category": "finops",     "cadence": "weekly",         "runs": 36,   "success_pct": 97,  "hours_saved": 172, "mode": "needs approval", "status": "healthy"},
]

DR_SUMMARY = {
    "protected_servers": "2,860",
    "replicated_storage": "412 TB",
    "replication_pairs": 8,
    "rpo_achieved": "≤ 15 min",
}

REPLICATION = [
    {"pair": "VMware · DC-East → DC-West",    "tech": "VMware SRM + Dell PPDM", "servers": 640, "tb": 96,  "rpo": "≤ 15 min", "lag": "4 min",  "status": "healthy"},
    {"pair": "VMware · DC-West → Colo-DR",    "tech": "Zerto",                  "servers": 220, "tb": 38,  "rpo": "≤ 2 min",  "lag": "1 min",  "status": "healthy"},
    {"pair": "AWS · us-east-1 → us-west-2",   "tech": "AWS Elastic DR",         "servers": 410, "tb": 58,  "rpo": "≤ 5 min",  "lag": "2 min",  "status": "healthy"},
    {"pair": "AWS · eu-west-1 → eu-central-1","tech": "AWS Backup + native",    "servers": 260, "tb": 32,  "rpo": "≤ 15 min", "lag": "12 min", "status": "warning"},
    {"pair": "Azure · eastus2 → westus2",     "tech": "Azure Site Recovery",    "servers": 380, "tb": 44,  "rpo": "≤ 15 min", "lag": "6 min",  "status": "healthy"},
    {"pair": "GCP · us-central1 → us-east1",  "tech": "Native + Rubrik",        "servers": 180, "tb": 26,  "rpo": "≤ 15 min", "lag": "5 min",  "status": "healthy"},
    {"pair": "Hyper-V · DC-Central → DC-East","tech": "Commvault",              "servers": 150, "tb": 22,  "rpo": "≤ 30 min", "lag": "14 min", "status": "healthy"},
    {"pair": "OCI · ashburn → phoenix",       "tech": "Rubrik",                 "servers": 90,  "tb": 18,  "rpo": "≤ 30 min", "lag": "11 min", "status": "healthy"},
]

COVERAGE = {
    "health_check": {"value": "98%",  "detail": "all 6 estates probed",    "ok": True},
    "patch":        {"value": "94%",  "detail": "next wave in 26 days",    "ok": True},
    "backup":       {"value": "91%",  "detail": "1 restore drill overdue", "ok": False},
    "capacity":     {"value": "32%",  "detail": "2 clusters under watch",  "ok": False},
}


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# REST endpoints — consumed by the SPA or external tooling

@app.route("/api/estates")
def api_estates():
    return jsonify(ESTATES)


@app.route("/api/agents")
def api_agents():
    return jsonify(AGENTS)


@app.route("/api/incidents")
def api_incidents():
    return jsonify(INCIDENTS)


@app.route("/api/ops-agents")
def api_ops_agents():
    return jsonify(OPS_AGENTS)


@app.route("/api/resilience")
def api_resilience():
    return jsonify({"summary": DR_SUMMARY, "replication": REPLICATION})


@app.route("/api/coverage")
def api_coverage():
    return jsonify(COVERAGE)


@app.route("/api/status")
def api_status():
    total_nodes = sum(e["nodes"] for e in ESTATES)
    total_vms   = sum(e["vms"]   for e in ESTATES)
    active_inc  = [i for i in INCIDENTS if i["tier"] != "resolved"]
    resolved    = [i for i in INCIDENTS if i["tier"] == "resolved"]
    return jsonify({
        "timestamp":      datetime.utcnow().isoformat() + "Z",
        "estates":        len(ESTATES),
        "total_nodes":    total_nodes,
        "total_vms":      total_vms,
        "active_agents":  sum(1 for a in AGENTS if a["state"] == "active"),
        "incidents_open": len(active_inc),
        "incidents_resolved_today": len(resolved),
        "l1_deflection_pct": 62,
        "sla_conformance_pct": 98.7,
    })


HCMS_RUNBOOKS = [
    # ── L1 — Fully automated ─────────────────────────────────────────────────
    {"id": "HCMS-CPU-001",  "name": "CPU utilisation dump",                  "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 412,  "ok": 97, "last": "18m ago",  "desc": "Pulls live CPU metrics and top-process list from HCMS Portal REST API. Triggers a 120-second process-level dump and attaches the JSON report to the THRONE incident."},
    {"id": "HCMS-MEM-001",  "name": "Memory utilisation dump",               "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 388,  "ok": 96, "last": "22m ago",  "desc": "Captures full memory snapshot from HCMS Portal including pagefile, available RAM, and top consumers. Heap dump triggered above 85%."},
    {"id": "HCMS-PROC-001", "name": "Process tree analysis — CPU + memory",  "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 276,  "ok": 98, "last": "41m ago",  "desc": "Pulls full process tree with per-process CPU, memory, and open-handle counts. Flags handle-leak candidates >500 handles."},
    {"id": "HCMS-DISK-001", "name": "Disk space & IOPS snapshot",            "tier": "L1",   "domain": "storage",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 520,  "ok": 99, "last": "8m ago",   "desc": "Collects disk utilisation, IOPS counters, and queue depth from HCMS Portal for all volumes on the target server."},
    {"id": "HCMS-SVC-001",  "name": "Windows service health check",          "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 1140, "ok": 99, "last": "5m ago",   "desc": "Queries HCMS Portal for all monitored Windows services, surfaces any stopped or degraded services and their last-known event log entries."},
    {"id": "HCMS-LOG-001",  "name": "Event log collection — last 4h",        "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 830,  "ok": 98, "last": "12m ago",  "desc": "Fetches System, Application, and Security event log entries (Error/Critical) from HCMS Portal for the last 4 hours and writes a structured JSON report."},
    {"id": "HCMS-NET-001",  "name": "Network connectivity & latency check",  "tier": "L1",   "domain": "network",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 614,  "ok": 97, "last": "9m ago",   "desc": "Tests connectivity to all registered endpoints via HCMS Portal, measures RTT, and reports any packet loss above threshold."},
    {"id": "HCMS-PERF-001", "name": "Performance baseline capture",          "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 290,  "ok": 96, "last": "1h ago",   "desc": "Runs a 5-minute performance counters capture via HCMS Portal covering CPU, memory, disk, and network to establish a diagnostic baseline."},
    {"id": "HCMS-APP-STAT", "name": "Application pool status report",        "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 460,  "ok": 98, "last": "15m ago",  "desc": "Enumerates IIS application pools on the target server via HCMS Portal, reporting state, worker-process PIDs, and request queue depth."},
    {"id": "HCMS-PATCH-CHK","name": "Patch compliance check",                "tier": "L1",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 380,  "ok": 97, "last": "2h ago",   "desc": "Queries HCMS Portal for installed and missing patches against the approved baseline, emits a compliance score and list of missing KBs."},
    # ── L2 — Engineer review required ────────────────────────────────────────
    {"id": "HCMS-CPU-002",  "name": "CPU throttling & affinity remediation", "tier": "L2",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 188,  "ok": 91, "last": "47m ago",  "desc": "Identifies runaway processes via HCMS Portal and applies CPU affinity masks or priority throttling after L2 engineer confirms the target PID list."},
    {"id": "HCMS-MEM-002",  "name": "Memory leak investigation & quiesce",  "tier": "L2",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 142,  "ok": 88, "last": "1.2h ago", "desc": "Captures private byte trends from HCMS Portal over 30 minutes to identify leaking processes. L2 reviews the trend report before the quiesce step runs."},
    {"id": "HCMS-DISK-002", "name": "Disk cleanup — temp & log rotation",   "tier": "L2",   "domain": "storage",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 260,  "ok": 93, "last": "55m ago",  "desc": "Identifies top disk consumers via HCMS Portal, proposes temp/log cleanup plan. L2 engineer approves file list before deletion executes."},
    {"id": "HCMS-NET-002",  "name": "Network trace capture — 5-min PCAP",   "tier": "L2",   "domain": "network",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 98,   "ok": 94, "last": "2.1h ago", "desc": "Triggers a 5-minute packet capture on the target interface via HCMS Portal agent. L2 engineer reviews the capture trigger scope before start."},
    {"id": "HCMS-APP-001",  "name": "Application pool recycle & warm-up",   "tier": "L2",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 212,  "ok": 95, "last": "38m ago",  "desc": "Gracefully recycles nominated IIS app pools via HCMS Portal and runs warm-up probes. L2 engineer confirms the recycle window before execution."},
    {"id": "HCMS-STOR-002", "name": "Datastore IO contention remediation",  "tier": "L2",   "domain": "storage",  "lang": "Ansible",    "env": "onprem", "source": "HCMS Streamlit", "runs": 1284, "ok": 96, "last": "11m ago",  "desc": "Remediates VMware datastore IO contention: throttles snapshot consolidation, rebalances IO queues, clears stale locks. L2 reviews proposed queue-depth changes."},
    # ── HITL — Human in the loop ──────────────────────────────────────────────
    {"id": "HCMS-PATCH-001","name": "Emergency patch deployment",            "tier": "HITL", "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 64,   "ok": 97, "last": "3h ago",   "desc": "Deploys a specific KB patch to a target server via HCMS Portal after THRONE raises an emergency change. Human must approve the pre-reboot checkpoint and the post-reboot validation gate."},
    {"id": "HCMS-SVC-002",  "name": "Critical service restart",             "tier": "HITL", "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 109,  "ok": 96, "last": "1.8h ago", "desc": "Restarts a P1-flagged service via HCMS Portal. Human approves the stop step before the script proceeds, then reviews the post-start health probe result."},
    {"id": "HCMS-DISK-003", "name": "Disk volume online expansion",         "tier": "HITL", "domain": "storage",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 78,   "ok": 99, "last": "4h ago",   "desc": "Extends a disk volume using free space from HCMS Portal storage pool. Human must confirm the target volume, new size, and datastore allocation before the extend runs."},
    {"id": "HCMS-SEC-001",  "name": "Firewall rule remediation",            "tier": "HITL", "domain": "netsec",   "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 55,   "ok": 98, "last": "5h ago",   "desc": "Removes or modifies Windows Firewall / host-based rules flagged as non-compliant by HCMS Portal security scan. Human reviews the exact rule diff before any change is committed."},
    {"id": "HCMS-MAINT-001","name": "Host maintenance mode + VM migration", "tier": "HITL", "domain": "servers",  "lang": "Ansible",    "env": "onprem", "source": "HCMS Streamlit", "runs": 48,   "ok": 93, "last": "6h ago",   "desc": "Evacuates a hypervisor host into maintenance mode. Human confirms the target host and migration destinations; THRONE executes DRS vMotion and suppresses alerts."},
    # ── L3 — Expert / specialist required ────────────────────────────────────
    {"id": "HCMS-KERN-001", "name": "Kernel / mini-dump analysis",          "tier": "L3",   "domain": "servers",  "lang": "PowerShell", "env": "onprem", "source": "HCMS Streamlit", "runs": 22,   "ok": 90, "last": "1d ago",   "desc": "Retrieves crash / kernel mini-dumps from HCMS Portal and packages them with a WinDbg analysis script. Requires L3 kernel engineer to interpret results and advise remediation."},
    {"id": "HCMS-DB-001",   "name": "Database slow-query + lock analysis",  "tier": "L3",   "domain": "servers",  "lang": "Python",     "env": "onprem", "source": "HCMS Streamlit", "runs": 38,   "ok": 87, "last": "18h ago",  "desc": "Pulls slow-query logs and lock-wait metrics from SQL Server / Oracle via HCMS Portal connector. L3 DBA reviews index recommendations and approves execution plan changes."},
    {"id": "HCMS-CLUS-001", "name": "Cluster failover & quorum recovery",   "tier": "L3",   "domain": "servers",  "lang": "Ansible",    "env": "onprem", "source": "HCMS Streamlit", "runs": 14,   "ok": 86, "last": "2d ago",   "desc": "Executes a controlled Windows Server Failover Cluster node failover via HCMS Portal. L3 cluster engineer must be on a bridge call; THRONE drives the runbook steps with human gate at each cluster resource transfer."},
    # ── Cloud runbooks (L1 → L3) ─────────────────────────────────────────────
    {"id": "CLOUD-CPU-001", "name": "Cloud VM CPU utilisation dump",        "tier": "L1",   "domain": "servers",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 318,  "ok": 96, "last": "14m ago",  "desc": "Pulls CPU metrics via HCMS cloud connector for EC2/Azure VM/GCP Compute/OCI. Triggers a process-level dump through the HCMS agent and saves the JSON report."},
    {"id": "CLOUD-MEM-001", "name": "Cloud VM memory utilisation dump",     "tier": "L1",   "domain": "servers",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 290,  "ok": 95, "last": "19m ago",  "desc": "Captures memory snapshot (RAM + swap) via HCMS cloud connector. Triggers conditional heap dump above threshold and emits top-10 memory consumers."},
    {"id": "CLOUD-DISK-001","name": "Cloud disk utilisation snapshot",      "tier": "L1",   "domain": "storage",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 408,  "ok": 98, "last": "11m ago",  "desc": "Pulls disk utilisation and IOPS metrics from cloud-native monitoring via HCMS connector, flags volumes above 80% utilisation."},
    {"id": "CLOUD-NET-001", "name": "Cloud network latency & flow check",   "tier": "L1",   "domain": "network",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 560,  "ok": 97, "last": "7m ago",   "desc": "Queries VPC flow logs and network latency metrics from HCMS cloud connector, surfaces top-10 talkers and packet-drop rates by subnet."},
    {"id": "CLOUD-SCALE-001","name":"Auto-scaling group health + adjustment","tier": "L2",   "domain": "servers",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 214,  "ok": 94, "last": "32m ago",  "desc": "Reviews ASG/VMSS scaling activity via HCMS connector. L2 engineer approves the proposed desired-capacity change before THRONE applies it."},
    {"id": "CLOUD-COST-001","name": "Idle resource cost-reclaim",           "tier": "L2",   "domain": "servers",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 940,  "ok": 99, "last": "27m ago",  "desc": "Identifies idle compute, unattached volumes, and orphaned snapshots via HCMS cloud connector. L2 reviews the deletion list before THRONE executes."},
    {"id": "CLOUD-DR-001",  "name": "Cloud DR failover test",               "tier": "HITL", "domain": "servers",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 28,   "ok": 96, "last": "1d ago",   "desc": "Runs a non-destructive DR failover test via HCMS cloud connector. Human approves each phase: snapshot creation, test-VPC spin-up, application validation, teardown."},
    {"id": "CLOUD-SEC-001", "name": "Cloud security-group drift correction","tier": "HITL", "domain": "netsec",   "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 488,  "ok": 94, "last": "34m ago",  "desc": "Compares live NSG/security-group rules against approved baseline. Human reviews the diff for wide-open ingress before THRONE revokes excess rules."},
    {"id": "CLOUD-ARCH-001","name": "Cross-region architecture review",     "tier": "L3",   "domain": "network",  "lang": "Python",     "env": "cloud",  "source": "HCMS Streamlit", "runs": 12,   "ok": 83, "last": "5d ago",   "desc": "Produces a full cross-region connectivity and redundancy map via HCMS cloud connector. L3 cloud architect reviews findings and proposes remediation plan."},
]


@app.route("/api/runbooks")
def api_runbooks():
    tier  = request.args.get("tier")
    env   = request.args.get("env")
    items = HCMS_RUNBOOKS
    if tier: items = [r for r in items if r["tier"] == tier]
    if env:  items = [r for r in items if r["env"]  == env]
    return jsonify({"total": len(items), "runbooks": items})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
