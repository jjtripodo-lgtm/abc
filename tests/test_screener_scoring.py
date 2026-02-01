from data.stub_provider import StubProvider
from lynch.screener import screen_fundamentals


def test_screen_returns_ranked_results():
    provider = StubProvider()
    fundamentals = [provider.get_fundamentals(ticker) for ticker in provider.list_universe()]
    results = screen_fundamentals(fundamentals, risk_tolerance="balanced")

    assert len(results) >= 10
    assert results[0].score >= results[-1].score


def test_hard_fail_for_negative_fcf_and_high_debt():
    provider = StubProvider()
    fundamentals = [provider.get_fundamentals("WBD")]
    results = screen_fundamentals(fundamentals, risk_tolerance="balanced")

    result = results[0]
    assert result.rating == "Fail"
    codes = {reason.code for reason in result.reasons}
    assert "DEBT_HIGH" in codes
    assert "FCF_WEAK" in codes

    for reason in result.reasons:
        assert reason.level in {"positive", "warning", "negative"}
        assert reason.code
        assert reason.message
