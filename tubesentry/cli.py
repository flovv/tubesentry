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
            print_banner=True,
            ad_url=ad_url,
            ad_text=ad_text,
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


if __name__ == "__main__":
    app()
