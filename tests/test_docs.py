from agentgrant.commands.docs import parse_llms_text


def test_parse_llms_text_supports_markdown_links_and_urls() -> None:
    llms_text = """
# Docs
- [Scopes](https://grantex.ai/docs/scopes) - Scope documentation
[Trust Registry](/docs/trust-registry)
https://grantex.ai/docs/delegation
"""
    pages = parse_llms_text(llms_text, "https://grantex.ai")

    assert [page.slug for page in pages] == ["scopes", "trust-registry", "delegation"]
    assert pages[0].description == "Scope documentation"
    assert str(pages[1].url) == "https://grantex.ai/docs/trust-registry"

