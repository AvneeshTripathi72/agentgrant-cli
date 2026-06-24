from agentgrant.utils.parser import parse_llms_text


def test_parse_llms_text_handles_links_and_absolute_urls() -> None:
    pages = parse_llms_text(
        """
        # docs
        - [Scopes](https://grantex.ai/docs/scopes) - scope docs
        [Trust Registry](/docs/trust-registry)
        https://grantex.ai/docs/delegation
        """,
        "https://grantex.ai",
    )

    assert [page.slug for page in pages] == ["scopes", "trust-registry", "delegation"]
    assert pages[0].description == "scope docs"
