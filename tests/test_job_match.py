import pytest


@pytest.mark.asyncio
async def test_job_match_success(authenticated_client, sample_pdf_bytes):
    # Upload resume
    files = {"file": ("resume_job_match.pdf", sample_pdf_bytes, "application/pdf")}
    await authenticated_client.post("/upload-resume", files=files)

    job_description = (
        "Looking for a Backend Engineering Intern with strong Python, FastAPI, PostgreSQL, "
        "and Docker skills. Experience with AWS cloud deployments and REST APIs is highly preferred."
    )

    response = await authenticated_client.post(
        "/job-match",
        json={"job_description": job_description}
    )
    assert response.status_code == 200
    data = response.json()
    assert "match_percentage" in data
    assert isinstance(data["match_percentage"], float)
    assert "Python" in data["matching_skills"]
    assert len(data["suggested_improvements"]) > 0
