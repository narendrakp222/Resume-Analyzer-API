import pytest


@pytest.mark.asyncio
async def test_upload_resume_pdf_success(authenticated_client, sample_pdf_bytes):
    files = {"file": ("test_resume.pdf", sample_pdf_bytes, "application/pdf")}
    response = await authenticated_client.post("/upload-resume", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_resume.pdf"
    assert "id" in data


@pytest.mark.asyncio
async def test_upload_resume_invalid_file_type(authenticated_client):
    files = {"file": ("test_resume.txt", b"Plain text content", "text/plain")}
    response = await authenticated_client.post("/upload-resume", files=files)
    assert response.status_code == 400
    assert "Only PDF files" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_my_resumes(authenticated_client, sample_pdf_bytes):
    # Upload a resume first
    files = {"file": ("my_cv.pdf", sample_pdf_bytes, "application/pdf")}
    await authenticated_client.post("/upload-resume", files=files)

    response = await authenticated_client.get("/my-resumes")
    assert response.status_code == 200
    resumes = response.json()
    assert len(resumes) >= 1
    assert resumes[0]["filename"] == "my_cv.pdf"
