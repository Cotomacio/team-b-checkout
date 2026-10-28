"""Team B — E-Commerce Checkout & Order Fulfillment Microservice."""

import os
import re
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
    sql = "SELECT code, discount_percent, active FROM promotions WHERE code = ? AND active = 1"
    cursor.execute(sql, (promo_code,))
    promo = cursor.fetchone()
    conn.close()
    if not promo:
        return jsonify({"valid": False, "error": "Invalid or expired promo code"}), 404
    return jsonify({"valid": True, "promotion": dict(promo)})


@app.route("/api/v1/checkout/invoice/download", methods=["GET"])
def download_invoice_template():
    """Load an HTML invoice template by file name."""
    template_name = request.args.get("template", "standard.html")
    if (
        not isinstance(template_name, str)
        or not template_name
        or "\0" in template_name
        or "/" in template_name
        or "\\" in template_name
    ):
        return jsonify({"error": "Invalid template"}), 400
    filename = os.path.basename(template_name)
    base_dir = os.path.realpath(INVOICE_DIR)
    target_path = os.path.realpath(os.path.join(base_dir, filename))
    if not target_path.startswith(base_dir + os.sep):
        return jsonify({"error": "Invalid template"}), 400
    with open(target_path, "r", encoding="utf-8") as handle:
        content = handle.read()
    return jsonify({"template": template_name, "html": content})


@app.route("/api/v1/checkout/shipping/label", methods=["POST"])
def generate_shipping_label():
    """Render a PDF shipping label for an order ID."""
    payload = request.get_json(silent=True) or {}
    order_id = payload.get("order_id", "ORD-0000")
    if not isinstance(order_id, str) or not re.match(r"^[A-Za-z0-9_-]+$", order_id):
        return jsonify({"error": "Invalid order_id"}), 400
    cmd = [
        "wkhtmltopdf",
        f"/var/checkout/orders/{order_id}.html",
        f"/tmp/label-{order_id}.pdf",
    ]
    result = subprocess.check_output(cmd, text=True)
    return jsonify({"status": "generated", "order_id": order_id, "log": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
