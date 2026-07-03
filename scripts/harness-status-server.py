#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
harness-status-server.py — Serve an HTML status dashboard for harness-eng projects.

Usage:
    python scripts/harness-status-server.py [project_dir] [--port PORT]

    project_dir: Path to project root (default: current directory)
    port: Server port (default: 8080)

The server provides:
    - GET /           — HTML status dashboard
    - GET /api/status — JSON status snapshot
    - POST /api/approve — Approve a design
    - POST /api/priority — Change feature priority
"""

import json
import os
import sys
import re
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import argparse
from datetime import datetime


class HarnessStatusCollector:
    """Collects status information from .harness-eng/ directory."""

    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.harness_dir = self.project_dir / ".harness-eng"

    def collect(self):
        """Collect all status information and return as dict."""
        status = {
            "project": self._get_project_name(),
            "last_updated": datetime.now().isoformat(),
            "constitution": self._check_file("CONSTITUTION.md"),
            "brd": self._check_file("BRD.md"),
            "architecture": self._check_file("ARCHITECTURE.md"),
            "technology": self._check_file("technology.yaml"),
            "phases": self._get_phases(),
            "single_features": self._get_single_features(),
            "summary": {}
        }

        # Calculate summary
        all_features = []
        for phase in status["phases"]:
            all_features.extend(phase.get("features", []))
        all_features.extend(status["single_features"])

        total = len(all_features)
        done = sum(1 for f in all_features if f.get("status") == "done")
        active = sum(1 for f in all_features if f.get("status") == "active")
        pending = sum(1 for f in all_features if f.get("status") == "pending")

        status["summary"] = {
            "total_phases": len(status["phases"]),
            "total_features": total,
            "done": done,
            "active": active,
            "pending": pending,
            "progress_pct": round(done / total * 100) if total > 0 else 0
        }

        return status

    def _get_project_name(self):
        """Extract project name from BRD or directory name."""
        brd_path = self.harness_dir / "BRD.md"
        if brd_path.exists():
            content = brd_path.read_text()
            # Look for project name in header
            match = re.search(r'^#\s+(?:Business Requirements Document|BRD)\s*[:–—]\s*(.+)', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        return self.project_dir.name

    def _check_file(self, filename):
        """Check if a file exists and get its status."""
        filepath = self.harness_dir / filename
        if filepath.exists():
            content = filepath.read_text()
            # Check for approval status
            approved = "approved" in content.lower() or "Approved by:" in content
            return {"exists": True, "approved": approved}
        return {"exists": False, "approved": False}

    def _get_phases(self):
        """Get all phases and their features."""
        phases_dir = self.harness_dir / "phases" / "active"
        if not phases_dir.exists():
            return []

        phases = []
        for phase_dir in sorted(phases_dir.iterdir()):
            if not phase_dir.is_dir():
                continue

            phase = {
                "id": phase_dir.name,
                "name": self._get_phase_name(phase_dir),
                "goal": self._get_phase_goal(phase_dir),
                "status": self._get_phase_status(phase_dir),
                "features": self._get_phase_features(phase_dir)
            }
            phases.append(phase)

        return phases

    def _get_phase_name(self, phase_dir):
        """Extract phase name from directory name."""
        # Convert "phase-1-foundation" to "Foundation"
        name = phase_dir.name
        # Remove phase-N- prefix
        name = re.sub(r'^phase-\d+-', '', name)
        # Capitalize
        return name.replace('-', ' ').title()

    def _get_phase_goal(self, phase_dir):
        """Extract phase goal from PHASE.md."""
        phase_md = phase_dir / "PHASE.md"
        if phase_md.exists():
            content = phase_md.read_text()
            match = re.search(r'^## Goal\s*\n\s*(.+)', content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        return ""

    def _get_phase_status(self, phase_dir):
        """Determine phase status from features."""
        features_dir = phase_dir / "features"
        if not features_dir.exists():
            return "pending"

        has_active = any(features_dir.iterdir())
        has_archived = False

        if has_active:
            return "active"
        elif has_archived:
            return "done"
        else:
            return "pending"

    def _get_phase_features(self, phase_dir):
        """Get all features in a phase."""
        features_dir = phase_dir / "features"
        if not features_dir.exists():
            return []

        features = []

        # Active features
        active_dir = features_dir / "active"
        if active_dir.exists():
            for feature_dir in active_dir.iterdir():
                if feature_dir.is_dir():
                    features.append(self._get_feature_info(feature_dir, "active"))

        # Archived features
        archive_dir = features_dir / "archive"
        if archive_dir.exists():
            for feature_dir in archive_dir.iterdir():
                if feature_dir.is_dir():
                    features.append(self._get_feature_info(feature_dir, "done"))

        return features

    def _get_single_features(self):
        """Get features from specs/ (non-phased project)."""
        specs_dir = self.harness_dir / "specs"
        if not specs_dir.exists():
            return []

        features = []

        # Active features
        active_dir = specs_dir / "active"
        if active_dir.exists():
            for feature_dir in active_dir.iterdir():
                if feature_dir.is_dir():
                    features.append(self._get_feature_info(feature_dir, "active"))

        # Archived features
        archive_dir = specs_dir / "archive"
        if archive_dir.exists():
            for feature_dir in archive_dir.iterdir():
                if feature_dir.is_dir():
                    features.append(self._get_feature_info(feature_dir, "done"))

        return features

    def _get_feature_info(self, feature_dir, default_status):
        """Get information about a feature."""
        name = feature_dir.name

        # Check for spec.md
        spec_path = feature_dir / "spec.md"
        has_spec = spec_path.exists()

        # Check for design.md
        design_path = feature_dir / "design.md"
        has_design = design_path.exists()
        design_approved = False
        if has_design:
            content = design_path.read_text()
            design_approved = "Approved by:" in content

        # Check for tasks.md
        tasks_path = feature_dir / "tasks.md"
        has_tasks = tasks_path.exists()

        # Check for verification.md
        verification_path = feature_dir / "verification.md"
        has_verification = verification_path.exists()

        # Determine status
        if has_verification:
            status = "done"
        elif has_tasks:
            status = "active"
        elif has_design:
            status = "designed"
        elif has_spec:
            status = "defined"
        else:
            status = default_status

        # Get stories count from spec
        stories_count = 0
        if has_spec:
            content = spec_path.read_text()
            stories_count = len(re.findall(r'^###\s+Story\s+\d+', content, re.MULTILINE))

        return {
            "id": name,
            "name": name.replace('-', ' ').title(),
            "status": status,
            "has_spec": has_spec,
            "has_design": has_design,
            "design_approved": design_approved,
            "has_tasks": has_tasks,
            "has_verification": has_verification,
            "stories_count": stories_count
        }


class HarnessRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for harness status dashboard."""

    def __init__(self, *args, project_dir=None, **kwargs):
        self.project_dir = project_dir
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._serve_dashboard()
        elif parsed.path == "/api/status":
            self._serve_status_json()
        elif parsed.path == "/api/style.css":
            self._serve_css()
        elif parsed.path == "/api/app.js":
            self._serve_js()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if parsed.path == "/api/approve":
            self._handle_approve(data)
        elif parsed.path == "/api/priority":
            self._handle_priority(data)
        else:
            self.send_error(404)

    def _serve_dashboard(self):
        """Serve the HTML dashboard."""
        html = self._get_html()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_status_json(self):
        """Serve the status as JSON."""
        collector = HarnessStatusCollector(self.project_dir)
        status = collector.collect()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status, indent=2).encode())

    def _serve_css(self):
        """Serve CSS."""
        css = self._get_css()
        self.send_response(200)
        self.send_header('Content-Type', 'text/css')
        self.end_headers()
        self.wfile.write(css.encode())

    def _serve_js(self):
        """Serve JavaScript."""
        js = self._get_js()
        self.send_response(200)
        self.send_header('Content-Type', 'application/javascript')
        self.end_headers()
        self.wfile.write(js.encode())

    def _handle_approve(self, data):
        """Handle approval request."""
        feature_path = data.get("feature_path")
        approved_by = data.get("approved_by", "User")

        if not feature_path:
            self.send_error(400, "Missing feature_path")
            return

        # Resolve the full path
        full_path = self.project_dir / ".harness-eng" / feature_path
        design_path = full_path / "design.md"

        if not design_path.exists():
            self.send_error(404, f"design.md not found at {feature_path}")
            return

        # Append approval
        content = design_path.read_text()
        if "Approved by:" not in content:
            content += f"\n\n---\n\n**Approved by:** {approved_by}\n**Approved:** {datetime.now().strftime('%Y-%m-%d')}\n"
            design_path.write_text(content)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": True}).encode())

    def _handle_priority(self, data):
        """Handle priority change request."""
        # This would update priority in spec.md
        # For now, just acknowledge
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": True, "note": "Priority update not yet implemented"}).encode())

    def _get_html(self):
        """Return the HTML dashboard."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>harness-eng Status Dashboard</title>
    <link rel="stylesheet" href="/api/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>harness-eng Status Dashboard</h1>
            <p class="subtitle">Project: <span id="project-name">Loading...</span></p>
            <p class="last-updated">Last updated: <span id="last-updated">-</span></p>
        </header>

        <section class="summary">
            <h2>Summary</h2>
            <div class="summary-cards">
                <div class="card">
                    <span class="card-value" id="total-phases">0</span>
                    <span class="card-label">Phases</span>
                </div>
                <div class="card">
                    <span class="card-value" id="total-features">0</span>
                    <span class="card-label">Features</span>
                </div>
                <div class="card">
                    <span class="card-value" id="done-count">0</span>
                    <span class="card-label">Done</span>
                </div>
                <div class="card">
                    <span class="card-value" id="active-count">0</span>
                    <span class="card-label">Active</span>
                </div>
                <div class="card progress">
                    <span class="card-value" id="progress-pct">0%</span>
                    <span class="card-label">Progress</span>
                </div>
            </div>
        </section>

        <section class="prerequisites">
            <h2>Prerequisites</h2>
            <div class="prereq-list">
                <div class="prereq" id="prereq-constitution">
                    <span class="prereq-status">-</span>
                    <span class="prereq-name">Constitution</span>
                </div>
                <div class="prereq" id="prereq-brd">
                    <span class="prereq-status">-</span>
                    <span class="prereq-name">BRD</span>
                </div>
                <div class="prereq" id="prereq-architecture">
                    <span class="prereq-status">-</span>
                    <span class="prereq-name">Architecture</span>
                </div>
                <div class="prereq" id="prereq-technology">
                    <span class="prereq-status">-</span>
                    <span class="prereq-name">Technology</span>
                </div>
            </div>
        </section>

        <section class="phases">
            <h2>Phases</h2>
            <div id="phases-container">
                <p>Loading phases...</p>
            </div>
        </section>

        <section class="single-features" id="single-features-section" style="display: none;">
            <h2>Features</h2>
            <div id="features-container">
                <p>Loading features...</p>
            </div>
        </section>
    </div>

    <script src="/api/app.js"></script>
</body>
</html>'''

    def _get_css(self):
        """Return CSS styles."""
        return '''
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e0e0e0;
}

header h1 {
    font-size: 2rem;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}

.subtitle {
    font-size: 1.1rem;
    color: #666;
}

.last-updated {
    font-size: 0.9rem;
    color: #999;
    margin-top: 0.5rem;
}

section {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

section h2 {
    font-size: 1.3rem;
    color: #1a1a1a;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.card {
    text-align: center;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.card-value {
    display: block;
    font-size: 2rem;
    font-weight: bold;
    color: #1a1a1a;
}

.card-label {
    display: block;
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.25rem;
}

.card.progress .card-value {
    color: #28a745;
}

.prereq-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.prereq {
    display: flex;
    align-items: center;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.prereq-status {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    margin-right: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.prereq-status.exists {
    background: #28a745;
    color: white;
}

.prereq-status.missing {
    background: #dc3545;
    color: white;
}

.prereq-name {
    font-weight: 500;
}

.phase {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #6c757d;
}

.phase.active {
    border-left-color: #007bff;
}

.phase.done {
    border-left-color: #28a745;
}

.phase-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.phase-name {
    font-size: 1.1rem;
    font-weight: 600;
}

.phase-status {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 500;
}

.phase-status.pending {
    background: #e9ecef;
    color: #6c757d;
}

.phase-status.active {
    background: #cce5ff;
    color: #004085;
}

.phase-status.done {
    background: #d4edda;
    color: #155724;
}

.phase-goal {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 0.75rem;
}

.features-list {
    margin-top: 0.75rem;
}

.feature {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: white;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    border: 1px solid #e0e0e0;
}

.feature-info {
    flex: 1;
}

.feature-name {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.feature-meta {
    font-size: 0.85rem;
    color: #666;
}

.feature-actions {
    display: flex;
    gap: 0.5rem;
}

.btn {
    padding: 0.4rem 0.8rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: background 0.2s;
}

.btn-approve {
    background: #28a745;
    color: white;
}

.btn-approve:hover {
    background: #218838;
}

.btn-approve:disabled {
    background: #6c757d;
    cursor: not-allowed;
}

.btn-priority {
    background: #17a2b8;
    color: white;
}

.btn-priority:hover {
    background: #138496;
}

.status-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 500;
}

.status-badge.defined {
    background: #fff3cd;
    color: #856404;
}

.status-badge.designed {
    background: #cce5ff;
    color: #004085;
}

.status-badge.active {
    background: #d1ecf1;
    color: #0c5460;
}

.status-badge.done {
    background: #d4edda;
    color: #155724;
}

.empty-state {
    text-align: center;
    padding: 2rem;
    color: #666;
}

@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }

    .summary-cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .prereq-list {
        grid-template-columns: 1fr;
    }

    .feature {
        flex-direction: column;
        align-items: flex-start;
    }

    .feature-actions {
        margin-top: 0.5rem;
        width: 100%;
    }

    .feature-actions .btn {
        flex: 1;
    }
}
'''

    def _get_js(self):
        """Return JavaScript."""
        return '''
// Load status on page load
document.addEventListener('DOMContentLoaded', loadStatus);

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        renderStatus(status);
    } catch (error) {
        console.error('Failed to load status:', error);
    }
}

function renderStatus(status) {
    // Project name
    document.getElementById('project-name').textContent = status.project;
    document.getElementById('last-updated').textContent = new Date(status.last_updated).toLocaleString();

    // Summary
    document.getElementById('total-phases').textContent = status.summary.total_phases;
    document.getElementById('total-features').textContent = status.summary.total_features;
    document.getElementById('done-count').textContent = status.summary.done;
    document.getElementById('active-count').textContent = status.summary.active;
    document.getElementById('progress-pct').textContent = status.summary.progress_pct + '%';

    // Prerequisites
    renderPrereq('prereq-constitution', status.constitution);
    renderPrereq('prereq-brd', status.brd);
    renderPrereq('prereq-architecture', status.architecture);
    renderPrereq('prereq-technology', status.technology);

    // Phases
    const phasesContainer = document.getElementById('phases-container');
    if (status.phases.length > 0) {
        phasesContainer.innerHTML = status.phases.map(renderPhase).join('');
    } else {
        phasesContainer.innerHTML = '<p class="empty-state">No phases defined. Run /h:define to create phases.</p>';
    }

    // Single features
    const featuresSection = document.getElementById('single-features-section');
    const featuresContainer = document.getElementById('features-container');
    if (status.single_features.length > 0) {
        featuresSection.style.display = 'block';
        featuresContainer.innerHTML = status.single_features.map(renderFeature).join('');
    } else {
        featuresSection.style.display = 'none';
    }
}

function renderPrereq(id, prereq) {
    const element = document.getElementById(id);
    const statusEl = element.querySelector('.prereq-status');

    if (prereq.exists) {
        statusEl.textContent = '✓';
        statusEl.className = 'prereq-status exists';
    } else {
        statusEl.textContent = '✗';
        statusEl.className = 'prereq-status missing';
    }
}

function renderPhase(phase) {
    const featuresHtml = phase.features.map(f => renderFeature(f, phase.id)).join('');

    return `
        <div class="phase ${phase.status}">
            <div class="phase-header">
                <span class="phase-name">${phase.name}</span>
                <span class="phase-status ${phase.status}">${phase.status}</span>
            </div>
            ${phase.goal ? `<div class="phase-goal">${phase.goal}</div>` : ''}
            <div class="features-list">
                ${featuresHtml || '<p class="empty-state">No features in this phase</p>'}
            </div>
        </div>
    `;
}

function renderFeature(feature, phaseId = null) {
    const featurePath = phaseId
        ? `phases/active/${phaseId}/features/${feature.id}`
        : `specs/active/${feature.id}`;

    const approveBtn = feature.has_design && !feature.design_approved
        ? `<button class="btn btn-approve" onclick="approveFeature('${featurePath}', '${feature.id}')">Approve</button>`
        : `<button class="btn btn-approve" disabled>Approved</button>`;

    const meta = [];
    if (feature.stories_count > 0) meta.push(`${feature.stories_count} stories`);
    if (feature.has_tasks) meta.push('Tasks ready');
    if (feature.has_verification) meta.push('Verified');

    return `
        <div class="feature">
            <div class="feature-info">
                <div class="feature-name">${feature.name}</div>
                <div class="feature-meta">
                    <span class="status-badge ${feature.status}">${feature.status}</span>
                    ${meta.length > 0 ? ' · ' + meta.join(' · ') : ''}
                </div>
            </div>
            <div class="feature-actions">
                ${approveBtn}
            </div>
        </div>
    `;
}

async function approveFeature(featurePath, featureId) {
    if (!confirm(`Approve design for ${featureId}?`)) return;

    try {
        const response = await fetch('/api/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                feature_path: featurePath,
                approved_by: 'User'
            })
        });

        const result = await response.json();
        if (result.success) {
            loadStatus(); // Refresh
        }
    } catch (error) {
        console.error('Failed to approve:', error);
        alert('Failed to approve feature');
    }
}

// Auto-refresh every 30 seconds
setInterval(loadStatus, 30000);
'''

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    parser = argparse.ArgumentParser(description='harness-eng Status Dashboard')
    parser.add_argument('project_dir', nargs='?', default='.', help='Project directory')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)

    if not os.path.exists(os.path.join(project_dir, '.harness-eng')):
        print(f"Error: .harness-eng directory not found in {project_dir}")
        print("Make sure you're in a harness-eng project directory.")
        sys.exit(1)

    print(f"Starting harness-eng Status Dashboard...")
    print(f"Project: {project_dir}")
    print(f"URL: http://localhost:{args.port}")
    print(f"Press Ctrl+C to stop")

    server = HTTPServer(('localhost', args.port), lambda *a, **kw: HarnessRequestHandler(*a, project_dir=project_dir, **kw))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
