@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True)

    name = data.get("name")
    sku = data.get("sku")
    price = Decimal(str(data.get("price")))
    warehouse_id = data.get("warehouse_id")
    initial_quantity = data.get("initial_quantity", 0)

    existing = db.session.execute(
        select(Product.id).where(Product.sku == sku)
    ).first()
    if existing:
        return jsonify({"error": "SKU already exists"}), 409

    product = Product(
        name=name,
        sku=sku,
        price=price
    )

    db.session.add(product)
    db.session.flush()

    inventory = Inventory(
        product_id=product.id,
        warehouse_id=warehouse_id,
        quantity=initial_quantity
    )

    db.session.add(inventory)
    db.session.commit()

    return jsonify(
        {
            "message": "Product created",
            "product_id": product.id
        }
    ), 201
