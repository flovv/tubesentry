from __future__ import annotations

import json
from collections.abc import Sequence


def generate_google_ads_script(
    channel_ids_or_urls: Sequence[str],
    dry_run: bool = True,
    mode: str = "SHARED_LIST",
    shared_list_name: str = "TubeSentry Waste Shield",
    campaign_name_contains: str = "",
    batch_size: int = 1000,
) -> str:
    """Generates a self-contained, copy-paste Google Ads JavaScript automation script.

    PPC managers and media buyers can paste this directly into Google Ads Scripts
    (Tools and Settings -> Bulk Actions -> Scripts) to automatically exclude
    identified waste placements at the Shared List or Campaign level.

    Args:
        channel_ids_or_urls: List of YouTube channel IDs or URLs to exclude.
        dry_run: If True, logs intended exclusions to Logger without applying changes.
        mode: 'SHARED_LIST' (creates/populates account-level exclusion list) or 'CAMPAIGNS'.
        shared_list_name: Name of the account-level Excluded Placement List.
        campaign_name_contains: Filter campaign names when mode is 'CAMPAIGNS'.
        batch_size: Maximum placements to process per execution (default 1000).

    Returns:
        str: Executable JavaScript code compatible with modern Google Ads Scripts (V8).
    """
    clean_channels = []
    for item in channel_ids_or_urls:
        val = str(item).strip()
        if not val or val.startswith("UC••••"):
            continue
        clean_channels.append(val)

    # Format JSON array with 2-space indentation
    channels_json = json.dumps(clean_channels, indent=2)

    script = f"""/**
 * TubeSentry Automated Placement Exclusion Script
 * Generated automatically by TubeSentry (https://github.com/flovv/tubesentry)
 *
 * Excludes identified waste YouTube channels (Made-for-Kids, passive audio,
 * underage gaming, foreign script leakage, and performance sinkholes).
 *
 * Setup Instructions:
 * 1. Open Google Ads -> Tools & Settings -> Bulk Actions -> Scripts.
 * 2. Click the '+' button to create a new script.
 * 3. Replace all default editor content with this code.
 * 4. Verify CONFIG settings below (DRY_RUN is enabled by default).
 * 5. Click 'Preview' to view the execution log safely.
 * 6. Set DRY_RUN: false, authorize script access, and click 'Run' or schedule daily.
 */

var CONFIG = {{
  // Test mode: true = preview in logs without making actual exclusions; false = apply changes
  DRY_RUN: {str(dry_run).lower()},

  // Exclusion mode: 'SHARED_LIST' (recommended account-wide) or 'CAMPAIGNS'
  EXCLUSION_MODE: '{mode}',

  // Name of the account-level Shared Placement Exclusion List
  SHARED_LIST_NAME: '{shared_list_name}',

  // Filter campaigns by name when using 'CAMPAIGNS' mode (leave empty for all enabled video campaigns)
  CAMPAIGN_NAME_CONTAINS: '{campaign_name_contains}',

  // Max exclusions to process per run (Google Ads script limit is 30 minutes)
  BATCH_SIZE: {batch_size}
}};

// Flagged channel IDs or URLs to exclude ({len(clean_channels)} total):
var CHANNELS_TO_EXCLUDE = {channels_json};

function main() {{
  Logger.log("============================================================");
  Logger.log(" TubeSentry Placement Exclusion Automation");
  Logger.log("============================================================");
  Logger.log("Total channels queued: " + CHANNELS_TO_EXCLUDE.length);
  Logger.log("Exclusion Mode:       " + CONFIG.EXCLUSION_MODE);
  Logger.log("Dry Run:              " + (CONFIG.DRY_RUN ? "ENABLED (preview only, no changes)" : "DISABLED (LIVE EXCLUSIONS ACTIVE)"));
  Logger.log("------------------------------------------------------------");

  if (CHANNELS_TO_EXCLUDE.length === 0) {{
    Logger.log("No valid channel IDs to exclude. Exiting.");
    return;
  }}

  if (CONFIG.EXCLUSION_MODE === 'SHARED_LIST') {{
    applyToSharedList(CHANNELS_TO_EXCLUDE);
  }} else {{
    applyToCampaigns(CHANNELS_TO_EXCLUDE);
  }}
}}

function formatPlacementUrl(raw) {{
  if (raw.indexOf("youtube.com") !== -1) {{
    return raw;
  }}
  return "youtube.com/channel/" + raw;
}}

function applyToSharedList(channels) {{
  var listIterator = AdsApp.excludedPlacementLists()
    .withCondition("name = '" + CONFIG.SHARED_LIST_NAME.replace(/'/g, "\\\\'") + "'")
    .get();

  var list = null;
  if (listIterator.hasNext()) {{
    list = listIterator.next();
    Logger.log("Found existing Shared Placement Exclusion List: " + CONFIG.SHARED_LIST_NAME);
  }} else {{
    if (!CONFIG.DRY_RUN) {{
      var builder = AdsApp.newExcludedPlacementListBuilder()
        .withName(CONFIG.SHARED_LIST_NAME)
        .build();
      list = builder.getResult();
      Logger.log("Created new Shared Placement Exclusion List: " + CONFIG.SHARED_LIST_NAME);
    }} else {{
      Logger.log("[DRY RUN] Would create Shared Placement Exclusion List: " + CONFIG.SHARED_LIST_NAME);
    }}
  }}

  var count = 0;
  var limit = Math.min(channels.length, CONFIG.BATCH_SIZE);
  for (var i = 0; i < limit; i++) {{
    var url = formatPlacementUrl(channels[i]);
    if (CONFIG.DRY_RUN) {{
      Logger.log("[DRY RUN] Would add to Shared List: " + url);
      count++;
    }} else {{
      try {{
        list.addExcludedPlacement(url);
        count++;
        if (count % 100 === 0) {{
          Logger.log("Added " + count + " / " + limit + " exclusions...");
        }}
      }} catch (e) {{
        Logger.log("Warning: Failed to exclude " + url + ": " + e.message);
      }}
    }}
  }}

  Logger.log("------------------------------------------------------------");
  Logger.log("Shared List execution complete. Processed " + count + " placements.");
  if (CONFIG.DRY_RUN) {{
    Logger.log("REMINDER: Set CONFIG.DRY_RUN = false and re-run to apply exclusions.");
  }}
}}

function applyToCampaigns(channels) {{
  var campaignSelector = AdsApp.videoCampaigns().withCondition("status = 'ENABLED'");
  if (CONFIG.CAMPAIGN_NAME_CONTAINS) {{
    campaignSelector = campaignSelector.withCondition(
      "name CONTAINS_IGNORE_CASE '" + CONFIG.CAMPAIGN_NAME_CONTAINS.replace(/'/g, "\\\\'") + "'"
    );
  }}

  var campaignIterator = campaignSelector.get();
  var campaigns = [];
  while (campaignIterator.hasNext()) {{
    campaigns.push(campaignIterator.next());
  }}

  Logger.log("Found " + campaigns.length + " matching enabled video campaign(s).");
  if (campaigns.length === 0) {{
    Logger.log("No enabled video campaigns found matching criteria.");
    return;
  }}

  var limit = Math.min(channels.length, CONFIG.BATCH_SIZE);

  for (var c = 0; c < campaigns.length; c++) {{
    var campaign = campaigns[c];
    Logger.log("Processing campaign [" + (c + 1) + "/" + campaigns.length + "]: " + campaign.getName());
    var count = 0;

    for (var i = 0; i < limit; i++) {{
      var url = formatPlacementUrl(channels[i]);
      if (CONFIG.DRY_RUN) {{
        Logger.log("[DRY RUN] [" + campaign.getName() + "] Would exclude: " + url);
        count++;
      }} else {{
        try {{
          campaign.videoTargeting().newPlacementBuilder().withUrl(url).exclude();
          count++;
          if (count % 100 === 0) {{
            Logger.log("Excluded " + count + " / " + limit + " placements on " + campaign.getName());
          }}
        }} catch (e) {{
          Logger.log("Warning: Could not exclude " + url + " on " + campaign.getName() + ": " + e.message);
        }}
      }}
    }}

    Logger.log("Campaign " + campaign.getName() + ": processed " + count + " exclusions.");
  }}

  Logger.log("------------------------------------------------------------");
  Logger.log("Campaign exclusion complete across " + campaigns.length + " campaign(s).");
}}
"""
    return script
