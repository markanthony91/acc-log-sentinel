from datetime import datetime, timezone

from src.reporter import (
    FleetSummary,
    MachineErrorSummary,
    ReportData,
    ResourceAlert,
    build_report_html,
    detect_silent_hosts,
    sort_top_offenders,
)


def test_detect_silent_hosts():
    now = datetime(2026, 3, 10, 14, 0, tzinfo=timezone.utc)
    expected = ["LOJA-001", "LOJA-002", "LOJA-003"]
    last_seen = {
        "LOJA-001": datetime(2026, 3, 10, 13, 10, tzinfo=timezone.utc),
        "LOJA-002": datetime(2026, 3, 10, 11, 30, tzinfo=timezone.utc),
    }

    silent = detect_silent_hosts(expected, last_seen, now=now)

    assert silent == ["LOJA-002", "LOJA-003"]


def test_sort_top_offenders():
    offenders = [
        MachineErrorSummary(hostname="LOJA-001", error_count=10, critical_count=0),
        MachineErrorSummary(hostname="LOJA-002", error_count=5, critical_count=2),
        MachineErrorSummary(hostname="LOJA-003", error_count=12, critical_count=1),
    ]

    ordered = sort_top_offenders(offenders)

    assert [item.hostname for item in ordered] == ["LOJA-002", "LOJA-003", "LOJA-001"]


def test_build_report_html():
    data = ReportData(
        summary=FleetSummary(
            total_machines=134,
            reporting_machines=130,
            silent_machines=4,
            machines_with_critical=3,
            machines_with_error=11,
            total_events=250,
            critical_count=3,
            error_count=45,
            warning_count=202,
            avg_reliability=7.4,
        ),
        silent_hosts=["LOJA-004"],
        bsod_machines=[("LOJA-042", "2026-03-10T13:42:11+00:00")],
        top_error_machines=[MachineErrorSummary("LOJA-042", 12, 2)],
        resource_alerts=[ResourceAlert("LOJA-009", "disk", 10.5)],
    )

    html = build_report_html(data)

    assert "134" in html
    assert "LOJA-004" in html
    assert "LOJA-042" in html
    assert "LOJA-009" in html
    assert "Relatorio Diario da Frota" in html
