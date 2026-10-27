
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import db, User, Statements, Admin
from app.functions import get_base64_encode


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("DB_URI", "sqlite://")

    test_app = create_app()
    test_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key",
    )

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(
    app,
    email="test@example.com",
    password="Password123",
    name="Test User",
):
    with app.app_context():
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(
                password, method="pbkdf2:sha256"
            ),
            session_id=f"session-{email}",
        )
        db.session.add(user)
        db.session.commit()

        return {
            "id": user.id,
            "session_id": user.session_id,
            "email": user.email,
        }


def login_test_user(client, session_id):
    with client.session_transaction() as session:
        session["session-sign-id"] = get_base64_encode(session_id)


def test_home_redirects_when_user_is_not_logged_in(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/auth/" in response.headers["Location"]


def test_registration_creates_a_user(app, client):
    response = client.post(
        "/auth/",
        data={
            "email": "newuser@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(
            email="newuser@example.com"
        ).first()

        assert user is not None
        assert user.name == "newuser"
        assert user.password != "Password123"


def test_valid_login_redirects_to_home(app, client):
    create_user(app)

    response = client.post(
        "/auth/",
        data={
            "email": "test@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_invalid_password_does_not_log_user_in(app, client):
    create_user(app)

    response = client.post(
        "/auth/",
        data={
            "email": "test@example.com",
            "password": "WrongPass123",
        },
    )

    assert response.status_code == 302
    assert "/auth/" in response.headers["Location"]

    with client.session_transaction() as session:
        assert "session-sign-id" not in session


def test_income_statement_is_saved_as_positive_amount(app, client):
    user = create_user(app)
    login_test_user(client, user["session_id"])

    response = client.post(
        "/new",
        data={
            "amount": "2500",
            "description": "Monthly salary",
            "datetime_data": "2026-10-27T10:00",
            "income": "Add Income",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        statement = Statements.query.filter_by(
            user_id=user["id"]
        ).first()

        assert statement is not None
        assert float(statement.amount) == 2500.00
        assert statement.description == "Monthly salary"


def test_expense_statement_is_saved_as_negative_amount(app, client):
    user = create_user(app)
    login_test_user(client, user["session_id"])

    response = client.post(
        "/new",
        data={
            "amount": "450",
            "description": "Grocery shopping",
            "datetime_data": "2026-10-27T11:00",
            "expense": "Add Expense",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        statement = Statements.query.filter_by(
            user_id=user["id"]
        ).first()

        assert statement is not None
        assert float(statement.amount) == -450.00
        assert statement.description == "Grocery shopping"


def test_csv_export_contains_user_statement(app, client):
    user = create_user(app)
    login_test_user(client, user["session_id"])

    with app.app_context():
        statement = Statements(
            description="Freelance payment",
            amount=1200.00,
            statement_id="test-statement-001",
            user_id=user["id"],
        )
        db.session.add(statement)
        db.session.commit()

    response = client.get("/download-statements")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"

    body = response.get_data(as_text=True)

    assert "Freelance payment" in body
    assert "income" in body


def test_admin_dashboard_requires_admin_session(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_can_log_in_and_open_dashboard(app, client):
    with app.app_context():
        admin = Admin(
            username="Test Admin",
            email="admin@example.com",
            password=generate_password_hash(
                "AdminPass123", method="pbkdf2:sha256"
            ),
            session_id="admin-session-test",
        )
        db.session.add(admin)
        db.session.commit()

    login_response = client.post(
        "/admin/login",
        data={
            "email": "admin@example.com",
            "password": "AdminPass123",
        },
    )

    assert login_response.status_code == 302

    dashboard_response = client.get("/admin/")

    assert dashboard_response.status_code == 200
