import pytest
from app import create_app, db
from app.models import Order, OrderItem

# Fixture para configurar la aplicación en modo de pruebas
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"  # Base de datos aislada en memoria
    })

    with app.app_context():
        db.create_all()  # Crea las tablas antes de las pruebas
        yield app
        db.session.remove()
        db.drop_all()    # Limpia todo al terminar

# Fixture para simular un cliente HTTP (como Postman o Frontend)
@pytest.fixture
def client(app):
    return app.test_client()


# --- PRUEBAS UNITARIAS ---

# 1. Probar la creación exitosa de un pedido
def test_create_order_success(client):
    payload = {
        "customer_name": "Juan Pérez",
        "items": [
            {"product_name": "Producto A", "quantity": 2, "price": 15.0},
            {"product_name": "Producto B", "quantity": 1, "price": 10.0}
        ]
    }
    response = client.post('/api/orders', json=payload)
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['customer_name'] == "Juan Pérez"
    assert data['status'] == "PENDING"
    assert len(data['items']) == 2

# 2. Probar error al intentar crear un pedido sin datos obligatorios
def test_create_order_invalid_data(client):
    payload = {
        "customer_name": "Juan Pérez"
        # Falta la lista de ítems (productos)
    }
    response = client.post('/api/orders', json=payload)
    assert response.status_code == 400

# 3. Probar la consulta de la lista de pedidos
def test_get_orders(client):
    # Primero insertamos un pedido de prueba
    payload = {
        "customer_name": "Carlos Gómez",
        "items": [{"product_name": "Producto C", "quantity": 1, "price": 5.0}]
    }
    client.post('/api/orders', json=payload)

    # Hacemos la consulta GET
    response = client.get('/api/orders')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['customer_name'] == "Carlos Gómez"

# 4. Probar la actualización exitosa de estado de un pedido
def test_update_order_status_success(client):
    # Creamos un pedido inicial
    payload = {
        "customer_name": "Ana Martínez",
        "items": [{"product_name": "Producto D", "quantity": 1, "price": 20.0}]
    }
    create_res = client.post('/api/orders', json=payload)
    order_id = create_res.get_json()['id']

    # Actualizamos su estado a SHIPPED
    status_payload = {"status": "SHIPPED"}
    response = client.patch(f'/api/orders/{order_id}/status', json=status_payload)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == "SHIPPED"

# 5. Probar error al pasar un estado que no está permitido
def test_update_order_status_invalid(client):
    payload = {
        "customer_name": "Ana Martínez",
        "items": [{"product_name": "Producto D", "quantity": 1, "price": 20.0}]
    }
    create_res = client.post('/api/orders', json=payload)
    order_id = create_res.get_json()['id']

    # Intentamos pasar un estado inválido como "ENTREGADO" en vez de "DELIVERED"
    status_payload = {"status": "ENTREGADO"}
    response = client.patch(f'/api/orders/{order_id}/status', json=status_payload)
    assert response.status_code == 400