import pytest


@pytest.mark.anyio
async def test_courses_crud(ac):
    # Create
    payload = {"title": "Test Course", "description": "A test course"}
    resp = await ac.post("/api/courses/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    course_id = data["id"]

    # List
    resp = await ac.get("/api/courses/")
    assert resp.status_code == 200
    lst = resp.json()
    assert isinstance(lst, list)

    # Get by id
    resp = await ac.get(f"/api/courses/{course_id}")
    assert resp.status_code == 200
    fetched = resp.json()
    assert fetched.get("id") == course_id

    # Update
    resp = await ac.put(f"/api/courses/{course_id}", json={"title": "Updated"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated.get("title") == "Updated"

    # Delete
    resp = await ac.delete(f"/api/courses/{course_id}")
    assert resp.status_code == 204
