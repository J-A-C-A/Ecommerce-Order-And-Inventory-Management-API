import pytest

@pytest.mark.asyncio
async def test_create_order_status(client, created_cart_with_item, customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country",}
    response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    print(response.json())
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    assert data["total_order_price"] == "20.00"
    assert data["order_items"][0]["product_quantity"] == 2

@pytest.mark.asyncio
async def test_create_order_empty_cart_fails(client, customer_auth_headers):
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country",}
    response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_order_reserves_stock(client,created_cart_with_item,admin_auth_headers ,customer_auth_headers):
    cart_data = created_cart_with_item
    product_id = cart_data["product"]["product_id"]
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country",}
    cart_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert cart_response.status_code == 201
    inventory_response = await client.get(f"/inventory/{product_id}", headers=admin_auth_headers)
    assert inventory_response.status_code == 200
    data = inventory_response.json()
    assert data["quantity_reserved"] == 2

@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client,created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    product_id = cart_data["product"]["product_id"]
    cart_response = await client.patch(f"/cart/items/{product_id}", json={"product_quantity": 12}, headers=customer_auth_headers)
    assert cart_response.status_code == 200
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country",}
    response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_create_order_clears_cart(client,created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    order_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert order_response.status_code == 201

    response = await client.get("/cart",headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["cart_items"]) == 0

@pytest.mark.asyncio
async def test_get_order_by_id_success(client,created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    post_data = post_response.json()
    order_id = post_data["order_id"]
    response = await client.get(f"/orders/{order_id}", headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["total_order_price"] == "20.00"
    assert data["street"] == payload["street"]
    assert data["building_number"] == payload["building_number"]
    assert data["apartment_number"] == payload["apartment_number"]
    assert data["postal_code"] == payload["postal_code"]
    assert data["city"] == payload["city"]
    assert data["country"] == payload["country"]

@pytest.mark.asyncio
async def test_get_order_forbidden_for_other_user(client, created_cart_with_item,customer_auth_headers, second_customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    post_data = post_response.json()
    order_id = post_data["order_id"]
    response = await client.get(f"/orders/{order_id}", headers=second_customer_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_all_orders_for_user(client,created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    product_id = cart_data["product"]["product_id"]
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response1 = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response1.status_code == 201
    cart_response = await client.post("/cart/items",json={"product_id": product_id,"product_quantity": 1},headers=customer_auth_headers)
    assert cart_response.status_code == 201
    post_response2 = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response2.status_code == 201
    response = await client.get("/orders", headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_pay_order_success(client,created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    post_data = post_response.json()
    order_id = post_data["order_id"]
    response = await client.post(f"/orders/{order_id}/pay", headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Paid"

@pytest.mark.asyncio
async def test_pay_order_wrong_status_fails(client, created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    post_data = post_response.json()
    order_id = post_data["order_id"]
    paid_response = await client.post(f"/orders/{order_id}/pay", headers=customer_auth_headers)
    assert paid_response.status_code == 200
    data = paid_response.json()
    assert data["status"] == "Paid"
    response = await client.post(f"/orders/{order_id}/pay", headers=customer_auth_headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_cancel_order(client,created_cart_with_item,customer_auth_headers):
    cart_data = created_cart_with_item
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    post_data = post_response.json()
    order_id = post_data["order_id"]
    response = await client.post(f"/orders/{order_id}/cancel",headers=customer_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Canceled"

@pytest.mark.asyncio
async def test_cancel_order_releases_stock(client,created_cart_with_item,customer_auth_headers,admin_auth_headers):
    cart_data = created_cart_with_item
    product_id = cart_data["product"]["product_id"]
    payload = {"street": "Przykładowa",
               "building_number": "1",
               "apartment_number": "1",
               "postal_code": "01-001",
               "city": "Default city",
               "country": "Default country", }
    post_response = await client.post("/orders", json=payload, headers=customer_auth_headers)
    assert post_response.status_code == 201
    post_data = post_response.json()
    order_id = post_data["order_id"]
    cancel_response = await client.post(f"/orders/{order_id}/cancel", headers=customer_auth_headers)
    assert cancel_response.status_code == 200
    cancel_data = cancel_response.json()
    assert cancel_data["status"] == "Canceled"
    response = await client.get(f"/inventory/{product_id}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["quantity_total"] == 10
    assert data["quantity_reserved"] == 0

@pytest.mark.asyncio
async def test_admin_update_order_status_success(client,created_cart_with_item,customer_auth_headers,admin_auth_headers):
    payload = {
        "street": "Przykładowa",
        "building_number": "1",
        "apartment_number": "1",
        "postal_code": "01-001",
        "city": "Default city",
        "country": "Default country",}

    order_response = await client.post("/orders",json=payload,headers=customer_auth_headers)
    assert order_response.status_code == 201
    order_data = order_response.json()
    order_id = order_data["order_id"]
    assert order_data["status"] == "Pending"

    paid_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Paid"},headers=admin_auth_headers)
    assert paid_response.status_code == 200
    assert paid_response.json()["status"] == "Paid"

    shipped_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Shipped"},headers=admin_auth_headers)
    assert shipped_response.status_code == 200
    assert shipped_response.json()["status"] == "Shipped"

    delivered_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Delivered"},headers=admin_auth_headers)
    assert delivered_response.status_code == 200
    assert delivered_response.json()["status"] == "Delivered"


@pytest.mark.asyncio
async def test_admin_update_order_status_invalid_transition(client,created_cart_with_item,customer_auth_headers,admin_auth_headers):
    payload = {
        "street": "Przykładowa",
        "building_number": "1",
        "apartment_number": "1",
        "postal_code": "01-001",
        "city": "Default city",
        "country": "Default country",}

    order_response = await client.post("/orders",json=payload,headers=customer_auth_headers)
    assert order_response.status_code == 201
    order_data = order_response.json()
    order_id = order_data["order_id"]
    assert order_data["status"] == "Pending"

    delivered_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Delivered"},headers=admin_auth_headers)
    assert delivered_response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_shipped_order_fails(client,created_cart_with_item,customer_auth_headers,admin_auth_headers):
    payload = {
        "street": "Przykładowa",
        "building_number": "1",
        "apartment_number": "1",
        "postal_code": "01-001",
        "city": "Default city",
        "country": "Default country",}
    order_response = await client.post("/orders",json=payload,headers=customer_auth_headers)
    assert order_response.status_code == 201
    order_data = order_response.json()
    order_id = order_data["order_id"]
    assert order_data["status"] == "Pending"

    paid_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Paid"},headers=admin_auth_headers)
    assert paid_response.status_code == 200

    shipped_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Shipped"},headers=admin_auth_headers)
    assert shipped_response.status_code == 200

    cancel_response = await client.post(f"/orders/{order_id}/cancel",headers=customer_auth_headers)
    assert cancel_response.status_code == 400

@pytest.mark.asyncio
async def test_cancel_delivered_order_fails(client,created_cart_with_item,customer_auth_headers,admin_auth_headers):
    payload = {
        "street": "Przykładowa",
        "building_number": "1",
        "apartment_number": "1",
        "postal_code": "01-001",
        "city": "Default city",
        "country": "Default country",}
    order_response = await client.post("/orders",json=payload,headers=customer_auth_headers)
    assert order_response.status_code == 201
    order_data = order_response.json()
    order_id = order_data["order_id"]
    assert order_data["status"] == "Pending"

    paid_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Paid"},headers=admin_auth_headers)
    assert paid_response.status_code == 200

    shipped_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Shipped"},headers=admin_auth_headers)
    assert shipped_response.status_code == 200

    delivered_response = await client.patch(f"/orders/{order_id}/status",json={"status": "Delivered"},headers=admin_auth_headers)
    assert delivered_response.status_code == 200

    cancel_response = await client.post(f"/orders/{order_id}/cancel",headers=customer_auth_headers)
    assert cancel_response.status_code == 400