import ipaddress
import re
import socket
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 "
    "JobMatchAgent/1.0"
)

REQUEST_TIMEOUT_SECONDS = 20.0
MAX_REDIRECTS = 5
MAX_DOWNLOAD_BYTES = 5 * 1024 * 1024
MIN_EXTRACTED_TEXT_LENGTH = 100

ALLOWED_CONTENT_TYPES = {
    "text/html",
    "application/xhtml+xml",
    "text/plain",
}

BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
}

LOGIN_PAGE_TERMS = {
    "sign in",
    "log in",
    "login",
    "anmelden",
    "einloggen",
    "create account",
    "konto erstellen",
}

JOB_RELATED_TERMS = {
    "job",
    "position",
    "vacancy",
    "career",
    "responsibilities",
    "requirements",
    "qualifications",
    "apply",
    "bewerbung",
    "stellenangebot",
    "stellenbeschreibung",
    "aufgaben",
    "anforderungen",
    "qualifikationen",
    "karriere",
}


class JobURLImportError(Exception):
    """
    Raised when a job webpage cannot be imported safely.
    """


def normalize_url(url: str) -> str:
    """
    Clean and validate the basic URL structure.
    """

    cleaned_url = url.strip()

    if not cleaned_url:
        raise JobURLImportError(
            "Please enter a job-page URL."
        )

    if "://" not in cleaned_url:
        cleaned_url = f"https://{cleaned_url}"

    parsed_url = urlparse(cleaned_url)

    if parsed_url.scheme.lower() not in {
        "http",
        "https",
    }:
        raise JobURLImportError(
            "Only HTTP and HTTPS URLs are supported."
        )

    if not parsed_url.hostname:
        raise JobURLImportError(
            "The URL does not contain a valid hostname."
        )

    if parsed_url.username or parsed_url.password:
        raise JobURLImportError(
            "URLs containing usernames or passwords are not allowed."
        )

    return cleaned_url


def is_blocked_ip_address(
    ip_address: str,
) -> bool:
    """
    Return True when an address belongs to a private,
    local, reserved, multicast or otherwise unsafe range.
    """

    try:
        address = ipaddress.ip_address(
            ip_address
        )

    except ValueError:
        return True

    return any(
        [
            address.is_private,
            address.is_loopback,
            address.is_link_local,
            address.is_multicast,
            address.is_reserved,
            address.is_unspecified,
        ]
    )


def validate_public_hostname(
    hostname: str,
) -> list[str]:
    """
    Resolve a hostname and confirm that all returned
    addresses are public internet addresses.
    """

    normalized_hostname = (
        hostname.rstrip(".").lower()
    )

    if normalized_hostname in BLOCKED_HOSTNAMES:
        raise JobURLImportError(
            "Localhost URLs are not allowed."
        )

    if normalized_hostname.endswith(
        (
            ".local",
            ".internal",
            ".localhost",
        )
    ):
        raise JobURLImportError(
            "Local or internal network addresses are not allowed."
        )

    try:
        direct_ip = ipaddress.ip_address(
            normalized_hostname
        )

        if is_blocked_ip_address(
            str(direct_ip)
        ):
            raise JobURLImportError(
                "Private or local IP addresses are not allowed."
            )

        return [
            str(direct_ip)
        ]

    except ValueError:
        pass

    try:
        address_results = socket.getaddrinfo(
            normalized_hostname,
            None,
            type=socket.SOCK_STREAM,
        )

    except socket.gaierror as error:
        raise JobURLImportError(
            "The website hostname could not be resolved."
        ) from error

    resolved_addresses = sorted(
        {
            result[4][0]
            for result in address_results
        }
    )

    if not resolved_addresses:
        raise JobURLImportError(
            "The website did not resolve to an IP address."
        )

    for resolved_address in resolved_addresses:
        if is_blocked_ip_address(
            resolved_address
        ):
            raise JobURLImportError(
                "The website resolves to a private, local "
                "or reserved network address."
            )

    return resolved_addresses


def validate_public_url(
    url: str,
) -> str:
    """
    Validate that a URL points to a public HTTP(S) host.
    """

    normalized_url = normalize_url(
        url
    )

    parsed_url = urlparse(
        normalized_url
    )

    validate_public_hostname(
        parsed_url.hostname or ""
    )

    return normalized_url


def get_content_type(
    response: httpx.Response,
) -> str:
    """
    Return the response MIME type without parameters.
    """

    raw_content_type = response.headers.get(
        "content-type",
        "",
    )

    return (
        raw_content_type
        .split(";", maxsplit=1)[0]
        .strip()
        .lower()
    )


