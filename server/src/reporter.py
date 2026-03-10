import logging
import socket
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import requests

from src.config import EMAIL_RECIPIENT, EMAIL_SENDER, RESEND_API_KEY
from src.database import get_pool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [LogSentinel-Report] %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MachineErrorSummary:
    hostname: str
    error_count: int
    critical_count: int


@dataclass(frozen=True)
class ResourceAlert:
    hostname: str
    alert_type: str
    value: float


@dataclass(frozen=True)
class FleetSummary:
    total_machines: int
    reporting_machines: int
    silent_machines: int
    machines_with_critical: int
    machines_with_error: int
    total_events: int
    critical_count: int
    error_count: int
    warning_count: int
    avg_reliability: float


@dataclass(frozen=True)
class ReportData:
    summary: FleetSummary
    silent_hosts: list[str] = field(default_factory=list)
    bsod_machines: list[tuple[str, str]] = field(default_factory=list)
    top_error_machines: list[MachineErrorSummary] = field(default_factory=list)
    resource_alerts: list[ResourceAlert] = field(default_factory=list)


def detect_silent_hosts(
    expected_hosts: list[str],
    last_seen_by_host: dict[str, datetime],
    now: datetime | None = None,
    collection_interval_hours: int = 1,
    missed_windows: int = 2,
) -> list[str]:
    reference = now or datetime.now(timezone.utc)
    cutoff = reference - timedelta(hours=collection_interval_hours * missed_windows)
    silent = []
    for host in expected_hosts:
        last_seen = last_seen_by_host.get(host)
        if last_seen is None or last_seen < cutoff:
            silent.append(host)
    return sorted(silent)


def sort_top_offenders(items: list[MachineErrorSummary], limit: int = 10) -> list[MachineErrorSummary]:
    return sorted(
        items,
        key=lambda item: (item.critical_count, item.error_count, item.hostname),
        reverse=True,
    )[:limit]


