import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.dependencies.database import Base, get_db
from api.models.sandwiches import Sandwich

# Test DB setup (SQLite file)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_guestorders.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the real DB dependency with the test one
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Pytest fixtures

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_sandwich(db_session):
    sandwich = Sandwich(
        name="Classic Veggie Sandwich",
        price=7.99
    )
    db_session.add(sandwich)
    db_session.commit()
    db_session.refresh(sandwich)
    return sandwich

# Tests

def test_create_guest_order_success(sample_sandwich):
    payload = {
        "guest_name": "Bob",
        "contact_phone": "555-123-4567",
        "contact_email": "gurleen@example.com",
        "table_number": 12,
        "notes": "No nuts, please.",
        "items": [
            {
                "menu_item_id": sample_sandwich.id,
                "quantity": 2,
                "special_requests": "Extra spicy, no onions"
            }
        ]
    }

    response = client.post("/guestorders/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["guest_name"] == "Bob"
    assert data["status"] == "pending"
    assert data["code"].startswith("ORD-")

    # Price checks
    assert data["subtotal"] == pytest.approx(2 * float(sample_sandwich.price), rel=1e-3)
    assert data["total_price"] == pytest.approx(data["subtotal"], rel=1e-3)

    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["menu_item_id"] == sample_sandwich.id
    assert item["name"] == "Classic Veggie Sandwich"
    assert item["quantity"] == 2
    assert item["unit_price"] == pytest.approx(float(sample_sandwich.price), rel=1e-3)


def test_create_guest_order_invalid_sandwich_id():
    payload = {
        "guest_name": "Test",
        "items": [
            {
                "menu_item_id": 9999,
                "quantity": 1
            }
        ]
    }

    response = client.post("/guestorders/", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Sandwich IDs not found" in data["detail"]


def test_create_guest_order_with_no_items():
    payload = {
        "guest_name": "Test",
        "items": []
    }

    response = client.post("/guestorders/", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Order must contain at least one item."


def test_get_guest_order_by_id(sample_sandwich):
    create_payload = {
        "guest_name": "Alice",
        "contact_phone": "555-111-2222",
        "contact_email": "alice@example.com",
        "table_number": 5,
        "notes": "Window seat",
        "items": [
            {
                "menu_item_id": sample_sandwich.id,
                "quantity": 1
            }
        ]
    }
    create_resp = client.post("/guestorders/", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    order_id = created["id"]

    get_resp = client.get(f"/guestorders/{order_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()

    assert data["id"] == order_id
    assert data["guest_name"] == "Alice"
    assert data["items"][0]["quantity"] == 1


def test_get_guest_order_by_code(sample_sandwich):
    create_payload = {
        "guest_name": "Charlie",
        "contact_phone": "555-222-3333",
        "contact_email": "charlie@example.com",
        "table_number": 9,
        "notes": "Birthday",
        "items": [
            {
                "menu_item_id": sample_sandwich.id,
                "quantity": 3
            }
        ]
    }
    create_resp = client.post("/guestorders/", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    code = created["code"]

    lookup_resp = client.get(f"/guestorders/lookup?code={code}")
    assert lookup_resp.status_code == 200
    data = lookup_resp.json()

    assert data["code"] == code
    assert data["guest_name"] == "Charlie"
    assert data["items"][0]["quantity"] == 3
