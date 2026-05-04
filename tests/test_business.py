# tests/test_business.py
# Tests for all /businesses/ endpoints.
#
# HOW PYTEST WORKS:
# - Every function starting with "test_" is automatically picked up and run by pytest
# - The "client" parameter is automatically injected by the fixture in conftest.py
# - Tests are completely independent - the DB is wiped between each one (see conftest.py)
#
# HOW TO ADD MORE TESTS:
# 1. Write a new function starting with test_
# 2. Give it a descriptive name: test_<what youre testing>_<expected outcome>
# 3. Use the helper functions at the top to set up any data you need
# 4. Make your HTTP request using the client
# 5. Assert the response status code and any data you care about

from fastapi.testclient import TestClient


# ── Helper Functions ───────────────────────────────────────────────────────────
# These are NOT tests (they don't start with test_).
# They are reusable shortcuts so we don't repeat the same setup code in every test.
# Any test that needs an existing business in the DB just calls create_business(client).

def create_business(client: TestClient, name: str = "Test Farm", code: str = "TF001"):
    """Creates a business via the API and returns the full response object.
    Default values mean you can call create_business(client) for a quick setup,
    or override them: create_business(client, name="Other Farm", code="OF001")
    """
    return client.post("/businesses/", json={"name": name, "code": code})


# ── Create Tests ───────────────────────────────────────────────────────────────
# Testing POST /businesses/
# We test: the happy path, duplicate codes, and invalid input

def test_create_business_success(client):
    # Happy path - valid data should create a business and return 201 Created
    response = create_business(client)

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Farm"
    assert data["code"] == "TF001"
    assert "id" in data               # check a UUID was generated
    assert "created_at" in data       # check timestamps were set by the DB


def test_create_business_code_uppercased(client):
    # The schema validator should uppercase the code before saving
    response = client.post("/businesses/", json={"name": "Test Farm", "code": "tf001"})

    assert response.status_code == 201
    assert response.json()["code"] == "TF001"   # lowercase input, uppercase stored


def test_create_business_duplicate_code(client):
    # Two businesses with the same code should be rejected - code is unique in the DB
    create_business(client)                     # first one succeeds
    response = create_business(client)          # second one with same code should fail

    assert response.status_code == 409          # 409 Conflict - already exists


def test_create_business_empty_name(client):
    # Schema validation: name cannot be an empty string (min_length=1)
    response = client.post("/businesses/", json={"name": "", "code": "TF001"})

    assert response.status_code == 422          # 422 Unprocessable Entity - failed validation


def test_create_business_empty_code(client):
    # Schema validation: code cannot be an empty string (min_length=1)
    response = client.post("/businesses/", json={"name": "Test Farm", "code": ""})

    assert response.status_code == 422


def test_create_business_code_too_long(client):
    # Schema validation: code has a max_length of 5
    response = client.post("/businesses/", json={"name": "Test Farm", "code": "TOOLONG"})

    assert response.status_code == 422


def test_create_business_missing_fields(client):
    # Schema validation: both name and code are required, sending neither should fail
    response = client.post("/businesses/", json={})

    assert response.status_code == 422


# ── List Tests ─────────────────────────────────────────────────────────────────
# Testing GET /businesses/
# We test: empty list, and that all created records come back

def test_list_businesses_empty(client):
    # When no businesses exist the endpoint should return an empty list, not an error
    response = client.get("/businesses/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_businesses_returns_all(client):
    # Create two businesses and check both come back in the list
    create_business(client, name="Farm One", code="F001")
    create_business(client, name="Farm Two", code="F002")

    response = client.get("/businesses/")

    assert response.status_code == 200
    assert len(response.json()) == 2            # exactly 2 records, no more, no less


# ── Get By ID Tests ────────────────────────────────────────────────────────────
# Testing GET /businesses/{business_id}
# We test: finding an existing record, a missing record, and a malformed UUID

def test_get_business_by_id_success(client):
    # Create a business, capture its ID, then fetch it back by that ID
    business_id = create_business(client).json()["id"]

    response = client.get(f"/businesses/{business_id}")

    assert response.status_code == 200
    assert response.json()["id"] == business_id     # confirm we got the right record back


def test_get_business_by_id_not_found(client):
    # A valid UUID that doesnt exist in the DB should return 404
    # We use the all-zeros UUID as a safe "definitely doesnt exist" value
    response = client.get("/businesses/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_get_business_invalid_uuid(client):
    # A string that isnt a UUID at all should be rejected before hitting the DB
    response = client.get("/businesses/not-a-uuid")

    assert response.status_code == 422             # FastAPI rejects it at the type hint level


# ── Update Tests ───────────────────────────────────────────────────────────────
# Testing PATCH /businesses/{business_id}
# We test: updating name, updating code, duplicate code conflict, and not found

def test_update_business_name(client):
    # Create a business then update just the name, code should remain unchanged
    business = create_business(client).json()
    business_id = business["id"]

    response = client.patch(f"/businesses/{business_id}", json={"name": "Updated Farm"})

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Farm"
    assert response.json()["code"] == "TF001"       # code was not in the patch, should be unchanged


def test_update_business_code(client):
    # Update just the code, name should remain unchanged
    business_id = create_business(client).json()["id"]

    response = client.patch(f"/businesses/{business_id}", json={"code": "UPD01"})

    assert response.status_code == 200
    assert response.json()["code"] == "UPD01"
    assert response.json()["name"] == "Test Farm"   # name was not in the patch, should be unchanged


def test_update_business_duplicate_code(client):
    # Trying to update a business to a code that another business already has should fail
    create_business(client, name="Farm One", code="F001")
    business_id_2 = create_business(client, name="Farm Two", code="F002").json()["id"]

    # Try to change Farm Two's code to F001 which Farm One already has
    response = client.patch(f"/businesses/{business_id_2}", json={"code": "F001"})

    assert response.status_code == 409


def test_update_business_not_found(client):
    # Trying to update a business that doesnt exist should return 404
    response = client.patch(
        "/businesses/00000000-0000-0000-0000-000000000000",
        json={"name": "Ghost Farm"}
    )

    assert response.status_code == 404


# ── Delete Tests ───────────────────────────────────────────────────────────────
# Testing DELETE /businesses/{business_id}
# We test: successful delete, not found, and the FK protection (cant delete if sites exist)

def test_delete_business_success(client):
    # Create a business with no linked sites, delete should succeed
    business_id = create_business(client).json()["id"]

    response = client.delete(f"/businesses/{business_id}")

    assert response.status_code == 200


def test_delete_business_confirm_gone(client):
    # After deleting, trying to fetch the same business by ID should return 404
    business_id = create_business(client).json()["id"]
    client.delete(f"/businesses/{business_id}")

    response = client.get(f"/businesses/{business_id}")

    assert response.status_code == 404             # confirms the delete actually worked


def test_delete_business_not_found(client):
    # Trying to delete a business that doesnt exist should return 404
    response = client.delete("/businesses/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_delete_business_with_linked_site(client):
    # If a business has sites linked to it via FK, deleting it should be blocked
    # This tests the foreign_key_remove_fail helper in your routes
    business_id = create_business(client).json()["id"]

    # Create a site linked to this business
    client.post("/sites/", json={
        "name": "North Field",
        "code": "NF001",
        "business_id": business_id
    })

    # Now try to delete the business - should be blocked by FK constraint
    response = client.delete(f"/businesses/{business_id}")

    assert response.status_code == 409             # 409 Conflict - has dependants

