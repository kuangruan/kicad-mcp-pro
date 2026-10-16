"""Native IPC companion tests (no GUI, socket or external network required)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "kicad-plugin"))

from companion_core import (  # noqa: E402
    BoardSummary,
    backend_status,
    board_summary,
    dashboard_url,
    sync_board_context,
)
from context import CompanionHealthStatus  # noqa: E402


def test_ipc_summary_is_read_only(tmp_path: Path) -> None:
    board = Mock()
    board.name = "sample.kicad_pcb"
    board.get_project.return_value.name = "sample"
    board.get_project.return_value.path = str(tmp_path / "sample.kicad_pro")
    board.get_footprints.return_value = [1, 2]
    board.get_nets.return_value = [1, 2, 3]
    board.get_selection.return_value = []
    client = Mock()
    client.get_board.return_value = board

    result = board_summary(lambda: client)

    assert result.name == "sample.kicad_pcb"
    assert result.project == "sample"
    assert result.footprints == 2
    assert result.nets == 3
    assert result.selected == 0
    client.get_board.assert_called_once_with()
    board.get_selection.assert_called_once_with()


def test_unavailable_kicad_reports_failure() -> None:
    def disconnected() -> None:
        raise OSError("IPC disconnected")

    with pytest.raises(OSError, match="disconnected"):
        board_summary(disconnected)


def test_backend_status_uses_existing_health_contract() -> None:
    client = Mock()
    client.health.return_value = CompanionHealthStatus(
        "ready", "Backend is healthy and compatible.", "4.3.0"
    )
    factory = Mock(return_value=client)
    loader = Mock(return_value={"schema_version": "test"})

    ok, message = backend_status(client_factory=factory, compatibility_loader=loader)

    assert ok and "healthy" in message
    factory.assert_called_once_with("http://127.0.0.1:3334", auth_token="")
    client.health.assert_called_once_with({"schema_version": "test"})


def test_bad_backend_is_not_marked_ready() -> None:
    client = Mock()
    client.health.return_value = CompanionHealthStatus(
        "backend_unreachable", "Backend not reachable."
    )
    ok, message = backend_status(
        client_factory=lambda *_args, **_kwargs: client,
        compatibility_loader=lambda: {},
    )
    assert not ok and "reachable" in message


def test_publish_context_uses_existing_mcp_client_contract(tmp_path: Path) -> None:
    client = Mock()
    client.health.return_value = CompanionHealthStatus("ready", "OK", "4.3.0")
    factory = Mock(return_value=client)
    snapshot = BoardSummary("board.kicad_pcb", "board", 3, 2, 1, str(tmp_path), "U1")

    sync_board_context(snapshot, client_factory=factory, compatibility_loader=lambda: {})

    args = client.push.call_args.args[0]
    assert args["file_type"] == "pcb"
    assert args["active_file"] == "board.kicad_pcb"
    assert args["selected_reference"] == "U1"
    assert args["snapshot"]["projectRoot"] == str(tmp_path)


def test_incompatible_backend_never_publishes_context() -> None:
    client = Mock()
    client.health.return_value = CompanionHealthStatus("backend_incompatible", "Mismatch")
    with pytest.raises(RuntimeError, match="Mismatch"):
        sync_board_context(
            BoardSummary("board.kicad_pcb", "board", 0, 0, 0),
            client_factory=lambda *_args, **_kwargs: client,
            compatibility_loader=lambda: {},
        )
    client.push.assert_not_called()


def test_dashboard_is_loopback_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KICAD_MCP_URL", raising=False)
    assert dashboard_url("#tools-catalog") == "http://127.0.0.1:3334/ui#tools-catalog"
    monkeypatch.setenv("KICAD_MCP_URL", "https://example.com")
    with pytest.raises(ValueError, match="loopback"):
        dashboard_url()


def test_dashboard_custom_local_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KICAD_MCP_URL", "http://localhost:3434")
    assert dashboard_url() == "http://localhost:3434/ui"
