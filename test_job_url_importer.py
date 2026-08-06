import sys

from services.job_url_importer import (
    JobURLImportError,
    import_job_from_url,
)


def main() -> None:
    """
    Test importing a public job-description webpage.
    """

    if len(sys.argv) < 2:
        print(
            "Usage:"
        )

        print(
            'python test_job_url_importer.py '
            '"https://example.com/public-job-page"'
        )

        sys.exit(1)

    job_url = sys.argv[1]

    try:
        result = import_job_from_url(
            job_url
        )

        print(
            "Job URL import successful."
        )

        print(
            f"Title: {result['title']}"
        )

        print(
            f"Final URL: {result['final_url']}"
        )

        print(
            "Extraction method: "
            f"{result['extraction_method']}"
        )

        print(
            "Job-page confidence: "
            f"{result['job_page_confidence']}"
        )

        print(
            f"Text length: {result['text_length']}"
        )

        if result["warnings"]:
            print("\nWarnings:")

            for warning in result["warnings"]:
                print(
                    f"- {warning}"
                )

        print(
            "\nExtracted text preview:\n"
        )

        print(
            result["text"][:2000]
        )

    except JobURLImportError as error:
        print(
            "Job URL import failed."
        )

        print(
            f"Reason: {error}"
        )

        sys.exit(1)

    except Exception as error:
        print(
            "Unexpected error."
        )

        print(
            f"Error type: "
            f"{type(error).__name__}"
        )

        print(
            f"Details: {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()