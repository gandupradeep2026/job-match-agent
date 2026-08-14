import json

from market_intelligence.providers.greenhouse import (
    GreenhouseProvider,
)
from market_intelligence.providers.lever import (
    LeverProvider,
)
from market_intelligence.source_registry import (
    JobSourceRegistry,
)


def write_config(
    tmp_path,
    data,
):

    path = (
        tmp_path
        / "job_sources.json"
    )

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    return path


def test_registry_loads_sources(
    tmp_path,
):

    path = write_config(
        tmp_path,
        {
            "sources": [
                {
                    "provider": (
                        "greenhouse"
                    ),
                    "board": (
                        "companyone"
                    ),
                    "company": (
                        "Company One"
                    ),
                    "enabled": True,
                },
                {
                    "provider": (
                        "lever"
                    ),
                    "site": (
                        "companytwo"
                    ),
                    "company": (
                        "Company Two"
                    ),
                    "enabled": True,
                },
            ]
        },
    )

    registry = (
        JobSourceRegistry(
            path
        )
    )

    sources = (
        registry.load_sources()
    )

    assert len(sources) == 2

    assert (
        sources[0].provider
        == "greenhouse"
    )

    assert (
        sources[1].provider
        == "lever"
    )


def test_disabled_sources_are_removed(
    tmp_path,
):

    path = write_config(
        tmp_path,
        {
            "sources": [
                {
                    "provider": (
                        "greenhouse"
                    ),
                    "board": (
                        "enabledcompany"
                    ),
                    "enabled": True,
                },
                {
                    "provider": (
                        "lever"
                    ),
                    "site": (
                        "disabledcompany"
                    ),
                    "enabled": False,
                },
            ]
        },
    )

    registry = (
        JobSourceRegistry(
            path
        )
    )

    enabled = (
        registry.enabled_sources()
    )

    assert len(enabled) == 1

    assert (
        enabled[0].provider
        == "greenhouse"
    )


def test_greenhouse_provider_is_built(
    tmp_path,
):

    path = write_config(
        tmp_path,
        {
            "sources": [
                {
                    "provider": (
                        "greenhouse"
                    ),
                    "board": "company",
                }
            ]
        },
    )

    registry = (
        JobSourceRegistry(
            path
        )
    )

    source = (
        registry.load_sources()[0]
    )

    provider = (
        registry.build_provider(
            source
        )
    )

    assert isinstance(
        provider,
        GreenhouseProvider,
    )


def test_lever_provider_is_built(
    tmp_path,
):

    path = write_config(
        tmp_path,
        {
            "sources": [
                {
                    "provider": "lever",
                    "site": "company",
                    "instance": "eu",
                }
            ]
        },
    )

    registry = (
        JobSourceRegistry(
            path
        )
    )

    source = (
        registry.load_sources()[0]
    )

    provider = (
        registry.build_provider(
            source
        )
    )

    assert isinstance(
        provider,
        LeverProvider,
    )

    assert (
        provider.instance
        == "eu"
    )


def test_greenhouse_requires_board(
    tmp_path,
):

    path = write_config(
        tmp_path,
        {
            "sources": [
                {
                    "provider": (
                        "greenhouse"
                    )
                }
            ]
        },
    )

    registry = (
        JobSourceRegistry(
            path
        )
    )

    try:
        registry.load_sources()

        assert False

    except ValueError as error:

        assert (
            "requires 'board'"
            in str(error)
        )


def test_unknown_provider_is_rejected(
    tmp_path,
):

    path = write_config(
        tmp_path,
        {
            "sources": [
                {
                    "provider": (
                        "unknown"
                    )
                }
            ]
        },
    )

    registry = (
        JobSourceRegistry(
            path
        )
    )

    try:
        registry.load_sources()

        assert False

    except ValueError as error:

        assert (
            "Unsupported provider"
            in str(error)
        )
