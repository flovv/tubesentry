from __future__ import annotations


class TubeSentryError(Exception):
    """Base exception for all TubeSentry errors."""


class MalformedPlacementCSVError(TubeSentryError):
    """Raised when an uploaded placement report CSV/TSV has invalid structure or missing columns."""


class QuotaExceededError(TubeSentryError):
    """Raised when YouTube Data API v3 daily quota limit is reached."""


class ProFeatureNotInstalledError(TubeSentryError):
    """Raised when a Pro feature is accessed without `tubesentry_pro` installed."""


class ProLicenseError(TubeSentryError):
    """Raised when Polar.sh license validation fails or license key is revoked/missing."""
