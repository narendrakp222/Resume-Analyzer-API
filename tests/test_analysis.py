import pytest


@pytest.mark.asyncio
async def test_analyze_resume_success(authenticated_client, sample_pdf_bytes):
    # Upload resume
    files = {"file": ("software_dev.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = await authenticated_client.post("/upload-resume", files=files)
    resume_id = upload_res.json()["id"]

    # Trigger analysis
    analyze_res = await authenticated_client.post(f"/analyze/{resume_id}")
    assert analyze_res.status_code == 200
    data = analyze_res.json()

    assert data["resume_id"] == resume_id
    assert isinstance(data["ats_score"], int)
    assert "Python" in data["extracted_skills"]
    assert "FastAPI" in data["extracted_skills"]
    assert len(data["suggestions"]) > 0

    # Get score
    score_res = await authenticated_client.get(f"/score/{resume_id}")
    assert score_res.status_code == 200
    score_data = score_res.json()
    assert score_data["ats_score"] == data["ats_score"]
    assert "Python" in score_data["skills_found"]
