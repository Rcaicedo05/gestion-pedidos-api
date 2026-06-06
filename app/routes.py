from flask import Blueprint, request, jsonify
from app import db, ma
from app.models import Order, OrderItem

# Definimos el Blueprint para agrupar las rutas de la API
orders_bp = Blueprint('orders', __name__)

# --- Esquemas de Serialización (Transforman objetos de BD a JSON) ---
class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        load_instance = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        include_relationships = True
    
    # Esto permite que al ver un pedido se incluyan todos sus productos asociados
    items = ma.Nested(OrderItemSchema, many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


# --- Endpoints de la API ---

# 1. Crear un Pedido (POST /api/orders)
@orders_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    if not data or 'customer_name' not in data or 'items' not in data:
        return jsonify({'error': 'Datos de solicitud incompletos o inválidos'}), 400
        
    # Crear la cabecera del pedido
    new_order = Order(
        customer_name=data['customer_name'],
        status='PENDING' # Todo pedido inicia en estado PENDING
    )
    
    # Agregar los productos (items) vinculados al pedido
    for item in data['items']:
        order_item = OrderItem(
            product_name=item['product_name'],
            quantity=item['quantity'],
            price=item['price']
        )
        new_order.items.append(order_item)
        
    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201


# 2. Obtener todos los Pedidos (GET /api/orders)
@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    all_orders = Order.query.all()
    return orders_schema.jsonify(all_orders), 200


# 3. Actualizar el Estado de un Pedido (PATCH /api/orders/<id>/status)
@orders_bp.route('/orders/<int:id>/status', methods=['PATCH'])
def update_order_status(id):
    order = Order.query.get_or_404(id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Debe proporcionar el campo status'}), 400
        
    # Validar que solo se permitan los estados requeridos en el taller
    allowed_statuses = ['PENDING', 'SHIPPED', 'DELIVERED']
    new_status = data['status'].upper()
    
    if new_status not in allowed_statuses:
        return jsonify({'error': f'Estado inválido. Permitidos: {allowed_statuses}'}), 400
        
    order.status = new_status
    db.session.commit()
    
    return order_schema.jsonify(order), 200