"""
Smart Health Risk Prediction System - Flask Backend
Author: Full-Stack Health App
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "health_records.db")

# ─────────────────────────────────────────────
# Database Initialization
# ─────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            age           INTEGER NOT NULL,
            gender        TEXT    NOT NULL,
            height_cm     REAL    NOT NULL,
            weight_kg     REAL    NOT NULL,
            blood_pressure TEXT,
            heart_rate    INTEGER NOT NULL,
            blood_sugar   REAL    NOT NULL,
            smoking       TEXT    NOT NULL,
            exercise_freq TEXT    NOT NULL,
            bmi           REAL    NOT NULL,
            risk_score    INTEGER NOT NULL,
            risk_level    TEXT    NOT NULL,
            created_at    TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# Helper: Calculate BMI
# ─────────────────────────────────────────────
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 2)

# ─────────────────────────────────────────────
# Helper: Calculate Risk Score & Level
# ─────────────────────────────────────────────
def calculate_risk(age, bmi, heart_rate, blood_sugar, smoking):
    score = 0
    breakdown = []

    if age > 50:
        score += 2
        breakdown.append({"factor": "Age > 50", "points": "+2"})
    if bmi > 25:
        score += 2
        breakdown.append({"factor": f"BMI {bmi} > 25 (Overweight)", "points": "+2"})
    if heart_rate > 100:
        score += 2
        breakdown.append({"factor": "Heart Rate > 100 bpm", "points": "+2"})
    if blood_sugar > 140:
        score += 3
        breakdown.append({"factor": "Blood Sugar > 140 mg/dL", "points": "+3"})
    if smoking.lower() == "yes":
        score += 2
        breakdown.append({"factor": "Active Smoker", "points": "+2"})

    if score <= 3:
        level = "Low"
    elif score <= 7:
        level = "Medium"
    else:
        level = "High"

    return score, level, breakdown

# ─────────────────────────────────────────────
# Helper: Get Recommendations
# ─────────────────────────────────────────────
def get_recommendations(risk_level, bmi, blood_sugar, heart_rate, smoking, exercise_freq):
    recs = []
    if risk_level == "Low":
        recs = [
            "✅ Maintain your healthy lifestyle — you're doing great!",
            "🥗 Keep a balanced diet rich in fruits, vegetables, and whole grains.",
            "🏃 Continue regular physical activity (at least 150 min/week).",
            "💧 Stay well-hydrated and get 7–8 hours of sleep nightly.",
            "🩺 Schedule annual health checkups as a preventive measure.",
        ]
    elif risk_level == "Medium":
        recs = [
            "⚠️ You have moderate health risks — proactive steps are important.",
            "🏋️ Increase exercise frequency to at least 4–5 days per week.",
            "📊 Monitor blood pressure, blood sugar, and heart rate regularly.",
            "🥦 Adopt a low-sugar, low-sodium diet to improve metabolic health.",
            "🚭 If you smoke, consider a cessation program — it significantly lowers risk.",
            "🩺 Consult your doctor for a comprehensive health screening.",
        ]
    else:
        recs = [
            "🚨 High health risk detected — please seek medical advice promptly.",
            "👨‍⚕️ Schedule an appointment with your doctor as soon as possible.",
            "💊 Follow any prescribed medication regimens strictly.",
            "🚫 Avoid smoking, alcohol, and high-sodium/sugar foods immediately.",
            "🏥 Undergo a thorough cardiac and metabolic evaluation.",
            "📉 Work with a dietician and fitness professional for a personalized plan.",
        ]

    # Additional specific tips
    if bmi > 30:
        recs.append("⚖️ Your BMI indicates obesity — a structured weight-loss program is recommended.")
    if blood_sugar > 140:
        recs.append("🍬 Elevated blood sugar detected — reduce refined carbs and monitor glucose daily.")
    if heart_rate > 100:
        recs.append("❤️ High resting heart rate — practice relaxation techniques and limit caffeine.")
    if smoking.lower() == "yes":
        recs.append("🚭 Quit smoking — it's the single most impactful step you can take for your health.")
    if exercise_freq.lower() in ["never", "rarely"]:
        recs.append("🏃 Start with 20–30 min walks daily and gradually increase intensity.")

    return recs

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        name          = request.form["name"].strip()
        age           = int(request.form["age"])
        gender        = request.form["gender"]
        height_cm     = float(request.form["height"])
        weight_kg     = float(request.form["weight"])
        blood_pressure= request.form.get("blood_pressure", "N/A").strip() or "N/A"
        heart_rate    = int(request.form["heart_rate"])
        blood_sugar   = float(request.form["blood_sugar"])
        smoking       = request.form["smoking"]
        exercise_freq = request.form["exercise_freq"]

        # Calculations
        bmi = calculate_bmi(weight_kg, height_cm)
        score, level, breakdown = calculate_risk(age, bmi, heart_rate, blood_sugar, smoking)
        recommendations = get_recommendations(level, bmi, blood_sugar, heart_rate, smoking, exercise_freq)

        # BMI Category
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO health_records
            (name, age, gender, height_cm, weight_kg, blood_pressure, heart_rate,
             blood_sugar, smoking, exercise_freq, bmi, risk_score, risk_level, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (name, age, gender, height_cm, weight_kg, blood_pressure, heart_rate,
              blood_sugar, smoking, exercise_freq, bmi, score, level,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return render_template("result.html",
            record_id=record_id, name=name, age=age, gender=gender,
            height_cm=height_cm, weight_kg=weight_kg, blood_pressure=blood_pressure,
            heart_rate=heart_rate, blood_sugar=blood_sugar, smoking=smoking,
            exercise_freq=exercise_freq, bmi=bmi, bmi_category=bmi_category,
            score=score, level=level, breakdown=breakdown,
            recommendations=recommendations,
            created_at=datetime.now().strftime("%B %d, %Y %I:%M %p")
        )

    except Exception as e:
        return render_template("index.html", error=f"Error processing data: {str(e)}")


@app.route("/history")
def history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to standard python dictionaries
    records = [dict(row) for row in rows]
    
    # Pre-calculate counts for stats & charts to bypass Jinja selectattr restrictions
    low_count = sum(1 for r in records if r['risk_level'] == 'Low')
    med_count = sum(1 for r in records if r['risk_level'] == 'Medium')
    high_count = sum(1 for r in records if r['risk_level'] == 'High')
    
    # Build chronological trend data for the line chart (oldest-first, last 10)
    trend_data = [
        {
            "label": r['name'][:10] + ' (' + r['created_at'][5:16] + ')',
            "bmi":   r['bmi'],
            "score": r['risk_score']
        }
        for r in reversed(records[:10])
    ]
    
    return render_template(
        "history.html",
        records=records,
        low_count=low_count,
        med_count=med_count,
        high_count=high_count,
        trend_data=trend_data
    )



@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM health_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("history"))


@app.route("/api/stats")
def api_stats():
    """Returns JSON stats for charts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM health_records")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT risk_level, COUNT(*) as cnt FROM health_records GROUP BY risk_level")
    risk_counts = {row["risk_level"]: row["cnt"] for row in cursor.fetchall()}

    cursor.execute("SELECT bmi, risk_score, age FROM health_records ORDER BY id DESC LIMIT 10")
    recent = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return jsonify({
        "total": total,
        "risk_counts": risk_counts,
        "recent": recent
    })


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("[OK] Database initialized.")
    print("[>>] Server starting at http://127.0.0.1:5000")
    app.run(debug=True)
