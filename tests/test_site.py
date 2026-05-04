# tests/test_site.py
# Tests for all /sites/ endpoints.
#
# IMPORTANT NOTE ABOUT SITES:
# Sites have a foreign key to businesses (business_id).
# This means almost every site test needs a business to exist first.
# The create_business helper at the top handles this so every test
# can set up its required data in one line before testing the actual thing.
#
# This is a great example of why helper functions are so useful in test files -
# without them every single test would need 4+ lines just to create a business
# before it could even start testing the site behaviour.

from fastapi.testclient import TestClient


# ── Helper Functions ───────────────────────────────────────────────────────────
# create_business is duplicated here from test_business.py intentionally.
# Each test file should be self-contained so it can be read and understood
# on its own without jumping between files.

def create_business(client: TestClient, name: str = "Test Farm", code: str = "TF001"):
    """Creates a business and returns the full response. Used as FK setup for site tests."""
    return client.post("/businesses/", json={"name": name, "code": code})


def create_site(client: TestClient, business_id: str, name: str = "North Field", code: str = "NF001"):
    """Creates a site linked to the given business_id and returns the full response.
    Requires a real business_id from the DB - use create_business(client).json()["id"] to get one.
    """
    return client.post("/sites/", json={"name": name, "code": code, "business_id": business_id})


# ── Create Tests ───────────────────────────────────────────────────────────────
# Testing POST /sites/
# We test: happy path, invalid FK, duplicate code, and validation errors

def test_create_site_success(client):
    # Happy path - create a business first, then create a site linked to it
    business_id = create_business(client).json()["id"]

    response = create_site(client, business_id)

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "North Field"
    assert data["code"] == "NF001"
    assert data["business_id"] == business_id       # confirm the FK was stored correctly
    assert "id" in data                             # confirm a UUID was generated for the site
    assert data["id"] != business_id                # confirm the site ID is NOT the same as business ID


def test_create_site_code_uppercased(client):
    # The schema validator should uppercase the code before saving
    business_id = create_business(client).json()["id"]

    response = client.post("/sites/", json={
        "name": "North Field",
        "code": "nf001",                            # lowercase input
        "business_id": business_id
    })

    assert response.status_code == 201
    assert response.json()["code"] == "NF001"       # should be stored uppercase


def test_create_site_invalid_business_id(client):
    # Providing a business_id that doesnt exist in the DB should fail with FK error
    # We use the all-zeros UUID as a safe "definitely doesnt exist" value
    response = create_site(client, "00000000-0000-0000-0000-000000000000")

    assert response.status_code == 400              # 400 Bad Request - FK constraint failed


def test_create_site_duplicate_code(client):
    # Two sites with the same code should be rejected - code is unique in the DB
    business_id = create_business(client).json()["id"]

    create_site(client, business_id)                # first one succeeds
    response = create_site(client, business_id)     # second one with same code should fail

    assert response.status_code == 409              # 409 Conflict - already exists


def test_create_site_empty_name(client):
    # Schema validation: name cannot be an empty string (min_length=1)
    business_id = create_business(client).json()["id"]

    response = client.post("/sites/", json={"name": "", "code": "NF001", "business_id": business_id})

    assert response.status_code == 422


def test_create_site_code_too_long(client):
    # Schema validation: code has a max_length of 5
    business_id = create_business(client).json()["id"]

    response = client.post("/sites/", json={"name": "North Field", "code": "TOOLONG", "business_id": business_id})

    assert response.status_code == 422


def test_create_site_missing_business_id(client):
    # business_id is required - sending without it should fail schema validation
    response = client.post("/sites/", json={"name": "North Field", "code": "NF001"})

    assert response.status_code == 422


# ── List Tests ─────────────────────────────────────────────────────────────────
# Testing GET /sites/
# We test: empty list, and that all created records come back

