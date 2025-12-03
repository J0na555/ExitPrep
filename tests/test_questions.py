import pytest


@pytest.mark.anyio
async def test_questions_crud(ac):
    # Need a course and chapter to attach question to
    course_payload = {"title": "Course for Questions", "description": "course desc"}
    resp = await ac.post("/api/courses/", json=course_payload)
    assert resp.status_code == 201
    course = resp.json()
    course_id = course["id"]

    chapter_payload = {
        "course_id": course_id,
        "title": "Chapter for Questions",
        "description": "ch desc",
        "order_index": 1,
    }
    resp = await ac.post("/api/chapters/", json=chapter_payload)
    assert resp.status_code == 201
    chapter = resp.json()
    chapter_id = chapter["id"]

    # Create question
    question_payload = {
        "chapter_id": chapter_id,
        "question_text": "What is 2+2?",
        "options": {"A": "3", "B": "4", "C": "5"},
        "correct_answer": "B",
        "difficulty": "easy",
        "explanation": "Basic math",
    }
    resp = await ac.post("/api/questions/", json=question_payload)
    assert resp.status_code == 201
    question = resp.json()
    question_id = question["id"]

    # List questions for chapter
    resp = await ac.get(f"/api/questions/chapter/{chapter_id}")
    assert resp.status_code == 200
    lst = resp.json()
    assert isinstance(lst, list)

    # Get by id
    resp = await ac.get(f"/api/questions/{question_id}")
    assert resp.status_code == 200

    # Update
    resp = await ac.put(f"/api/questions/{question_id}", json={"question_text": "What is 3+3?"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated.get("question_text") == "What is 3+3?"

    # Delete
    resp = await ac.delete(f"/api/questions/{question_id}")
    assert resp.status_code == 204
