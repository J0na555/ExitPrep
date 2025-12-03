import pytest


@pytest.mark.anyio
async def test_chapters_crud(ac):
    # Need a course to attach chapter to
    course_payload = {"title": "Course for Chapters", "description": "course desc"}
    resp = await ac.post("/api/courses/", json=course_payload)
    assert resp.status_code == 201
    course = resp.json()
    course_id = course["id"]

    # Create chapter
    chapter_payload = {
        "course_id": course_id,
        "title": "Chapter 1",
        "description": "ch desc",
        "order_index": 1,
    }
    resp = await ac.post("/api/chapters/", json=chapter_payload)
    assert resp.status_code == 201
    chapter = resp.json()
    chapter_id = chapter["id"]

    # List chapters for course
    resp = await ac.get(f"/api/chapters/course/{course_id}")
    assert resp.status_code == 200
    lst = resp.json()
    assert isinstance(lst, list)

    # Get by id
    resp = await ac.get(f"/api/chapters/{chapter_id}")
    assert resp.status_code == 200

    # Update
    resp = await ac.put(f"/api/chapters/{chapter_id}", json={"title": "Chapter 1 Updated"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated.get("title") == "Chapter 1 Updated"

    # Delete
    resp = await ac.delete(f"/api/chapters/{chapter_id}")
    assert resp.status_code == 204
