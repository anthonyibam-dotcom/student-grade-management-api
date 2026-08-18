def student_payload():
    return {
        "first_name": "Grace",
        "last_name": "Hopper",
        "email": "grace@example.com",
        "enrollment_date": "2026-09-01",
    }


def course_payload(code="CS101"):
    return {
        "code": code,
        "title": "Computer Science",
        "credits": 4,
        "description": "Foundations of computing",
    }


def create_student_and_course(client):
    student = client.post("/api/v1/students/", json=student_payload()).json()
    course = client.post("/api/v1/courses/", json=course_payload()).json()
    return student["id"], course["id"]


def test_course_crud(client):
    created = client.post("/api/v1/courses/", json=course_payload()).json()
    course_id = created["id"]
    assert created["code"] == "CS101"
    assert client.get(f"/api/v1/courses/{course_id}").status_code == 200
    updated = client.put(f"/api/v1/courses/{course_id}", json={"credits": 5}).json()
    assert updated["credits"] == 5
    assert client.delete(f"/api/v1/courses/{course_id}").status_code == 204


def test_grade_create_update_filter_and_delete(client):
    student_id, course_id = create_student_and_course(client)
    payload = {
        "student_id": student_id,
        "course_id": course_id,
        "score": 89.5,
        "semester": "Fall 2026",
    }
    response = client.post("/api/v1/grades/", json=payload)
    assert response.status_code == 201
    grade = response.json()
    assert grade["letter_grade"] == "B"

    filtered = client.get("/api/v1/grades/", params={"student_id": student_id})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    updated = client.put(f"/api/v1/grades/{grade['id']}", json={"score": 95}).json()
    assert updated["letter_grade"] == "A"
    assert client.delete(f"/api/v1/grades/{grade['id']}").status_code == 204


def test_grade_score_boundaries_and_duplicate_conflict(client):
    student_id, course_id = create_student_and_course(client)
    base = {"student_id": student_id, "course_id": course_id, "semester": "Fall 2026"}
    for score in (-5, 105):
        response = client.post("/api/v1/grades/", json={**base, "score": score})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    assert client.post("/api/v1/grades/", json={**base, "score": 60}).status_code == 201
    duplicate = client.post("/api/v1/grades/", json={**base, "score": 70})
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "GRADE_EXISTS"


def test_deleting_student_cascades_grades(client):
    student_id, course_id = create_student_and_course(client)
    grade = client.post(
        "/api/v1/grades/",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "score": 75,
            "semester": "Spring 2027",
        },
    )
    assert grade.status_code == 201
    assert client.delete(f"/api/v1/students/{student_id}").status_code == 204
    assert client.get("/api/v1/grades/").json()["total"] == 0