def download_public_page(
    url: str,
) -> dict[str, Any]:
    """
    Download a public webpage while validating every redirect.
    """

    current_url = validate_public_url(
        url
    )

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": (
            "text/html,"
            "application/xhtml+xml,"
            "text/plain;q=0.9,*/*;q=0.1"
        ),
        "Accept-Language": (
            "en-US,en;q=0.9,de;q=0.8"
        ),
    }

    timeout = httpx.Timeout(
        REQUEST_TIMEOUT_SECONDS,
        connect=10.0,
    )

    with httpx.Client(
        headers=headers,
        timeout=timeout,
        follow_redirects=False,
    ) as client:
        for redirect_number in range(
            MAX_REDIRECTS + 1
        ):
            try:
                with client.stream(
                    "GET",
                    current_url,
                ) as response:
                    if response.status_code in {
                        301,
                        302,
                        303,
                        307,
                        308,
                    }:
                        redirect_location = (
                            response.headers.get(
                                "location",
                                "",
                            )
                        )

                        if not redirect_location:
                            raise JobURLImportError(
                                "The website returned an invalid redirect."
                            )

                        if (
                            redirect_number
                            >= MAX_REDIRECTS
                        ):
                            raise JobURLImportError(
                                "The webpage redirected too many times."
                            )

                        redirected_url = urljoin(
                            current_url,
                            redirect_location,
                        )

                        current_url = (
                            validate_public_url(
                                redirected_url
                            )
                        )

                        continue

                    if response.status_code == 401:
                        raise JobURLImportError(
                            "This job page requires authentication."
                        )

                    if response.status_code == 403:
                        raise JobURLImportError(
                            "The website blocked access to this job page."
                        )

                    if response.status_code == 404:
                        raise JobURLImportError(
                            "The job page could not be found."
                        )

                    if response.status_code == 429:
                        raise JobURLImportError(
                            "The website is temporarily rate-limiting access."
                        )

                    if response.status_code >= 400:
                        raise JobURLImportError(
                            "The website returned HTTP status "
                            f"{response.status_code}."
                        )

                    content_type = get_content_type(
                        response
                    )

                    if (
                        content_type
                        and content_type
                        not in ALLOWED_CONTENT_TYPES
                    ):
                        raise JobURLImportError(
                            "The URL does not point to a supported "
                            f"webpage. Content type: {content_type}"
                        )

                    declared_length = (
                        response.headers.get(
                            "content-length"
                        )
                    )

                    if declared_length:
                        try:
                            declared_bytes = int(
                                declared_length
                            )

                        except ValueError:
                            declared_bytes = 0

                        if (
                            declared_bytes
                            > MAX_DOWNLOAD_BYTES
                        ):
                            raise JobURLImportError(
                                "The webpage is too large to import."
                            )

                    downloaded_content = bytearray()

                    for chunk in response.iter_bytes():
                        downloaded_content.extend(
                            chunk
                        )

                        if (
                            len(downloaded_content)
                            > MAX_DOWNLOAD_BYTES
                        ):
                            raise JobURLImportError(
                                "The webpage exceeded the "
                                "maximum permitted download size."
                            )

                    encoding = (
                        response.encoding
                        or "utf-8"
                    )

                    try:
                        html_text = bytes(
                            downloaded_content
                        ).decode(
                            encoding,
                            errors="replace",
                        )

                    except LookupError:
                        html_text = bytes(
                            downloaded_content
                        ).decode(
                            "utf-8",
                            errors="replace",
                        )

                    return {
                        "requested_url": url,
                        "final_url": current_url,
                        "status_code": (
                            response.status_code
                        ),
                        "content_type": content_type,
                        "html": html_text,
                        "download_size": len(
                            downloaded_content
                        ),
                    }

            except httpx.TimeoutException as error:
                raise JobURLImportError(
                    "The website took too long to respond."
                ) from error

            except httpx.ConnectError as error:
                raise JobURLImportError(
                    "A connection to the website could not be established."
                ) from error

            except httpx.HTTPError as error:
                raise JobURLImportError(
                    f"Website request failed: {error}"
                ) from error

    raise JobURLImportError(
        "The webpage could not be downloaded."
    )


def clean_extracted_text(
    text: str,
) -> str:
    """
    Normalize whitespace while preserving paragraphs.
    """

    cleaned_text = text.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    cleaned_lines = []

    for line in cleaned_text.splitlines():
        cleaned_line = re.sub(
            r"[ \t]+",
            " ",
            line,
        ).strip()

        if cleaned_line:
            cleaned_lines.append(
                cleaned_line
            )

    return "\n".join(
        cleaned_lines
    ).strip()


