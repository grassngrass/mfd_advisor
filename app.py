from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, json
from datetime import datetime
from modules.analyzer import analyze_portfolio
from modules.risk import calculate_risk_profile
from modules.recommender import generate_recommendations
from modules.wealth import predict_wealth
from modules.pdf_generator import generate_pdf_report

app = Flask(__name__)
DB_PATH = "mfd.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            income REAL,
            risk_appetite TEXT DEFAULT 'Moderate',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            fund_name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            expected_return REAL DEFAULT 12.0,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
    """)
    conn.commit()
    conn.close()

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/clients")
def clients_page():
    return render_template("clients.html")

@app.route("/portfolio/<int:client_id>")
def portfolio_page(client_id):
    return render_template("portfolio.html", client_id=client_id)

@app.route("/reports")
def reports_page():
    return render_template("reports.html")

def get_clients():
    conn = get_db()
    clients = conn.execute("""
        SELECT c.*, COUNT(i.id) as fund_count, COALESCE(SUM(i.amount),0) as total_invested
        FROM clients c LEFT JOIN investments i ON c.id = i.client_id
        GROUP BY c.id ORDER BY c.created_at DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in clients])

@app.route("/api/clients", methods=["POST"])
def add_client():
    d = request.json
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO clients (name, email, age, income, risk_appetite) VALUES (?,?,?,?,?)",
            (d["name"], d["email"], d.get("age"), d.get("income"), d.get("risk_appetite","Moderate"))
        )
        conn.commit()
        client_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return jsonify({"success": True, "id": client_id})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "error": "Email already exists"}), 400

@app.route("/api/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(client))

@app.route("/api/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    conn = get_db()
    conn.execute("DELETE FROM investments WHERE client_id=?", (client_id,))
    conn.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/investments/<int:client_id>", methods=["GET"])
def get_investments(client_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM investments WHERE client_id=? ORDER BY date DESC", (client_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/investments", methods=["POST"])
def add_investment():
    d = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO investments (client_id, fund_name, amount, category, date, expected_return) VALUES (?,?,?,?,?,?)",
        (d["client_id"], d["fund_name"], d["amount"], d["category"], d["date"], d.get("expected_return", 12.0))
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/investments/<int:inv_id>", methods=["DELETE"])
def delete_investment(inv_id):
    conn = get_db()
    conn.execute("DELETE FROM investments WHERE id=?", (inv_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/analyze/<int:client_id>")
def analyze(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    investments = conn.execute("SELECT * FROM investments WHERE client_id=?", (client_id,)).fetchall()
    conn.close()
    if not client:
        return jsonify({"error": "Client not found"}), 404
    result = analyze_portfolio(dict(client), [dict(i) for i in investments])
    return jsonify(result)

@app.route("/api/risk/<int:client_id>")
def risk_profile(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": "Not found"}), 404
    result = calculate_risk_profile(dict(client))
    return jsonify(result)

@app.route("/api/recommend/<int:client_id>")
def recommend(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    investments = conn.execute("SELECT * FROM investments WHERE client_id=?", (client_id,)).fetchall()
    conn.close()
    result = generate_recommendations(dict(client), [dict(i) for i in investments])
    return jsonify(result)

@app.route("/api/wealth/<int:client_id>")
def wealth(client_id):
    years = int(request.args.get("years", 10))
    conn = get_db()
    investments = conn.execute("SELECT * FROM investments WHERE client_id=?", (client_id,)).fetchall()
    conn.close()
    result = predict_wealth([dict(i) for i in investments], years)
    return jsonify(result)

@app.route("/api/dashboard")
def dashboard_stats():
    conn = get_db()
    total_clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    total_aum     = conn.execute("SELECT COALESCE(SUM(amount),0) FROM investments").fetchone()[0]
    total_funds   = conn.execute("SELECT COUNT(*) FROM investments").fetchone()[0]
    cat_dist      = conn.execute("""
        SELECT category, SUM(amount) as total FROM investments GROUP BY category ORDER BY total DESC
    """).fetchall()
    recent_clients = conn.execute("""
        SELECT c.name, c.email, COALESCE(SUM(i.amount),0) as aum
        FROM clients c LEFT JOIN investments i ON c.id=i.client_id
        GROUP BY c.id ORDER BY c.created_at DESC LIMIT 5
    """).fetchall()
    conn.close()
    return jsonify({
        "total_clients": total_clients,
        "total_aum": total_aum,
        "total_funds": total_funds,
        "category_distribution": [dict(r) for r in cat_dist],
        "recent_clients": [dict(r) for r in recent_clients]
    })

@app.route("/api/report/<int:client_id>")
def generate_report(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    investments = conn.execute("SELECT * FROM investments WHERE client_id=?", (client_id,)).fetchall()
    conn.close()
    if not client:
        return jsonify({"error": "Not found"}), 404
    analysis     = analyze_portfolio(dict(client), [dict(i) for i in investments])
    risk         = calculate_risk_profile(dict(client))
    recs         = generate_recommendations(dict(client), [dict(i) for i in investments])
    wealth_data  = predict_wealth([dict(i) for i in investments], 10)
    pdf_path     = generate_pdf_report(dict(client), [dict(i) for i in investments], analysis, risk, recs, wealth_data)
    return send_file(pdf_path, as_attachment=True, download_name=f"report_{client['name'].replace(' ','_')}.pdf")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)