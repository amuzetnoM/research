"""
COMPASS Framework API

REST API for interacting with the COMPASS ethical framework.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from .compass_core import COMPASSFramework, Action

app = Flask(__name__)
CORS(app)

# Example directives and constraints
DIRECTIVES = [
    "Preservation of Human Life",
    "Respect for Human Dignity",
    "Promotion of Human Wellbeing",
    "Fairness and Non-Discrimination",
    "Transparency and Accountability",
    "Privacy and Data Protection",
    "Environmental Sustainability"
]

def no_harm_constraint(action: Action, environment: dict) -> bool:
    # Placeholder: always returns True (no harm detected)
    return True

framework = COMPASSFramework(DIRECTIVES, [no_harm_constraint])

@app.route("/api/compass/info", methods=["GET"])
def info():
    return jsonify({
        "name": "COMPASS Ethical Framework",
        "directives": DIRECTIVES
    })

@app.route("/api/compass/decide", methods=["POST"])
def decide():
    data = request.json
    actions_data = data.get("actions", [])
    environment = data.get("environment", {})
    user_commands = data.get("user_commands", [])
    system_state = data.get("system_state", {})

    actions = [Action(a.get("id", ""), a.get("parameters", {}), a.get("description", "")) for a in actions_data]
    context = framework.perceive(environment, user_commands, system_state)
    result = framework.decide_and_act(actions, context)
    if not result:
        return jsonify({"success": False, "error": "No permissible action found"}), 400
    return jsonify({
        "success": True,
        "action": result["action"].id,
        "explanation": result["explanation"],
        "outcome": result["outcome"]
    })

@app.route("/api/compass/logs", methods=["GET"])
def logs():
    return jsonify(framework.get_logs())

@app.route("/api/compass/metrics", methods=["GET"])
def metrics():
    return jsonify(framework.get_metrics())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)
