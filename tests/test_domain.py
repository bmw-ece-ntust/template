"""Tests for pure domain models: topology, health."""

from __future__ import annotations

from controllers.health import HealthService
from models.health import Health
from models.parameters import NodeType
from models.topology import NetworkTopology, NodeInfo


def test_topology_add_get_remove() -> None:
    topo = NetworkTopology()
    topo.add(NodeInfo("cell-0", "gnb-1", "ericsson"))
    assert topo.get("cell-0").vendor_id == "ericsson"
    topo.remove("cell-0")
    assert topo.get("cell-0") is None
    topo.remove("missing")  # no-op must not raise


def test_topology_filters_by_type_and_active_state() -> None:
    topo = NetworkTopology()
    topo.add(NodeInfo("cell-0", "gnb-1", "ericsson", NodeType.GNB))
    topo.add(NodeInfo("ap-1", "ap-cluster", "aruba", NodeType.WIFI_AP))
    topo.set_active("cell-0", active=False)
    assert {n.cell_id for n in topo.cells()} == {"cell-0", "ap-1"}
    assert [n.cell_id for n in topo.cells(NodeType.WIFI_AP)] == ["ap-1"]
    assert [n.cell_id for n in topo.active_cells()] == ["ap-1"]


def test_set_active_on_missing_cell_is_noop() -> None:
    topo = NetworkTopology()
    topo.set_active("nope", active=True)  # must not raise
    assert topo.cells() == []


def test_health_service_and_serialization() -> None:
    health = HealthService("template-app").get_health()
    assert isinstance(health, Health)
    assert health.status == "OK"
    assert health.service == "template-app"
    payload = health.to_dict()
    assert payload["status"] == "OK"
    assert set(payload) == {"status", "service", "timestamp"}
