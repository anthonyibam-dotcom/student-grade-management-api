from datetime import date


def student_payload(email="ada@example.com"):
    return {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": email,
        "enrollment_date": "2026-09-01",
    }


def test_student_crud_and_search(client):
    response = client.post("/api/v1/students/", json=student_payload())
    assert response.status_code == 201
    student = response.json()
    assert student["email"] == "ada@example.com"
    student_id = student["id"]

    response = client.get("/api/v1/students/", params={"search": "Lovelace"})
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["gpa"] == 0.0

    response = client.put(f"/api/v1/students/{student_id}", json={"last_name": "Byron"})
    assert response.status_code == 200
    assert response.json()["last_name"] == "Byron"

    response = client.delete(f"/api/v1/students/{student_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/students/{student_id}").status_code == 404


def test_student_email_conflict_and_invalid_email(client):
    assert client.post("/api/v1/students/", json=student_payload()).status_code == 201
    conflict = client.post("/api/v1/students/", json=student_payload())
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "STUDENT_EMAIL_EXISTS"

    invalid = client.post("/api/v1/students/", json=student_payload("not-an-email"))
    assert invalid.status_code == 422
    assert invalid.json()["success"] is False


def test_student_pagination(client):
    for index in range(3):
        assert client.post(
            "/api/v1/students/", json=student_payload(f"student{index}@example.com")
        ).status_code == 201
    response = client.get("/api/v1/students/", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 2
