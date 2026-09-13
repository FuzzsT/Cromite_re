# Cromite Re automation

This repository mirrors `uazo/cromite` and keeps a small Cromite Re automation layer on top.

## What it does

- Synchronizes the current `uazo/cromite` `master` branch every day and on manual workflow runs.
- Queries Google's official Chrome VersionHistory API for the newest Android Stable version.
- Generates `build/patches/Cromite-Re-auto-latest-UA.patch` and appends it to Cromite's patch list.
- Enables Cromite's existing mobile User-Agent override by default.
- Defaults to a Pixel compatibility profile using Android 17 / Pixel 11 Pro XL and the exact latest Chrome Android Stable version.
- Also supports Chrome's modern reduced Android UA profile from manual workflow dispatch.
- Preserves any explicit, non-empty custom UA entered in Cromite settings.
- Builds an ARM64 APK from the matching upstream `uazo/cromite-build:<VERSION>-<UPSTREAM_SHA>` image and creates or updates a GitHub Release.

## Pixel profile

The default generated compatibility UA has the form:

`Mozilla/5.0 (Linux; Android 17; Pixel 11 Pro XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/<latest-stable-version> Mobile Safari/537.36`

Modern Chromium also uses User-Agent Client Hints. The classic `User-Agent` override does not force every high-entropy Client Hint, so sites that rely only on `Sec-CH-UA-Model` can still see Cromite's own privacy behavior.

## Workflow

Workflow: `.github/workflows/cromite-re-sync-release.yml`

Scheduled runs happen daily at `03:17 UTC`. The workflow also runs after changes to the automation files on `main`, which gives an immediate validation/sync run after updates. Manual runs can select either the `pixel` or `reduced` UA profile and choose whether to publish the APK.

The workflow preserves its own automation files while mirroring upstream source. Upstream GitHub workflows are intentionally not copied into this repository, preventing unrelated upstream CI jobs from being triggered here.

## Generated metadata

Each sync writes `build/CROMITE_RE_UA.json` containing the exact Chrome Stable version, major version, generated UA, API source, UA mode, Android profile and device profile used for that release.
