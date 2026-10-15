import sqlite3

import app as tiger


def _test_client(tmp_path, monkeypatch):
    db_path = tmp_path / "tiger_test.db"
    monkeypatch.setattr(tiger, "DB", str(db_path))
    tiger.init_db()
    tiger.app.config.update(TESTING=True)
    return tiger.app.test_client(), db_path


def test_student_setup_displays_profile(tmp_path, monkeypatch):
    client, _ = _test_client(tmp_path, monkeypatch)
    response = client.get("/student")
    assert response.status_code == 200
    assert b"Student Setup" in response.data
    assert b"Sample Student" in response.data


def test_student_profile_post_persists_and_reads_back(tmp_path, monkeypatch):
    client, db_path = _test_client(tmp_path, monkeypatch)
    response = client.post(
        "/student",
        data={
            "student_id": "TEST1001",
            "name": "Jordan Test",
            "email": "jordan.test@example.com",
            "major": "Computer Engineering",
            "concentration": "Embedded Systems",
            "catalog_year": "2026-2027",
            "standing": "Senior",
            "gpa": "3.50",
            "credits_completed": "90",
            "total_credits": "128",
            "target_graduation": "Spring 2027",
            "pace": "15",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Student profile saved." in response.data
    assert b"Jordan Test" in response.data

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT student_id, name, major, catalog_year FROM student WHERE id=1"
        ).fetchone()
    assert row == ("TEST1001", "Jordan Test", "Computer Engineering", "2026-2027")


def test_core_pages_load(tmp_path, monkeypatch):
    client, _ = _test_client(tmp_path, monkeypatch)
    for path in ("/", "/catalog", "/requirements", "/transcript", "/prerequisites", "/audit", "/priority", "/what-if", "/planner", "/risks", "/data-center"):
        response = client.get(path)
        assert response.status_code == 200, f"{path} returned {response.status_code}"


def test_course_catalog_export_is_csv(tmp_path, monkeypatch):
    client, _ = _test_client(tmp_path, monkeypatch)
    response = client.get("/export/courses")
    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert b"code" in response.data
