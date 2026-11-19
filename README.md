# WoW Forever TSM public snapshots

A GitHub Actions job, every 5 minutes (`.github/workflows/snapshot.yml`), runs `fetch.py`,
which saves each new snapshot of TradeSkillMaster's free public pricing files
for WoW Forever (realm Normal, Alliance auction house, and the US region) to
the `data` branch, as `realm/normal-alliance/<epoch>.csv.gz` and
`region/us/<epoch>.csv.gz` (TSM's snapshot time). It keeps the last 30 days.

The Market Watch on the owner's PC (`WoWForeverTSMHistory/public.py`) pulls
these to fill the hours its own TSM app downloads missed, and its plots shade
those stretches red.

Run it by hand: Actions → TSM public snapshots → Run workflow.
Source of the data: https://tradeskillmaster.com/public-data
