# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ===================== MODELS =====================
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer)
    is_available = db.Column(db.Boolean, default=True)
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("table.id"))
    customer_name = db.Column(db.String(100))
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"))
    quantity = db.Column(db.Integer)

# ===================== APIs =====================
# View Menu
@app.route("/api/menu", methods=["GET"])
def view_menu():
    items = MenuItem.query.all()
    return jsonify([
        {"id": i.id, "name": i.name, "price": i.price, "stock": i.stock}
        for i in items
    ])
# Add Menu Item
@app.route("/api/menu", methods=["POST"])
def add_menu():
    data = request.json
    item = MenuItem(**data)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Menu item added"})
# Place Order
@app.route("/api/orders", methods=["POST"])
def place_order():
    data = request.json
    total = 0
    order = Order(total_price=0)
    db.session.add(order)
    db.session.commit()
    for item in data["items"]:
        menu = MenuItem.query.get(item["menu_item_id"])
        if menu.stock < item["quantity"]:
            return jsonify({"error": "Insufficient stock"}), 400
        menu.stock -= item["quantity"]
        total += menu.price * item["quantity"]
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu.id,
            quantity=item["quantity"]
        )
        db.session.add(order_item)
    order.total_price = total
    db.session.commit()
    return jsonify({"order_id": order.id, "total": total})
# Reserve Table
@app.route("/api/reserve", methods=["POST"])
def reserve_table():
    data = request.json
    table = Table.query.filter_by(is_available=True).filter(Table.capacity >= data["people"]).first()
    if not table:
        return jsonify({"error": "No table available"}), 400
    table.is_available = False
    reservation = Reservation(
        table_id=table.id,
        customer_name=data["customer_name"]
    )
    db.session.add(reservation)
    db.session.commit()
    return jsonify({"message": "Table reserved", "table_id": table.id})
# Add Table
@app.route("/api/tables", methods=["POST"])
def add_table():
    table = Table(**request.json)
    db.session.add(table)
    db.session.commit()
    return jsonify({"message": "Table added"})
# Update Inventory
@app.route("/api/inventory/<int:item_id>", methods=["PUT"])
def update_inventory(item_id):
    item = MenuItem.query.get(item_id)
    item.stock = request.json["stock"]
    db.session.commit()
    return jsonify({"message": "Inventory updated"})
# Daily Sales Report
@app.route("/api/reports/daily-sales", methods=["GET"])
def daily_sales():
    today = date.today()
    orders = Order.query.filter(db.func.date(Order.created_at) == today).all()
    total = sum(o.total_price for o in orders)
    return jsonify({"date": str(today), "total_sales": total})
# Stock Alert
@app.route("/api/reports/low-stock", methods=["GET"])
def low_stock():
    items = MenuItem.query.filter(MenuItem.stock < 5).all()
    return jsonify([
        {"id": i.id, "name": i.name, "stock": i.stock}
        for i in items
    ])

# ===================== RUN =====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)