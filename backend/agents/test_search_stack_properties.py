"""
Property-based tests for the treatment-exploration-search Search_Stack.

Feature: treatment-exploration-search
Testing framework: Hypothesis
"""

from hypothesis import given, settings, strategies as st

from agents.infrastructure.models import SearchResult
from agents.infrastructure.web_search import ResultMerger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_result(url: str, quality_score: float, title: str = "Title") -> SearchResult:
    """Create a minimal SearchResult for testing."""
    return SearchResult(
        title=title or "Title",
        url=url,
        snippet="snippet",
        source_domain="example.com",
        quality_score=quality_score,
    )


# Strategy: valid quality scores in [0.0, 1.0]
quality_score_st = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Strategy: non-empty URL strings (simple ASCII to avoid SearchResult validation issues)
url_st = st.from_regex(r"https://[a-z]{1,10}\.[a-z]{2,4}/[a-z0-9]{0,10}", fullmatch=True)

# Strategy: a single SearchResult
search_result_st = st.builds(
    make_result,
    url=url_st,
    quality_score=quality_score_st,
)

# Strategy: a list of SearchResult objects
result_list_st = st.lists(search_result_st, min_size=0, max_size=20)

# Strategy: a list of lists of SearchResult objects
result_lists_st = st.lists(result_list_st, min_size=0, max_size=5)


# ---------------------------------------------------------------------------
# Property 11: ResultMerger deduplication keeps higher quality score
# ---------------------------------------------------------------------------

# Feature: treatment-exploration-search, Property 11: ResultMerger deduplication keeps higher quality score
@settings(max_examples=100)
@given(
    url=url_st,
    score_a=quality_score_st,
    score_b=quality_score_st,
    extra_lists=result_lists_st,
)
def test_result_merger_deduplication_keeps_higher_quality_score(
    url: str, score_a: float, score_b: float, extra_lists
):
    """
    For any two SearchResult entries sharing the same URL but with different
    quality_score values, ResultMerger.merge must return exactly one entry for
    that URL and it must be the entry with the higher quality_score.

    Validates: Requirements 4.2
    """
    result_a = make_result(url, score_a, title="Result A")
    result_b = make_result(url, score_b, title="Result B")

    result_lists = [[result_a], [result_b]] + extra_lists
    merged = ResultMerger.merge(result_lists, max_results=1000)

    # Exactly one entry for the shared URL
    url_entries = [r for r in merged if r.url == url]
    assert len(url_entries) == 1

    # That entry must have the higher quality_score
    expected_score = max(score_a, score_b)
    assert url_entries[0].quality_score == expected_score


# ---------------------------------------------------------------------------
# Property 12: ResultMerger output is sorted by quality score descending
# ---------------------------------------------------------------------------

# Feature: treatment-exploration-search, Property 12: ResultMerger output is sorted by quality score descending
@settings(max_examples=100)
@given(result_lists=result_lists_st)
def test_result_merger_output_sorted_descending(result_lists):
    """
    For any collection of SearchResult lists, the list returned by
    ResultMerger.merge must be sorted such that
    results[i].quality_score >= results[i+1].quality_score for all valid i.

    Validates: Requirements 4.3
    """
    merged = ResultMerger.merge(result_lists, max_results=1000)

    for i in range(len(merged) - 1):
        assert merged[i].quality_score >= merged[i + 1].quality_score, (
            f"Sort order violated at index {i}: "
            f"{merged[i].quality_score} < {merged[i+1].quality_score}"
        )


# ---------------------------------------------------------------------------
# Property 13: ResultMerger output never exceeds max_results
# ---------------------------------------------------------------------------

# Feature: treatment-exploration-search, Property 13: ResultMerger output never exceeds max_results
@settings(max_examples=100)
@given(
    result_lists=result_lists_st,
    max_results=st.integers(min_value=0, max_value=50),
)
def test_result_merger_cap_never_exceeds_max_results(result_lists, max_results: int):
    """
    For any collection of SearchResult lists and any max_results = n,
    ResultMerger.merge must return a list of length <= n.

    Validates: Requirements 4.4
    """
    merged = ResultMerger.merge(result_lists, max_results=max_results)
    assert len(merged) <= max_results, (
        f"Expected len(merged) <= {max_results}, got {len(merged)}"
    )
