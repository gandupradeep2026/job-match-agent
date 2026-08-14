import logging
from pathlib import Path

from market_intelligence.refresh_runner import (
    MarketRefreshRunner,
)


LOG_PATH = Path(
    "logs/market_refresh.log"
)


def configure_logging():

    LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                LOG_PATH,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )


def main():

    configure_logging()

    logger = logging.getLogger(
        "market_refresh"
    )

    logger.info(
        "=" * 70
    )

    logger.info(
        "Starting scheduled "
        "market refresh."
    )

    try:

        runner = (
            MarketRefreshRunner()
        )

        execution = runner.run()

        result = (
            execution.refresh_result
        )

        logger.info(
            "Market refresh completed."
        )

        logger.info(
            "Snapshot ID: %s",
            execution.snapshot_id,
        )

        logger.info(
            "Sources checked: %s",
            result.sources_attempted,
        )

        logger.info(
            "Fetched: %s",
            result.fetched,
        )

        logger.info(
            "New jobs: %s",
            result.inserted,
        )

        logger.info(
            "Duplicates: %s",
            result.duplicates,
        )

        logger.info(
            "Filtered out: %s",
            result.filtered_out,
        )

        logger.info(
            "Failed jobs: %s",
            result.failed_jobs,
        )

        logger.info(
            "Source errors: %s",
            result.source_errors,
        )

        logger.info(
            "Jobs before: %s",
            result.jobs_before,
        )

        logger.info(
            "Jobs after: %s",
            result.jobs_after,
        )

        if result.source_errors:

            logger.warning(
                "%s source(s) failed.",
                result.source_errors,
            )

        for source in (
            result.source_results
        ):

            if source.source_error:

                logger.error(
                    "%s (%s): %s",
                    source.company,
                    source.provider,
                    source.source_error,
                )

            elif source.failed:

                logger.warning(
                    "%s (%s): "
                    "%s individual job(s) failed.",
                    source.company,
                    source.provider,
                    source.failed,
                )

        logger.info(
            "Scheduled market refresh "
            "finished successfully."
        )

    except Exception:

        logger.exception(
            "Scheduled market refresh failed."
        )

        raise


if __name__ == "__main__":
    main()
