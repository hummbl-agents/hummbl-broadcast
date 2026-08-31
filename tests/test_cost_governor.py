"""Cost governor tests."""

import time

from hummbl_broadcast.config import CostGovernorConfig
from hummbl_broadcast.cost import CostGovernor


def test_can_spend_under_cap():
    g = CostGovernor(CostGovernorConfig(max_cost_per_hour_usd=1.0, max_cost_per_day_usd=10.0))
    assert g.can_spend(0.5)
    g.record(0.5)
    assert g.can_spend(0.4)
    assert not g.can_spend(0.6)


def test_snapshot_reflects_recent():
    g = CostGovernor(CostGovernorConfig(max_cost_per_hour_usd=10.0, max_cost_per_day_usd=100.0))
    g.record(2.0)
    g.record(3.0)
    snap = g.snapshot()
    assert snap["last_hour_usd"] == 5.0
    assert snap["hour_cap_usd"] == 10.0


def test_can_spend_respects_day_cap():
    g = CostGovernor(CostGovernorConfig(max_cost_per_hour_usd=100.0, max_cost_per_day_usd=5.0))
    g.record(4.0)
    assert g.can_spend(1.0)
    assert not g.can_spend(2.0)
