# Google Ads JavaScript Generator

The Google Ads scripting community (practitioners following Nils Rooijmans, Mike Rhodes, Smarter Ecommerce, and the r/PPC community) relies on copy-paste JavaScript snippets that run directly within the Google Ads interface.

Rather than requiring manual CSV uploads into Google Ads Editor, **TubeSentry** can generate a self-contained, copy-paste JavaScript file that automates placement exclusions directly inside your Google Ads account.

---

## 1. Generating the Script via CLI

During an audit, pass `--export-script`:

```bash
tubesentry audit where_ads_showed.csv --export-script cleanup_placements.js
```

Or export from a report with custom settings:

```bash
tubesentry export script \
  --report where_ads_showed.csv \
  --out cleanup_placements.js \
  --list-name "TubeSentry Waste Shield" \
  --dry-run
```

---

## 2. Generated JavaScript Structure

The generated script is self-contained and formatted for modern Google Ads Scripts (V8 runtime):

```javascript
var CONFIG = {
  // Test mode: true = preview in logs without making actual exclusions; false = apply changes
  DRY_RUN: true,

  // Exclusion mode: 'SHARED_LIST' (recommended account-wide) or 'CAMPAIGNS'
  EXCLUSION_MODE: 'SHARED_LIST',

  // Name of the account-level Shared Placement Exclusion List
  SHARED_LIST_NAME: 'TubeSentry Waste Shield',

  // Filter campaigns by name when using 'CAMPAIGNS' mode
  CAMPAIGN_NAME_CONTAINS: '',

  // Max exclusions to process per run (Google Ads script limit is 30 minutes)
  BATCH_SIZE: 1000
};

var CHANNELS_TO_EXCLUDE = [
  "UCbCmjCuTUZos6Inko4u57UQ",
  "UCSJ4gkVC6NrvII8umztf0Ow"
  // ... all flagged channel IDs
];

function main() {
  // Automatically creates or populates the Shared Placement Exclusion List
}
```

---

## 3. How to Deploy in Google Ads

1. In your Google Ads dashboard, navigate to **Tools and Settings > Bulk Actions > Scripts**.
2. Click the blue **+** button to create a new script.
3. Paste the contents of `cleanup_placements.js`.
4. Click **Preview** to verify the execution logs in safe dry-run mode.
5. In `CONFIG`, set `DRY_RUN: false`, authorize the script, and click **Run**.
6. (Optional) Set a daily or weekly schedule to keep your account shielded automatically.

---

## 4. Shared List vs. Campaign Mode

* **`SHARED_LIST` Mode (Recommended):** Creates or appends to an account-level **Excluded Placement List** in the Shared Library. Applying this list to all campaigns blocks flagged channels across Video, Performance Max, and Demand Gen without hitting individual campaign limits.
* **`CAMPAIGNS` Mode:** Targets specific campaigns matching `--campaign-name-contains`.