def extract_page_title(
    html_text: str,
) -> str:
    """
    Extract the best available page title.
    """

    soup = BeautifulSoup(
        html_text,
        "html.parser",
    )

    for attribute_name, attribute_value in [
        (
            "property",
            "og:title",
        ),
        (
            "name",
            "twitter:title",
        ),
    ]:
        metadata_tag = soup.find(
            "meta",
            attrs={
                attribute_name: (
                    attribute_value
                )
            },
        )

        if metadata_tag:
            content = metadata_tag.get(
                "content",
                "",
            ).strip()

            if content:
                return content

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    heading = soup.find("h1")

    if heading:
        return heading.get_text(
            " ",
            strip=True,
        )

    return ""


def extract_with_trafilatura(
    html_text: str,
    source_url: str,
) -> str:
    """
    Extract the principal readable content with Trafilatura.
    """

    extracted_text = trafilatura.extract(
        html_text,
        url=source_url,
        include_comments=False,
        include_tables=True,
        include_links=False,
        favor_precision=True,
        output_format="txt",
    )

    return clean_extracted_text(
        extracted_text or ""
    )


def extract_with_beautifulsoup(
    html_text: str,
) -> str:
    """
    Fallback extraction using visible HTML text.
    """

    soup = BeautifulSoup(
        html_text,
        "html.parser",
    )

    for unwanted_element in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "nav",
            "footer",
            "form",
        ]
    ):
        unwanted_element.decompose()

    preferred_containers = []

    for selector in [
        "main",
        "article",
        "[role='main']",
        ".job-description",
        ".jobDescription",
        "#job-description",
        "#jobDescription",
        ".description",
        ".posting",
    ]:
        preferred_containers.extend(
            soup.select(selector)
        )

    if preferred_containers:
        extracted_parts = [
            container.get_text(
                "\n",
                strip=True,
            )
            for container in preferred_containers
        ]

        extracted_text = "\n".join(
            extracted_parts
        )

    else:
        extracted_text = soup.get_text(
            "\n",
            strip=True,
        )

    return clean_extracted_text(
        extracted_text
    )


def page_appears_to_be_login_only(
    title: str,
    extracted_text: str,
) -> bool:
    """
    Detect likely login-only pages with little job content.
    """

    combined_text = (
        f"{title}\n{extracted_text}"
        .lower()
    )

    login_term_count = sum(
        term in combined_text
        for term in LOGIN_PAGE_TERMS
    )

    job_term_count = sum(
        term in combined_text
        for term in JOB_RELATED_TERMS
    )

    return (
        login_term_count >= 2
        and job_term_count == 0
    )


def calculate_job_page_confidence(
    title: str,
    extracted_text: str,
) -> str:
    """
    Return a simple confidence label indicating whether
    the page resembles a job advertisement.
    """

    combined_text = (
        f"{title}\n{extracted_text}"
        .lower()
    )

    matching_terms = sum(
        term in combined_text
        for term in JOB_RELATED_TERMS
    )

    if matching_terms >= 5:
        return "high"

    if matching_terms >= 2:
        return "medium"

    return "low"


def import_job_from_url(
    url: str,
) -> dict[str, Any]:
    """
    Download and extract a public job webpage.

    Returns text for user verification. It does not save
    or analyse the application automatically.
    """

    page_data = download_public_page(
        url
    )

    html_text = page_data["html"]
    final_url = page_data["final_url"]

    title = extract_page_title(
        html_text
    )

    extracted_text = extract_with_trafilatura(
        html_text=html_text,
        source_url=final_url,
    )

    extraction_method = "trafilatura"

    if (
        len(extracted_text)
        < MIN_EXTRACTED_TEXT_LENGTH
    ):
        extracted_text = (
            extract_with_beautifulsoup(
                html_text
            )
        )

        extraction_method = "beautifulsoup"

    if (
        len(extracted_text)
        < MIN_EXTRACTED_TEXT_LENGTH
    ):
        raise JobURLImportError(
            "Very little readable text could be extracted. "
            "The page may require JavaScript, login access, "
            "or may block automated reading."
        )

    if page_appears_to_be_login_only(
        title=title,
        extracted_text=extracted_text,
    ):
        raise JobURLImportError(
            "The URL appears to lead to a login page "
            "instead of a public job description."
        )

    confidence = calculate_job_page_confidence(
        title=title,
        extracted_text=extracted_text,
    )

    warnings = []

    if confidence == "low":
        warnings.append(
            "The extracted page does not strongly resemble "
            "a job advertisement. Review the text carefully."
        )

    if extraction_method == "beautifulsoup":
        warnings.append(
            "The fallback HTML extractor was used. "
            "Navigation or unrelated text may be included."
        )

    return {
        "title": title,
        "requested_url": page_data[
            "requested_url"
        ],
        "final_url": final_url,
        "text": extracted_text,
        "text_length": len(
            extracted_text
        ),
        "download_size": page_data[
            "download_size"
        ],
        "content_type": page_data[
            "content_type"
        ],
        "extraction_method": (
            extraction_method
        ),
        "job_page_confidence": confidence,
        "warnings": warnings,
    }