def create_student(client):
    response = client.post(
        "/api/v1/students/",
        json={
            "first_name": "Katherine",
            "last_name": "Johnson",
            "email": "katherine@example.com",
            "enrollment_date": "2026-09-01",
        },
    )
    return response.json()["id"]


def create_course(client, code, credits):
    response = client.post(
        "/api/v1/courses/",
        json={"code": code, "title": code, "credits": credits},
    )
    return response.json()["id"]


def add_grade(client, student_id, course_id, score, semester):
    return client.post(
        "/api/v1/grades/",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "score": score,
            "semester": semester,
        },
    )


def test_gpa_and_weighted_average_are_credit_weighted(client):
    student_id = create_student(client)
    course_a = create_course(client, "MATH101", 4)
    course_b = create_course(client, "ART101", 2)
    assert add_grade(client, student_id, course_a, 95, "Fall 2026").status_code == 201
    assert add_grade(client, student_id, course_b, 75, "Fall 2026").status_code == 201

    response = client.get(f"/api/v1/analytics/students/{student_id}/gpa")
    assert response.status_code == 200
    data = response.json()
    assert data["gpa"] == 3.33
    assert data["weighted_average"] == 88.33
    assert data["grade_count"] == 2

    detail = client.get(f"/api/v1/students/{student_id}").json()
    assert len(detail["courses"]) == 2
    assert detail["gpa"] == 3.33


def test_course_statistics(client):
    student_a = create_student(client)
    student_b = client.post(
        "/api/v1/students/",
        json={
            "first_name": "Dorothy",
            "last_name": "Vaughan",
            "email": "dorothy@example.com",
            "enrollment_date": "2026-09-01",
        },
    ).json()["id"]
    course_id = create_course(client, "STAT101", 3)
    assert add_grade(client, student_a, course_id, 90, "Fall 2026").status_code == 201
    assert add_grade(client, student_b, course_id, 50, "Fall 2026").status_code == 201

    response = client.get(f"/api/v1/analytics/courses/{course_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "course_id": course_id,
        "grade_count": 2,
        "mean_score": 70.0,
        "max_score": 90.0,
        "min_score": 50.0,
        "passing_rate": 50.0,
    }


def test_missing_analytics_resource_is_uniform_error(client):
    response = client.get("/api/v1/analytics/students/999/gpa")
    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {"code": "STUDENT_NOT_FOUND", "message": "Student 999 was not found"},
    }
