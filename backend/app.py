import os
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

FIELDS = [
    "title",
    "description",
    "research_area",
    "faculty_name",
    "department",
    "required_skills",
    "positions",
    "deadline",
    "status",
]
REQUIRED = [f for f in FIELDS if f != "status"]


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "research_portal"),
    )


def serialize(row):
    row["deadline"] = row["deadline"].isoformat()
    return row


def validate(data, partial=False):
    if not isinstance(data, dict):
        return ["Request body must be valid JSON"]
    errors = []
    for field in REQUIRED:
        if field not in data:
            if not partial:
                errors.append(f"{field} is required")
        elif str(data[field]).strip() == "":
            errors.append(f"{field} cannot be empty")
    if "positions" in data and str(data["positions"]).strip() != "":
        try:
            if int(data["positions"]) < 1:
                errors.append("positions must be at least 1")
        except (ValueError, TypeError):
            errors.append("positions must be a number")
    if "deadline" in data and str(data["deadline"]).strip() != "":
        try:
            datetime.strptime(str(data["deadline"]), "%Y-%m-%d")
        except ValueError:
            errors.append("deadline must be in YYYY-MM-DD format")
    if "status" in data and data["status"] not in ("Open", "Closed"):
        errors.append("status must be Open or Closed")
    return errors


def fetch_one(cursor, opportunity_id):
    cursor.execute("SELECT * FROM opportunities WHERE id = %s", (opportunity_id,))
    return cursor.fetchone()


@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    data = request.get_json(silent=True)
    errors = validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    values = {f: data[f] for f in REQUIRED}
    values["status"] = data.get("status", "Open")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """INSERT INTO opportunities
            (title, description, research_area, faculty_name, department,
             required_skills, positions, deadline, status)
            VALUES (%(title)s, %(description)s, %(research_area)s, %(faculty_name)s,
                    %(department)s, %(required_skills)s, %(positions)s, %(deadline)s, %(status)s)""",
            values,
        )
        db.commit()
        row = fetch_one(cursor, cursor.lastrowid)
        return jsonify(serialize(row)), 201
    finally:
        cursor.close()
        db.close()


@app.route("/api/opportunities", methods=["GET"])
def get_all_opportunities():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM opportunities ORDER BY id DESC")
        return jsonify([serialize(r) for r in cursor.fetchall()]), 200
    finally:
        cursor.close()
        db.close()


@app.route("/api/opportunities/<int:opportunity_id>", methods=["GET"])
def get_opportunity(opportunity_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        row = fetch_one(cursor, opportunity_id)
        if not row:
            return jsonify({"error": "Opportunity not found"}), 404
        return jsonify(serialize(row)), 200
    finally:
        cursor.close()
        db.close()


@app.route("/api/opportunities/<int:opportunity_id>", methods=["PUT"])
def update_opportunity(opportunity_id):
    data = request.get_json(silent=True)
    errors = validate(data, partial=True)
    if not errors and not any(k in FIELDS for k in data):
        errors = ["No valid fields provided to update"]
    if errors:
        return jsonify({"errors": errors}), 400
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not fetch_one(cursor, opportunity_id):
            return jsonify({"error": "Opportunity not found"}), 404
        updates = {k: data[k] for k in FIELDS if k in data}
        set_clause = ", ".join(f"{k} = %s" for k in updates)
        cursor.execute(
            f"UPDATE opportunities SET {set_clause} WHERE id = %s",
            list(updates.values()) + [opportunity_id],
        )
        db.commit()
        return jsonify(serialize(fetch_one(cursor, opportunity_id))), 200
    finally:
        cursor.close()
        db.close()


@app.route("/api/opportunities/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not fetch_one(cursor, opportunity_id):
            return jsonify({"error": "Opportunity not found"}), 404
        cursor.execute("DELETE FROM opportunities WHERE id = %s", (opportunity_id,))
        db.commit()
        return jsonify({"message": "Opportunity deleted successfully"}), 200
    finally:
        cursor.close()
        db.close()


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(500)
def server_error(_):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(mysql.connector.Error)
def database_error(_):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
