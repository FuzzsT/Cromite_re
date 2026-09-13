# Cromite Re automation

This repository mirrors `uazo/cromite` and keeps a small Cromite Re automation layer on top.

## What it does

- Synchronizes the current `uazo/cromite` repository every day and on manual workflow runs.
- Queries Google's official Chrome VersionHistory API for the newest Android Stable version.
- Generates `build/patches/Cromite-Re-auto-latest-UA.patch` and appends it to Cromite's patch list.
- Enables Cromite's existing mobile User-Agent override by default.
- Uses Chrome's modern reduced Android UA form, for example `Mozilla/5.0 (Linux; Android 10; K) ... Chrome/<major>.0.0.0 Mobile Safari/537.36`.
- Preserves any explicit, non-empty custom UA entered in Cromite settings.
- Builds an ARM64 APK from the matching upstream `uazo/cromite-build:<VERSION>-<UPSTREAM_SHA>` image and creates or updates a GitHub Release.

## Pixel / future Pixel behavior

Modern Chrome intentionally reduces the classic Android User-Agent. A real Pixel model belongs to high-entropy User-Agent Client Hints rather than the normal `User-Agent` header. Cromite deliberately restricts those high-entropy hints for privacy, so this automation does not fake a specific Pixel model. It follows the latest Chrome Android Stable major version while retaining Cromite's privacy behavior.

## Workflow

Workflow: `.github/workflows/cromite-re-sync-release.yml`

Scheduled runs happen daily at `03:17 UTC`. You can also run the workflow manually and choose whether to build/publish the APK.

The build uses `ubuntu-latest` by default. Chromium builds are very large. If a larger or self-hosted runner is available, define the repository variable `CROMITE_RE_RUNNER` with that runner label (for example `self-hosted` or your own label).

No Cromite signing secrets are required for the default zero-secret build path. If you later want a persistent production signing key, add a separate signing step or adapt the upstream keystore setup instead of committing a private key to the repository.

## Generated metadata

Each sync writes `build/CROMITE_RE_UA.json` containing the exact Chrome Stable version, major version, generated UA, API source and mode used for that release.
