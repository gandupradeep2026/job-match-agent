from unittest.mock import MagicMock

import httpx
import pytest

import services.job_url_importer as importer


PUBLIC_TEST_IP = "93.184.216.34"


@pytest.fixture()
def public_dns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Make every test hostname resolve to a public IP.
    """

    monkeypatch.setattr(
        importer.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (
                importer.socket.AF_INET,
                importer.socket.SOCK_STREAM,
                6,
                "",
                (
                    PUBLIC_TEST_IP,
                    0,
                ),
            )
        ],
    )


def build_mock_response(
    html: str,
    status_code: int = 200,
    headers: dict | None = None,
) -> MagicMock:
    """
    Build a mocked streaming HTTP response.
    """

    response = MagicMock()

    response.status_code = status_code

    response.headers = headers or {
        "content-type": (
            "text/html; charset=utf-8"
        ),
    }

    response.encoding = "utf-8"

    response.iter_bytes.return_value = [
        html.encode("utf-8"),
    ]

    response.__enter__.return_value = (
        response
    )

    response.__exit__.return_value = (
        False
    )

    return response


def build_mock_client(
    response: MagicMock,
) -> MagicMock:
    """
    Build a mocked httpx.Client context manager.
    """

    client = MagicMock()

    client.stream.return_value = (
        response
    )

    client.__enter__.return_value = (
        client
    )

    client.__exit__.return_value = (
        False
    )

    return client


def test_normalize_url_adds_https() -> None:
    result = importer.normalize_url(
        "example.com/jobs/123"
    )

    assert result == (
        "https://example.com/jobs/123"
    )


def test_normalize_url_rejects_unsupported_scheme() -> None:
    with pytest.raises(
        importer.JobURLImportError
    ):
        importer.normalize_url(
            "ftp://example.com/job"
        )


def test_normalize_url_rejects_credentials() -> None:
    with pytest.raises(
        importer.JobURLImportError
    ):
        importer.normalize_url(
            "https://user:password@example.com/job"
        )


def test_private_ip_is_blocked() -> None:
    assert (
        importer.is_blocked_ip_address(
            "127.0.0.1"
        )
        is True
    )

    assert (
        importer.is_blocked_ip_address(
            "192.168.1.10"
        )
        is True
    )

    assert (
        importer.is_blocked_ip_address(
            "10.0.0.10"
        )
        is True
    )


def test_public_ip_is_allowed() -> None:
    assert (
        importer.is_blocked_ip_address(
            PUBLIC_TEST_IP
        )
        is False
    )


def test_localhost_is_rejected() -> None:
    with pytest.raises(
        importer.JobURLImportError
    ):
        importer.validate_public_url(
            "http://localhost/job"
        )


def test_private_hostname_resolution_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        importer.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (
                importer.socket.AF_INET,
                importer.socket.SOCK_STREAM,
                6,
                "",
                (
                    "192.168.1.5",
                    0,
                ),
            )
        ],
    )

    with pytest.raises(
        importer.JobURLImportError
    ):
        importer.validate_public_url(
            "https://example.com/job"
        )


def test_extract_page_title_from_og_metadata() -> None:
    html = """
    <html>
        <head>
            <meta
                property="og:title"
                content="IT Support Specialist"
            >
            <title>Fallback Title</title>
        </head>
        <body></body>
    </html>
    """

    result = importer.extract_page_title(
        html
    )

    assert result == (
        "IT Support Specialist"
    )


def test_extract_page_title_from_title_tag() -> None:
    html = """
    <html>
        <head>
            <title>
                System Administrator Job
            </title>
        </head>
        <body></body>
    </html>
    """

    result = importer.extract_page_title(
        html
    )

    assert result == (
        "System Administrator Job"
    )


def test_extract_with_beautifulsoup_removes_navigation() -> None:
    html = """
    <html>
        <body>
            <nav>
                Home Careers Contact
            </nav>

            <main>
                <h1>IT Support Specialist</h1>

                <p>
                    Responsibilities include user support,
                    Active Directory and Microsoft 365.
                </p>
            </main>

            <footer>
                Privacy Terms
            </footer>
        </body>
    </html>
    """

    result = (
        importer.extract_with_beautifulsoup(
            html
        )
    )

    assert "IT Support Specialist" in result
    assert "Active Directory" in result
    assert "Home Careers Contact" not in result
    assert "Privacy Terms" not in result


def test_job_page_confidence_high() -> None:
    result = (
        importer.calculate_job_page_confidence(
            title="System Administrator Job",
            extracted_text=(
                "Responsibilities requirements "
                "qualifications apply career position"
            ),
        )
    )

    assert result == "high"


def test_job_page_confidence_low() -> None:
    result = (
        importer.calculate_job_page_confidence(
            title="Company Home Page",
            extracted_text=(
                "Welcome to our corporate website."
            ),
        )
    )

    assert result == "low"


def test_login_only_page_is_detected() -> None:
    result = (
        importer.page_appears_to_be_login_only(
            title="Sign in",
            extracted_text=(
                "Log in to continue. "
                "Create account."
            ),
        )
    )

    assert result is True


def test_download_public_page_success(
    monkeypatch: pytest.MonkeyPatch,
    public_dns: None,
) -> None:
    html = """
    <html>
        <body>
            <h1>IT Support Specialist</h1>
            <p>Job responsibilities and requirements.</p>
        </body>
    </html>
    """

    response = build_mock_response(
        html
    )

    client = build_mock_client(
        response
    )

    monkeypatch.setattr(
        importer.httpx,
        "Client",
        lambda *args, **kwargs: client,
    )

    result = importer.download_public_page(
        "https://example.com/jobs/123"
    )

    assert result["status_code"] == 200
    assert result["content_type"] == (
        "text/html"
    )
    assert "IT Support Specialist" in (
        result["html"]
    )
    assert result["final_url"] == (
        "https://example.com/jobs/123"
    )


def test_download_public_page_rejects_403(
    monkeypatch: pytest.MonkeyPatch,
    public_dns: None,
) -> None:
    response = build_mock_response(
        "",
        status_code=403,
    )

    client = build_mock_client(
        response
    )

    monkeypatch.setattr(
        importer.httpx,
        "Client",
        lambda *args, **kwargs: client,
    )

    with pytest.raises(
        importer.JobURLImportError,
        match="blocked access",
    ):
        importer.download_public_page(
            "https://example.com/jobs/123"
        )


def test_download_public_page_rejects_login_required(
    monkeypatch: pytest.MonkeyPatch,
    public_dns: None,
) -> None:
    response = build_mock_response(
        "",
        status_code=401,
    )

    client = build_mock_client(
        response
    )

    monkeypatch.setattr(
        importer.httpx,
        "Client",
        lambda *args, **kwargs: client,
    )

    with pytest.raises(
        importer.JobURLImportError,
        match="requires authentication",
    ):
        importer.download_public_page(
            "https://example.com/jobs/123"
        )


def test_download_public_page_rejects_large_response(
    monkeypatch: pytest.MonkeyPatch,
    public_dns: None,
) -> None:
    response = build_mock_response(
        "",
        headers={
            "content-type": "text/html",
            "content-length": str(
                importer.MAX_DOWNLOAD_BYTES
                + 1
            ),
        },
    )

    client = build_mock_client(
        response
    )

    monkeypatch.setattr(
        importer.httpx,
        "Client",
        lambda *args, **kwargs: client,
    )

    with pytest.raises(
        importer.JobURLImportError,
        match="too large",
    ):
        importer.download_public_page(
            "https://example.com/jobs/123"
        )


def test_import_job_from_url_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    html = """
    <html>
        <head>
            <title>
                Fachinformatiker Systemintegration
            </title>
        </head>

        <body>
            <main>
                <h1>
                    Fachinformatiker für
                    Systemintegration
                </h1>

                <h2>Aufgaben</h2>

                <p>
                    Support users, configure networks,
                    manage Active Directory and maintain
                    Microsoft 365 systems.
                </p>

                <h2>Anforderungen</h2>

                <p>
                    German B2, English B1, Linux,
                    Windows Server and PowerShell.
                </p>

                <p>
                    Apply now for this position.
                </p>
            </main>
        </body>
    </html>
    """

    monkeypatch.setattr(
        importer,
        "download_public_page",
        lambda url: {
            "requested_url": url,
            "final_url": (
                "https://example.com/jobs/123"
            ),
            "status_code": 200,
            "content_type": "text/html",
            "html": html,
            "download_size": len(
                html.encode("utf-8")
            ),
        },
    )

    monkeypatch.setattr(
        importer,
        "extract_with_trafilatura",
        lambda html_text, source_url: (
            importer.extract_with_beautifulsoup(
                html_text
            )
        ),
    )

    result = importer.import_job_from_url(
        "https://example.com/jobs/123"
    )

    assert result["title"] == (
        "Fachinformatiker Systemintegration"
    )

    assert "Active Directory" in (
        result["text"]
    )

    assert result["job_page_confidence"] in {
        "medium",
        "high",
    }

    assert result["final_url"] == (
        "https://example.com/jobs/123"
    )


def test_import_job_from_url_rejects_short_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        importer,
        "download_public_page",
        lambda url: {
            "requested_url": url,
            "final_url": url,
            "status_code": 200,
            "content_type": "text/html",
            "html": "<html><body>Short</body></html>",
            "download_size": 31,
        },
    )

    monkeypatch.setattr(
        importer,
        "extract_with_trafilatura",
        lambda html_text, source_url: (
            "Short"
        ),
    )

    monkeypatch.setattr(
        importer,
        "extract_with_beautifulsoup",
        lambda html_text: "Short",
    )

    with pytest.raises(
        importer.JobURLImportError,
        match="Very little readable text",
    ):
        importer.import_job_from_url(
            "https://example.com/job"
        )