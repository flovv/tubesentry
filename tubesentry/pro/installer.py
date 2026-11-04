from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

import httpx

from tubesentry.contracts.exceptions import ProLicenseError

POLAR_VALIDATE_URL = "https://api.polar.sh/v1/customer-portal/license-keys/validate"
POLAR_ORG_ID = os.getenv("POLAR_ORG_ID", "org_tubesentry_production")
WHEEL_INDEX_URL = "https://wheels.tubesentry.dev/simple"


def install_pro(
    api_key: str,
    index_url: str | None = None,
    local_path: str | None = None,
) -> bool:
    """Verifies Polar.sh license key and installs the matching `tubesentry-pro` package.

    Args:
        api_key: Polar.sh license key (e.g. 'TS_PRO_...').
        index_url: Optional private wheel index URL.
        local_path: Optional path to local directory or wheel for development/testing.

    Returns:
        bool: True if installation and verification succeeded.

    Raises:
        ProLicenseError: If license validation fails.
        RuntimeError: If pip wheel installation fails.
    """
    if not api_key:
        raise ProLicenseError("License key must not be empty.")

    # 1. License Verification: Allow test keys or offline mock flag
    is_test_key = (
        api_key.startswith(("TS_TEST_", "TS_DEV_")) or os.getenv("TUBESENTRY_MOCK_AUTH") == "1"
    )

    if not is_test_key:
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(
                    POLAR_VALIDATE_URL,
                    json={"key": api_key, "organization_id": POLAR_ORG_ID},
                )
            if resp.status_code != 200:
                raise ProLicenseError(
                    f"Invalid or revoked TubeSentry Pro license key (HTTP {resp.status_code}). "
                    "Obtain a key at https://buy.polar.sh/polar_cl_lRuifr3uJS0LR0k6frhg3JEKBRZNQq75hv7cS2am9cX"
                )
            data = resp.json()
            if data.get("status") != "granted":
                raise ProLicenseError(
                    f"TubeSentry Pro license is not active (status: '{data.get('status')}')."
                )
        except httpx.RequestError as exc:
            raise ProLicenseError(
                f"Could not reach Polar.sh license verification server ({exc}). Check internet connectivity."
            ) from exc

    # Set environment variable for active session
    os.environ["TUBESENTRY_API_KEY"] = api_key

    if is_test_key and not local_path:
        from tubesentry.pro import bridge

        bridge.HAS_PRO = True
        return True

    # 2. Check if tubesentry_pro is already installed in the current environment
    already_installed = False
    try:
        importlib.import_module("tubesentry_pro")
        already_installed = True
    except ImportError:
        pass

    if not already_installed:
        # Check for local repository (workspace development)
        possible_local_dirs = [
            Path(local_path) if local_path else None,
            Path(__file__).resolve().parents[3] / "tubesentry-pro-private",
            Path.cwd() / "tubesentry-pro-private",
        ]

        installed = False
        for p in possible_local_dirs:
            if p and p.exists() and (p / "pyproject.toml").exists():
                cmd = [sys.executable, "-m", "pip", "install", "-e", str(p)]
                proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
                if proc.returncode == 0:
                    installed = True
                    break

        if not installed:
            if is_test_key:
                from tubesentry.pro import bridge

                bridge.HAS_PRO = True
                return True
            effective_index = index_url or WHEEL_INDEX_URL
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"--extra-index-url={effective_index}",
                "tubesentry-pro",
            ]
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(
                    f"Failed to install tubesentry-pro package via pip:\n{proc.stderr}\n"
                    "If running in offline/local mode, ensure tubesentry-pro-private directory is available."
                )

    # 3. Reload bridge
    from tubesentry.pro import bridge

    try:
        bridge.tubesentry_pro = importlib.import_module("tubesentry_pro")
        bridge.HAS_PRO = True
    except ImportError:
        pass

    return True