def test_list_sites_empty(client):
    # When no sites exist the endpoint should return an empty list, not an error
    response = client.get("/sites/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_sites_returns_all(client):
    # Create two sites (can be under the same business) and check both come back
    business_id = create_business(client).json()["id"]

    create_site(client, business_id, name="North Field", code="NF001")
    create_site(client, business_id, name="South Field", code="SF001")

    response = client.get("/sites/")

    assert response.status_code == 200
    assert len(response.json()) == 2                # exactly 2 records


def test_list_sites_across_businesses(client):
    # Sites from different businesses should all appear in the list together
    business_id_1 = create_business(client, name="Farm One", code="F001").json()["id"]
    business_id_2 = create_business(client, name="Farm Two", code="F002").json()["id"]

    create_site(client, business_id_1, name="North Field", code="NF001")
    create_site(client, business_id_2, name="South Field", code="SF001")

    response = client.get("/sites/")

    assert response.status_code == 200
    assert len(response.json()) == 2


# ── Get By ID Tests ────────────────────────────────────────────────────────────
# Testing GET /sites/{site_id}
# We test: finding an existing record, a missing record, and a malformed UUID

def test_get_site_by_id_success(client):
    # Create a site, capture its ID, then fetch it back by that ID
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    response = client.get(f"/sites/{site_id}")

    assert response.status_code == 200
    assert response.json()["id"] == site_id         # confirm we got the right record back


def test_get_site_by_id_not_found(client):
    # A valid UUID that doesnt exist in the DB should return 404
    response = client.get("/sites/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_get_site_invalid_uuid(client):
    # A string that isnt a UUID at all should be rejected before hitting the DB
    response = client.get("/sites/not-a-uuid")

    assert response.status_code == 422


# ── Update Tests ───────────────────────────────────────────────────────────────
# Testing PATCH /sites/{site_id}
# We test: updating name, updating code, reassigning to a different business,
#          invalid business_id on update, duplicate code conflict, and not found

def test_update_site_name(client):
    # Update just the name, everything else should remain unchanged
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    response = client.patch(f"/sites/{site_id}", json={"name": "Updated Field"})

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Field"
    assert response.json()["code"] == "NF001"       # code was not in the patch, should be unchanged


def test_update_site_code(client):
    # Update just the code, name should remain unchanged
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    response = client.patch(f"/sites/{site_id}", json={"code": "UPD01"})

    assert response.status_code == 200
    assert response.json()["code"] == "UPD01"
    assert response.json()["name"] == "North Field" # name was not in the patch, should be unchanged


def test_update_site_business_id(client):
    # A site can be reassigned to a different business (eg one business takes over another)
    # This tests the business_id field in SitesUpdate
    business_id_1 = create_business(client, name="Farm One", code="F001").json()["id"]
    business_id_2 = create_business(client, name="Farm Two", code="F002").json()["id"]

    site_id = create_site(client, business_id_1).json()["id"]

    # Reassign the site from Farm One to Farm Two
    response = client.patch(f"/sites/{site_id}", json={"business_id": business_id_2})

    assert response.status_code == 200
    assert response.json()["business_id"] == business_id_2  # confirm the FK was updated


def test_update_site_invalid_business_id(client):
    # Trying to reassign a site to a business that doesnt exist should fail
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    response = client.patch(f"/sites/{site_id}", json={
        "business_id": "00000000-0000-0000-0000-000000000000"
    })

    assert response.status_code == 400              # FK constraint failed


def test_update_site_duplicate_code(client):
    # Trying to update a site to a code that another site already has should fail
    business_id = create_business(client).json()["id"]

    create_site(client, business_id, name="North Field", code="NF001")
    site_id_2 = create_site(client, business_id, name="South Field", code="SF001").json()["id"]

    # Try to change South Field's code to NF001 which North Field already has
    response = client.patch(f"/sites/{site_id_2}", json={"code": "NF001"})

    assert response.status_code == 409


def test_update_site_not_found(client):
    # Trying to update a site that doesnt exist should return 404
    response = client.patch(
        "/sites/00000000-0000-0000-0000-000000000000",
        json={"name": "Ghost Site"}
    )

    assert response.status_code == 404


# ── Delete Tests ───────────────────────────────────────────────────────────────
# Testing DELETE /sites/{site_id}
# We test: successful delete, not found, and confirming it's actually gone after delete

def test_delete_site_success(client):
    # Create a site then delete it, should return 200
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    response = client.delete(f"/sites/{site_id}")

    assert response.status_code == 200


def test_delete_site_confirm_gone(client):
    # After deleting a site, fetching it by ID should return 404
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    client.delete(f"/sites/{site_id}")

    response = client.get(f"/sites/{site_id}")

    assert response.status_code == 404             # confirms the delete actually worked


def test_delete_site_not_found(client):
    # Trying to delete a site that doesnt exist should return 404
    response = client.delete("/sites/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_delete_site_does_not_delete_business(client):
    # Deleting a site should NOT delete the parent business
    business_id = create_business(client).json()["id"]
    site_id = create_site(client, business_id).json()["id"]

    client.delete(f"/sites/{site_id}")

    # The business should still be there
    response = client.get(f"/businesses/{business_id}")

    assert response.status_code == 200             # business is unaffected by site deletion