def build_report_html(data: ReportData) -> str:
    now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    hostname = socket.gethostname()
    summary = data.summary

    silent_html = (
        "".join(f"<li>{host}</li>" for host in data.silent_hosts[:20])
        or "<li>Nenhuma loja silenciosa</li>"
    )
    bsod_html = (
        "".join(f"<li>{host} - {ts}</li>" for host, ts in data.bsod_machines)
        or "<li>Nenhum BSOD detectado</li>"
    )
    offender_rows = "".join(
        "<tr>"
        f"<td style='padding:6px 10px;border-bottom:1px solid #eee'>{item.hostname}</td>"
        f"<td style='padding:6px 10px;border-bottom:1px solid #eee;text-align:center'>{item.error_count}</td>"
        f"<td style='padding:6px 10px;border-bottom:1px solid #eee;text-align:center'>{item.critical_count}</td>"
        "</tr>"
        for item in data.top_error_machines
    ) or (
        "<tr><td colspan='3' style='padding:8px 10px'>Sem ofensores relevantes</td></tr>"
    )
    resource_rows = "".join(
        "<tr>"
        f"<td style='padding:6px 10px;border-bottom:1px solid #eee'>{item.hostname}</td>"
        f"<td style='padding:6px 10px;border-bottom:1px solid #eee;text-align:center'>{item.alert_type}</td>"
        f"<td style='padding:6px 10px;border-bottom:1px solid #eee;text-align:center'>{item.value:.1f}</td>"
        "</tr>"
        for item in data.resource_alerts
    ) or (
        "<tr><td colspan='3' style='padding:8px 10px'>Sem alertas de recursos</td></tr>"
    )

    return f"""
<body style="font-family:Segoe UI,Arial,sans-serif;background:#f4f6f8;margin:0;padding:24px">
  <div style="max-width:860px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 3px 18px rgba(0,0,0,0.08)">
    <div style="padding:22px 28px;background:linear-gradient(135deg,#17324d,#365b7f);color:#ffffff">
      <h1 style="margin:0;font-size:24px">Log Sentinel - Relatorio Diario da Frota</h1>
      <div style="margin-top:6px;font-size:12px;opacity:0.9">{now} | Host gerador: {hostname}</div>
    </div>
    <div style="padding:24px 28px">
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px">
        <div style="background:#1f8f5f;color:#fff;padding:14px;border-radius:10px;text-align:center">
          <div style="font-size:28px;font-weight:700">{summary.reporting_machines}/{summary.total_machines}</div>
          <div style="font-size:12px">Reportando</div>
        </div>
        <div style="background:#c44a3d;color:#fff;padding:14px;border-radius:10px;text-align:center">
          <div style="font-size:28px;font-weight:700">{summary.silent_machines}</div>
          <div style="font-size:12px">Silenciosas</div>
        </div>
        <div style="background:#c27a17;color:#fff;padding:14px;border-radius:10px;text-align:center">
          <div style="font-size:28px;font-weight:700">{summary.error_count}</div>
          <div style="font-size:12px">Errors</div>
        </div>
        <div style="background:#5b4bb7;color:#fff;padding:14px;border-radius:10px;text-align:center">
          <div style="font-size:28px;font-weight:700">{summary.avg_reliability:.1f}</div>
          <div style="font-size:12px">Reliability medio</div>
        </div>
      </div>

      <h2 style="font-size:18px;color:#17324d">Resumo da frota</h2>
      <ul style="font-size:14px;line-height:1.7;color:#243746">
        <li>Total de eventos nas ultimas 24h: {summary.total_events}</li>
        <li>Lojas com ao menos um Critical: {summary.machines_with_critical}</li>
        <li>Lojas com ao menos um Error: {summary.machines_with_error}</li>
        <li>Warnings nas ultimas 24h: {summary.warning_count}</li>
      </ul>

      <h2 style="font-size:18px;color:#17324d">Lojas silenciosas</h2>
      <ul style="font-size:14px;line-height:1.7;color:#243746">{silent_html}</ul>

      <h2 style="font-size:18px;color:#17324d">BSOD detectados</h2>
      <ul style="font-size:14px;line-height:1.7;color:#243746">{bsod_html}</ul>

      <h2 style="font-size:18px;color:#17324d">Top ofensores</h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:18px">
        <tr style="background:#e9eef3">
          <th style="padding:8px 10px;text-align:left">Hostname</th>
          <th style="padding:8px 10px;text-align:center">Errors</th>
          <th style="padding:8px 10px;text-align:center">Critical</th>
        </tr>
        {offender_rows}
      </table>

      <h2 style="font-size:18px;color:#17324d">Alertas de recursos</h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px">
        <tr style="background:#e9eef3">
          <th style="padding:8px 10px;text-align:left">Hostname</th>
          <th style="padding:8px 10px;text-align:center">Tipo</th>
          <th style="padding:8px 10px;text-align:center">Valor</th>
        </tr>
        {resource_rows}
      </table>
    </div>
  </div>
</body>
""".strip()


