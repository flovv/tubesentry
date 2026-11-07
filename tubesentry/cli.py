from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

import tubesentry
from tubesentry.contracts.exceptions import ProLicenseError
from tubesentry.io.fixtures import generate_synthetic_placement_csv
from tubesentry.pro.installer import install_pro

app = typer.Typer(
    name="tubesentry",
    help="TubeSentry — Local-First YouTube & PMax Ad Placement Waste Auditor & MCP Server",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def demo(
    out_dir: Path = typer.Option(
        Path("./demo_youtube"),
        "--out-dir",
        "-o",
        help="Directory to save the generated synthetic placement CSV report.",
    ),
    rows: int = typer.Option(
        25000,
        "--rows",
        "-n",
        help="Number of synthetic placement rows to generate.",
    ),
    lang: str = typer.Option(
        "de",
        "--lang",
        "-l",
        help="Localized number and text formatting ('de' or 'en').",
    ),
) -> None:
    """Generates a realistic 25,000-row Google Ads PMax/YouTube placement CSV and runs an immediate audit."""
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_file = out_dir / "google_ads_where_ads_showed_sample.csv"

    console.print(
        f"[bold blue][*] Generating {rows:,} synthetic Google Ads placement rows...[/bold blue]"
    )
    generate_synthetic_placement_csv(
        output_path=csv_file,
        num_rows=rows,
        language=lang,
    )
    console.print(f"[bold green][OK] Saved synthetic report to:[/bold green] {csv_file}")
    console.print("[bold yellow][*] Running immediate TubeSentry diagnostic pass...[/bold yellow]\n")

    tubesentry.audit_placements(
        report=csv_file,
        target_languages=["de", "en"] if lang == "de" else ["en"],
        print_banner=True,
    )


@app.command()
def audit(
    report_csv: Path = typer.Argument(
        ...,
        help="Path to Google Ads or DV360 placement CSV/TSV export file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    lang: str = typer.Option(
        "de,en",
        "--lang",
        "-l",
        help="Comma-separated target languages for geotargeting verification (e.g. 'de,en').",
    ),
    cpa: float | None = typer.Option(
        None,
        "--cpa",
        help="Target CPA in account currency to evaluate Performance Sinkhole bleed.",
    ),
    key: str | None = typer.Option(
        None,
        "--key",
        "-k",
        help="TubeSentry Pro Polar.sh API key (or set TUBESENTRY_API_KEY).",
    ),
    out_exclusions: Path | None = typer.Option(
        None,
        "--out-exclusions",
        help="Path to export reactive Google Ads Editor exclusion CSV (Pro feature).",
    ),
    out_65k: Path | None = typer.Option(
        None,
        "--out-65k",
        help="Path to export full 65,000-channel protection shield CSV (Pro feature).",
    ),
    html: Path | None = typer.Option(
        None,
        "--html",
        help="Path to export interactive white-label HTML audit deck (Pro feature).",
    ),
    ad_url: str | None = typer.Option(
        None,
        "--ad-url",
        help="YouTube Ad video URL or creative link to profile targeting fit using Gemini.",
    ),
    ad_text: str | None = typer.Option(
        None,
        "--ad-text",
        help="Ad copy, transcript, or campaign brief to profile ICP intent.",
    ),
    export_script: Path | None = typer.Option(
        None,
        "--export-script",
        "-s",
        help="Path to export a copy-paste Google Ads JavaScript automation script (e.g. cleanup.js).",
    ),
) -> None:
    """Audits a Google Ads or DV360 YouTube placement report for wasted ad spend."""
    target_languages = [s.strip().lower() for s in lang.split(",") if s.strip()]

    try:
        tubesentry.audit_placements(
            report=report_csv,
            target_languages=target_languages,
            target_cpa=cpa,
            api_key=key,
            export_exclusions_csv=str(out_exclusions) if out_exclusions else None,
            export_65k_shield_csv=str(out_65k) if out_65k else None,
            export_html_deck=str(html) if html else None,
            export_google_ads_script=str(export_script) if export_script else None,
            print_banner=True,
            ad_url=ad_url,
            ad_text=ad_text,
        )
        if export_script:
            console.print(
                f"\n[bold green][OK] Exported Google Ads JavaScript automation to:[/bold green] {export_script}"
            )
            console.print(
                "[dim]Copy and paste into Google Ads -> Tools & Settings -> Bulk Actions -> Scripts.[/dim]"
            )
    except Exception as e:
        err_console.print(f"[bold red]Audit error:[/bold red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def mcp() -> None:
    """Starts the FastMCP stdio server for Claude Desktop, Claude Code, and Cursor."""
    from tubesentry.mcp_server import main as run_mcp

    run_mcp()


@app.command()
def auth(
    key: str | None = typer.Option(
        None,
        "--key",
        "-k",
        help="TubeSentry Pro license key from Polar.sh (e.g. 'TS_PRO_...').",
    ),
) -> None:
    """Validates a Polar.sh license key and installs/activates TubeSentry Pro."""
    license_key = key
    if not license_key:
        license_key = typer.prompt("TubeSentry Pro license key", hide_input=True)

    console.print("[bold blue][*] Validating license key with Polar.sh...[/bold blue]")
    try:
        success = install_pro(license_key)
        if success:
            console.print(
                "[bold green][OK] License validated successfully! TubeSentry Pro is active.[/bold green]"
            )
        else:
            console.print("[bold red][FAIL] Installation failed.[/bold red]")
            raise typer.Exit(code=1)
    except ProLicenseError as e:
        console.print(f"[bold red][FAIL] License validation error:[/bold red] {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[bold red][FAIL] Error installing Pro extension:[/bold red] {e}")
        raise typer.Exit(code=1) from e


skill_app = typer.Typer(
    name="skill",
    help="Manage and install the TubeSentry AI agent skill.",
    no_args_is_help=True,
)
app.add_typer(skill_app, name="skill")


@skill_app.command(name="install")
def skill_install(
    target_dir: Path | None = typer.Option(
        None,
        "--target-dir",
        "-t",
        help="Custom destination directory (defaults to ./.agents/skills or ./.claude/skills).",
    ),
) -> None:
    """Installs the TubeSentry Agent Skill (SKILL.md) into the workspace for AI agents."""
    from tubesentry.skills import install_skill

    try:
        dest_file = install_skill(target_dir=target_dir)
        console.print(
            f"[bold green][OK] TubeSentry Agent Skill installed to:[/bold green] {dest_file}"
        )
        console.print(
            "[dim]AI agents (Antigravity, Claude Code, Cursor, Codex) in this workspace can now use `youtube-placement-audit`.[/dim]"
        )
    except Exception as e:
        err_console.print(f"[bold red]Failed to install skill:[/bold red] {e}")
        raise typer.Exit(code=1) from e


@skill_app.command(name="show")
def skill_show() -> None:
    """Outputs the markdown instructions of the bundled TubeSentry Agent Skill."""
    from tubesentry.skills import get_bundled_skill_text

    console.print(get_bundled_skill_text())


@skill_app.command(name="path")
def skill_path() -> None:
    """Prints the local filesystem path of the bundled SKILL.md file."""
    from tubesentry.skills import get_bundled_skill_path

    console.print(str(get_bundled_skill_path()))


export_app = typer.Typer(
    name="export",
    help="Export placement exclusions as Google Ads Scripts or BigQuery SQL.",
    no_args_is_help=True,
)
app.add_typer(export_app, name="export")


@export_app.command(name="script")
def export_script_cmd(
    report_csv: Path = typer.Option(
        ...,
        "--report",
        "-r",
        help="Path to Google Ads placement CSV report.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    out_file: Path = typer.Option(
        Path("cleanup_placements.js"),
        "--out",
        "-o",
        help="Destination path for the Google Ads JavaScript file.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--live",
        help="Whether the generated script defaults to dry-run preview mode.",
    ),
    mode: str = typer.Option(
        "SHARED_LIST",
        "--mode",
        "-m",
        help="Exclusion mode: 'SHARED_LIST' (account-wide) or 'CAMPAIGNS'.",
    ),
    shared_list_name: str = typer.Option(
        "TubeSentry Waste Shield",
        "--list-name",
        help="Name of the account-level Excluded Placement List.",
    ),
) -> None:
    """Generates a self-contained Google Ads JavaScript automation script from a placement report."""
    from tubesentry.integrations import generate_google_ads_script

    report = tubesentry.audit_placements(report=report_csv, print_banner=False)
    channel_ids = [
        r.channel_id
        for r in report.top_offenders
        if r.channel_id and not r.channel_id.startswith("UC••••")
    ]
    script_js = generate_google_ads_script(
        channel_ids_or_urls=channel_ids,
        dry_run=dry_run,
        mode=mode,
        shared_list_name=shared_list_name,
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(script_js, encoding="utf-8")
    console.print(f"[bold green][OK] Google Ads Script exported to:[/bold green] {out_file}")
    console.print(
        f"[dim]Generated {len(channel_ids)} placement exclusions. Paste into Google Ads -> Tools -> Scripts.[/dim]"
    )


@export_app.command(name="bigquery")
def export_bigquery_cmd(
    out_file: Path = typer.Option(
        Path("tubesentry_bigquery.sql"),
        "--out",
        "-o",
        help="Destination path for the BigQuery SQL query file.",
    ),
    dataset: str = typer.Option(
        "google_ads_export",
        "--dataset",
        "-d",
        help="BigQuery dataset name containing Google Ads DTS tables.",
    ),
    customer_id: str = typer.Option(
        "",
        "--customer-id",
        "-c",
        help="Optional Google Ads customer ID suffix (e.g. 1234567890).",
    ),
    lookback_days: int = typer.Option(
        30,
        "--days",
        help="Lookback period in days.",
    ),
    target_cpa: float = typer.Option(
        40.0,
        "--cpa",
        help="Target CPA threshold for performance sinkholes.",
    ),
    as_dbt: bool = typer.Option(
        False,
        "--dbt",
        help="Format output as a dbt model with Jinja configuration.",
    ),
) -> None:
    """Exports a BigQuery Data Transfer Service (DTS) SQL model to audit placements in your data warehouse."""
    from tubesentry.integrations import generate_bigquery_dts_sql

    sql = generate_bigquery_dts_sql(
        dataset=dataset,
        customer_id=customer_id,
        lookback_days=lookback_days,
        target_cpa=target_cpa,
        as_dbt=as_dbt,
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(sql, encoding="utf-8")
    console.print(f"[bold green][OK] BigQuery SQL model exported to:[/bold green] {out_file}")
    console.print(
        "[dim]Plug this query into BigQuery Studio, Scheduled Queries, or your dbt project.[/dim]"
    )


if __name__ == "__main__":
    app()
