from flask import Blueprint, request, jsonify
import json
from datetime import datetime

from backend.database import get_connection
from backend.gemini_client import GeminiClient

bugs_bp = Blueprint("bugs", __name__)


@bugs_bp.route("/analyze-bug", methods=["POST"])
def analyze_bug():
    try:
        data = request.get_json(silent=True)

        if not data or "bug_text" not in data:
            return jsonify({"error": "bug_text is required"}), 400

        bug_text = data.get("bug_text", "").strip()
        language = data.get("language")
        context = data.get("context")

        if not bug_text:
            return jsonify({"error": "bug_text cannot be empty"}), 400

        if len(bug_text) > 8000:
            return jsonify({"error": "bug_text is too long"}), 400

        # --- AI ANALYSIS ---
        gemini = GeminiClient()
        result = gemini.analyze_bug(bug_text, language, context)

        if not isinstance(result, dict):
            raise ValueError("Invalid AI response")

        # --- DATABASE SAVE ---
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bugs (
                bug_text, language, context,
                explanation, root_cause, fix_steps,
                example_code, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bug_text,
            language,
            context,
            result.get("explanation"),
            result.get("root_cause"),
            json.dumps(result.get("fix_steps", [])),
            result.get("example_code"),
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

        return jsonify(result), 200

    except Exception as e:
        # This prints directly into Render logs
        print("ANALYZE BUG ERROR:", str(e))
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@bugs_bp.route("/bugs", methods=["GET"])
def get_bugs():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, bug_text, language, context,
                   explanation, root_cause, fix_steps,
                   example_code, created_at
            FROM bugs
            ORDER BY created_at DESC
            LIMIT 20
        """)

        rows = cursor.fetchall()
        conn.close()

        bugs = []
        for row in rows:
            bugs.append({
                "id": row[0],
                "bug_text": row[1],
                "language": row[2],
                "context": row[3],
                "explanation": row[4],
                "root_cause": row[5],
                "fix_steps": json.loads(row[6]) if row[6] else [],
                "example_code": row[7],
                "created_at": row[8]
            })

        return jsonify(bugs), 200

    except Exception as e:
        print("FETCH BUGS ERROR:", str(e))
        # Frontend expects a list. Give it one.
        return jsonify([]), 200