async def collect_report_data(
    expected_machines: list[str] | None = None,
    now: datetime | None = None,
) -> ReportData:
    reference = now or datetime.now(timezone.utc)
    since_24h = reference - timedelta(hours=24)
    silent_cutoff = reference - timedelta(hours=2)
    pool = get_pool()

    async with pool.acquire() as conn:
        machine_total = await conn.fetchval("SELECT COUNT(*) FROM machines")
        reporting_total = await conn.fetchval(
            "SELECT COUNT(*) FROM machines WHERE last_seen >= $1",
            silent_cutoff,
        )

        severity_rows = await conn.fetch(
            """
            SELECT level, COUNT(*) AS count
            FROM events
            WHERE event_timestamp >= $1
            GROUP BY level
            """,
            since_24h,
        )
        severity_map = {row["level"]: row["count"] for row in severity_rows}

        top_rows = await conn.fetch(
            """
            SELECT hostname,
                   SUM(CASE WHEN level = 'Error' THEN 1 ELSE 0 END) AS error_count,
                   SUM(CASE WHEN level = 'Critical' THEN 1 ELSE 0 END) AS critical_count
            FROM events
            WHERE event_timestamp >= $1
            GROUP BY hostname
            HAVING SUM(CASE WHEN level IN ('Error', 'Critical') THEN 1 ELSE 0 END) > 0
            ORDER BY critical_count DESC, error_count DESC, hostname DESC
            LIMIT 10
            """,
            since_24h,
        )

        resource_rows = await conn.fetch(
            """
            WITH latest_metrics AS (
                SELECT DISTINCT ON (hostname)
                    hostname,
                    disk_free_percent,
                    ram_available_mb,
                    reliability_index
                FROM metrics
                ORDER BY hostname, collected_at DESC
            )
            SELECT hostname, 'disk' AS alert_type, disk_free_percent AS value
            FROM latest_metrics
            WHERE disk_free_percent < 15
            UNION ALL
            SELECT hostname, 'ram' AS alert_type, ram_available_mb AS value
            FROM latest_metrics
            WHERE ram_available_mb < 500
            UNION ALL
            SELECT hostname, 'reliability' AS alert_type, reliability_index AS value
            FROM latest_metrics
            WHERE reliability_index >= 0 AND reliability_index < 5
            ORDER BY hostname, alert_type
            """
        )

        avg_reliability = await conn.fetchval(
            """
            SELECT AVG(reliability_index)
            FROM (
                SELECT DISTINCT ON (hostname) hostname, reliability_index
                FROM metrics
                ORDER BY hostname, collected_at DESC
            ) latest_metrics
            WHERE reliability_index >= 0
            """
        )

        last_seen_rows = await conn.fetch("SELECT hostname, last_seen FROM machines")
        critical_hosts = await conn.fetchval(
            "SELECT COUNT(DISTINCT hostname) FROM events WHERE level = 'Critical' AND event_timestamp >= $1",
            since_24h,
        )
        error_hosts = await conn.fetchval(
            "SELECT COUNT(DISTINCT hostname) FROM events WHERE level IN ('Error', 'Critical') AND event_timestamp >= $1",
            since_24h,
        )
        total_events = await conn.fetchval(
            "SELECT COUNT(*) FROM events WHERE event_timestamp >= $1",
            since_24h,
        )
        bsod_rows = await conn.fetch(
            """
            SELECT hostname, collected_at
            FROM metrics
            WHERE bsod_detected = TRUE AND collected_at >= $1
            ORDER BY collected_at DESC
            LIMIT 20
            """,
            since_24h,
        )

    expected_hosts = expected_machines or [row["hostname"] for row in last_seen_rows]
    last_seen_map = {row["hostname"]: row["last_seen"] for row in last_seen_rows}
    silent_hosts = detect_silent_hosts(expected_hosts, last_seen_map, now=reference)
    top_offenders = sort_top_offenders(
        [
            MachineErrorSummary(
                hostname=row["hostname"],
                error_count=int(row["error_count"] or 0),
                critical_count=int(row["critical_count"] or 0),
            )
            for row in top_rows
        ]
    )
    resource_alerts = [
        ResourceAlert(
            hostname=row["hostname"],
            alert_type=row["alert_type"],
            value=float(row["value"]),
        )
        for row in resource_rows
    ]
    bsod_machines = [
        (row["hostname"], row["collected_at"].astimezone(timezone.utc).isoformat())
        for row in bsod_rows
    ]

    summary = FleetSummary(
        total_machines=int(machine_total or 0),
        reporting_machines=int(reporting_total or 0),
        silent_machines=len(silent_hosts),
        machines_with_critical=int(critical_hosts or 0),
        machines_with_error=int(error_hosts or 0),
        total_events=int(total_events or 0),
        critical_count=int(severity_map.get("Critical", 0)),
        error_count=int(severity_map.get("Error", 0)),
        warning_count=int(severity_map.get("Warning", 0)),
        avg_reliability=float(avg_reliability or 0),
    )

    return ReportData(
        summary=summary,
        silent_hosts=silent_hosts,
        bsod_machines=bsod_machines,
        top_error_machines=top_offenders,
        resource_alerts=resource_alerts,
    )


def send_report_email(html_body: str, subject: str | None = None) -> bool:
    if not RESEND_API_KEY or not EMAIL_RECIPIENT:
        logger.warning("Resend not configured, skipping email delivery")
        return False

    payload = {
        "from": EMAIL_SENDER,
        "to": [item.strip() for item in EMAIL_RECIPIENT.split(",") if item.strip()],
        "subject": subject or f"Log Sentinel - Relatorio Diario {datetime.now(timezone.utc):%d/%m/%Y}",
        "html": html_body,
    }
    response = requests.post(
        "https://api.resend.com/emails",
        json=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    if response.status_code >= 400:
        logger.error("Resend error %d: %s", response.status_code, response.text)
        return False

    logger.info("Daily report sent to %s", EMAIL_RECIPIENT)
    return True
