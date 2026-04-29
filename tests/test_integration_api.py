import pytest
import sqlalchemy as sa

from app.models.enums import UserRole
from app.models.user import User

from app.services import order_service as order_service_module


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'



async def _register_and_login(client, email: str, password: str):
    register_response = await client.post(
        '/api/v1/auth/register',
        json={'email': email, 'password': password, 'fullname': 'test user'}
    )
    assert register_response.status_code in (200, 201)

    login_response = await client.post(
        '/api/v1/auth/login',
        json={'email': email, 'password': password}
    )
    assert login_response.status_code == 200
    return login_response.json()['access_token']


@pytest.mark.asyncio
async def test_catalog_cart_order_flow(client, db_session):
    admin_token = await _register_and_login(client, email='admin@example.com', password='admin123')
    customer_token = await _register_and_login(client, email='customer@example.com', password='customer123')

    result = await db_session.execute(
        sa.select(User).where(User.email == 'admin@example.com')
    )
    admin_user = result.scalar_one()
    admin_user.role = UserRole.admin
    await db_session.commit()

    category_response = await client.post(
        '/api/v1/categories/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Book', 'description': 'Category Book'}
    )

    assert category_response.status_code == 201

    category_id = category_response.json()['id']

    product_response = await client.post(
        '/api/v1/products/',
        headers={'Authorization': f'Bearer {admin_token}'},
        data={
            "name": "Test Product",
            "description": "Test Product Description",
            "price": "19.52",
            "stock": 5,
            "category_id": category_id
        }
    )
    assert product_response.status_code == 201
    product_id = product_response.json()['id']

    cart_response = await client.put(
        '/api/v1/cart/items',
        headers={'Authorization': f'Bearer {customer_token}'},
        json={'product_id': product_id, 'quantity': 2}
    )
    assert cart_response.status_code == 200
    assert len(cart_response.json()['items']) == 1

    order_response = await client.post(
        '/api/v1/orders/',
        headers={'Authorization': f'Bearer {customer_token}'},
    )
    assert order_response.status_code == 200
    assert order_response.json()['status'] == 'pending'


