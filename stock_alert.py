@app.route("/api/companies/<int:company_id>/alerts/low-stock", methods=["GET"])
def low_stock_alerts(company_id):
    query = text("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.sku,
            w.id AS warehouse_id,
            w.name AS warehouse_name,
            i.quantity AS current_stock,
            t.threshold,
            CEIL(i.quantity / NULLIF(t.daily_sales, 0)) AS days_until_stockout,
            s.id AS supplier_id,
            s.name AS supplier_name,
            s.contact_email
        FROM inventories i
        JOIN products p ON p.id = i.product_id
        JOIN warehouses w ON w.id = i.warehouse_id
        JOIN suppliers s ON s.id = p.supplier_id
        JOIN product_thresholds t ON t.product_type = p.product_type
        WHERE w.company_id = :company_id
          AND i.quantity < t.threshold
          AND t.daily_sales > 0
    """)

    rows = db.session.execute(query, {"company_id": company_id}).mappings().all()

    alerts = [
        {
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "sku": r["sku"],
            "warehouse_id": r["warehouse_id"],
            "warehouse_name": r["warehouse_name"],
            "current_stock": r["current_stock"],
            "threshold": r["threshold"],
            "days_until_stockout": r["days_until_stockout"],
            "supplier": {
                "id": r["supplier_id"],
                "name": r["supplier_name"],
                "contact_email": r["contact_email"]
            }
        }
        for r in rows
    ]

    return jsonify(
        {
            "alerts": alerts,
            "total_alerts": len(alerts)
        }
    )
