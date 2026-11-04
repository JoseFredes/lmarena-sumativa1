import pandas as pd
import pytest

from arena.sampling import complete_session_share, sample_rows, sample_sessions


@pytest.fixture
def votes():
    # s1 has 3 votes, s2 has 2, s3..s10 have 1 each
    sessions = ["s1"] * 3 + ["s2"] * 2 + [f"s{i}" for i in range(3, 11)]
    return pd.DataFrame({"evaluation_session_id": sessions, "v": range(len(sessions))})


def test_sample_rows_size_and_seed(votes):
    a, b = sample_rows(votes, 5, seed=1), sample_rows(votes, 5, seed=1)
    assert len(a) == 5 and a.equals(b)


def test_sample_sessions_keeps_sessions_whole(votes):
    out = sample_sessions(votes, 4, seed=3)
    assert out["evaluation_session_id"].nunique() == 4
    full_sizes = votes.groupby("evaluation_session_id").size()
    out_sizes = out.groupby("evaluation_session_id").size()
    assert (out_sizes == full_sizes.reindex(out_sizes.index)).all()


@pytest.mark.parametrize("n", [0, -1, 999])
def test_invalid_sizes_raise(votes, n):
    with pytest.raises(ValueError, match="between"):
        sample_rows(votes, n)
    with pytest.raises(ValueError, match="between"):
        sample_sessions(votes, n)


def test_complete_session_share(votes):
    whole = sample_sessions(votes, 10)
    assert complete_session_share(whole, votes) == 1.0
    assert complete_session_share(votes.iloc[[0, 3]], votes) == 0.0


def test_complete_session_share_partial_and_empty(votes):
    # s1 (3 votes) present with 2 of 3 rows; s2 (2 votes) present complete -> 0.5
    assert complete_session_share(votes.iloc[[0, 1, 3, 4]], votes) == 0.5
    # only single-vote sessions present -> no multi-vote session to judge
    assert pd.isna(complete_session_share(votes.iloc[5:], votes))
