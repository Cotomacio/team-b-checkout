"""Team B — E-Commerce Checkout & Order Fulfillment Microservice."""

import os
import sqlite3
import subprocess
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.environ.get("CHECKOUT_DB", "/tmp/checkout.db")
INVOICE_DIR = "/var/checkout/invoices"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api/v1/checkout/promo", methods=["GET"])
def validate_promo_code():
    """Validate a promotional discount code during checkout."""
    promo_code = request.args.get("code", "")
    conn = get_db()
    cursor = conn.cursor()
    # Vulnerable to SQL Injection (CWE-89): unsanitized string interpolation
    sql = f"SELECT code, discount_percent, active FROM promotions WHERE code = '{promo_code}' AND active = 1"
    cursor.execute(sql)
    promo = cursor.fetchone()
    conn.close()
    if not promo:
        return jsonify({"valid": False, "error": "Invalid or expired promo code"}), 404
    return jsonify({"valid": True, "promotion": dict(promo)})


@app.route("/api/v1/checkout/invoice/download", methods=["GET"])
def download_invoice_template():
    """Load an HTML invoice template by file name."""
    template_name = request.args.get("template", "standard.html")
    # Vulnerable to Path Traversal (CWE-22): unsanitized path concatenation
    target_path = f"{INVOICE_DIR}/{template_name}"
    with open(target_path, "r", encoding="utf-8") as handle:
        content = handle.read()
    return jsonify({"template": template_name, "html": content})


@app.route("/api/v1/checkout/shipping/label", methods=["POST"])
def generate_shipping_label():
    """Render a PDF shipping label for an order ID."""
    payload = request.get_json(silent=True) or {}
    order_id = payload.get("order_id", "ORD-0000")
    # Vulnerable to OS Command Injection (CWE-78): shell=True with user-controlled order_id
    cmd = f"wkhtmltopdf /var/checkout/orders/{order_id}.html /tmp/label-{order_id}.pdf"
    result = subprocess.check_output(cmd, shell=True, text=True)
    return jsonify({"status": "generated", "order_id": order_id, "log": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
