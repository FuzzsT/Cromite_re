#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

VERSION_HISTORY_ENDPOINTS = (
    "https://versionhistory.googleapis.com/v1/chrome/platforms/android/channels/stable/versions",
    "https://versionhistory.googleapis.com/v1/chrome/platforms/android/channels/stable/versions/all/releases",
)
PATCH_NAME = "Cromite-Re-auto-latest-UA.patch"
DEFAULT_DEVICE = "Pixel 11 Pro XL"
DEFAULT_ANDROID = "17"


def version_key(value: str) -> tuple[int, int, int, int]:
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", value):
        raise ValueError(f"Unexpected Chrome version: {value!r}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def _extract_versions(payload: dict) -> list[str]:
    values: list[str] = []
    for key in ("versions", "releases"):
        for item in payload.get(key, []):
            value = str(item.get("version", ""))
            try:
                version_key(value)
            except ValueError:
                continue
            values.append(value)
    return values


def fetch_latest_android_stable() -> tuple[str, str]:
    errors: list[str] = []
    for endpoint in VERSION_HISTORY_ENDPOINTS:
        for attempt in range(3):
            try:
                query = urllib.parse.urlencode({"page_size": 200, "order_by": "version desc"})
                url = f"{endpoint}?{query}"
                request = urllib.request.Request(
                    url,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "Cromite-Re-UA-Updater/2.0",
                    },
                )
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = json.load(response)
                candidates = _extract_versions(payload)
                if candidates:
                    return max(candidates, key=version_key), url
                errors.append(f"{endpoint}: no valid versions")
            except Exception as exc:  # noqa: BLE001 - emit useful CI diagnostics
                errors.append(f"{endpoint} attempt {attempt + 1}: {exc}")
                time.sleep(1 + attempt)
    raise RuntimeError("Unable to resolve latest Chrome Android Stable: " + "; ".join(errors))


def build_reduced_android_ua(chrome_version: str) -> str:
    major = version_key(chrome_version)[0]
    return (
        "Mozilla/5.0 (Linux; Android 10; K) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{major}.0.0.0 Mobile Safari/537.36"
    )


def build_pixel_compat_ua(chrome_version: str, android_version: str, device: str) -> str:
    return (
        f"Mozilla/5.0 (Linux; Android {android_version}; {device}) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_version} Mobile Safari/537.36"
    )


def cpp_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_patch(ua: str) -> str:
    escaped = cpp_string(ua)
    return f"""From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001
From: Cromite Re Bot <cromite-re-bot@users.noreply.github.com>
Date: Thu, 1 Jan 1970 00:00:00 +0000
Subject: [PATCH] Cromite Re: default to latest Chrome Android UA

Keep Cromite's existing User-Agent customization UI, but make the mobile
override enabled by default and seed it with the latest generated Chrome
Android User-Agent.

If an older profile still contains an empty mobile override, migrate it to
the generated value. Explicit non-empty custom User-Agent values remain
untouched.
---
 chrome/browser/android/preferences/browser_prefs_android.cc | 4 ++--
 chrome/browser/android/preferences/privacy_preferences_manager_impl.cc | 6 +++++-
 2 files changed, 7 insertions(+), 3 deletions(-)

diff --git a/chrome/browser/android/preferences/browser_prefs_android.cc b/chrome/browser/android/preferences/browser_prefs_android.cc
--- a/chrome/browser/android/preferences/browser_prefs_android.cc
+++ b/chrome/browser/android/preferences/browser_prefs_android.cc
@@ -20,8 +20,8 @@ void RegisterPrefs(PrefRegistrySimple* registry) {{
   RegisterClipboardAndroidPrefs(registry);
   readaloud::RegisterLocalPrefs(registry);
   webauthn::authenticator::RegisterLocalState(registry);
 
-  registry->RegisterBooleanPref(prefs::kOverrideUserAgentEnabled, false);
-  registry->RegisterStringPref(prefs::kOverrideUserAgent, "");
+  registry->RegisterBooleanPref(prefs::kOverrideUserAgentEnabled, true);
+  registry->RegisterStringPref(prefs::kOverrideUserAgent, "{escaped}");
   registry->RegisterBooleanPref(prefs::kOverrideUserAgentDesktopModeEnabled, false);
   registry->RegisterStringPref(prefs::kOverrideUserAgentDesktopMode, "");
   registry->RegisterBooleanPref(prefs::kDesktopModeViewportMetaEnabled, false);
diff --git a/chrome/browser/android/preferences/privacy_preferences_manager_impl.cc b/chrome/browser/android/preferences/privacy_preferences_manager_impl.cc
--- a/chrome/browser/android/preferences/privacy_preferences_manager_impl.cc
+++ b/chrome/browser/android/preferences/privacy_preferences_manager_impl.cc
@@ -61,7 +61,11 @@ static void UpdateOverrideUserAgent() {{
   std::string ua = g_browser_process->local_state()->GetString(prefs::kOverrideUserAgent);
   if (ua.empty()) {{
-    ua = ChromeContentBrowserClient().GetUserAgent();
+    ua = "{escaped}";
+    g_browser_process->local_state()->SetString(prefs::kOverrideUserAgent, ua);
+    g_browser_process->local_state()->SetBoolean(prefs::kOverrideUserAgentEnabled, true);
+    overrideUserAgentEnabled = true;
   }}
 
   base::CommandLine* parsed_command_line = base::CommandLine::ForCurrentProcess();
--
2.43.0
"""


def update_patch_list(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if line.strip() != PATCH_NAME]
    lines.append(PATCH_NAME)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Path to the Cromite patch repository")
    parser.add_argument(
        "--profile",
        choices=("pixel", "reduced"),
        default="pixel",
        help="pixel = Pixel compatibility UA; reduced = modern Chrome reduced UA",
    )
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--android", default=DEFAULT_ANDROID)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    patch_list = repo / "build" / "cromite_patches_list.txt"
    patch_dir = repo / "build" / "patches"

    if not patch_list.is_file() or not patch_dir.is_dir():
        raise SystemExit(f"{repo} does not look like a Cromite patch repository")

    chrome_version, source_url = fetch_latest_android_stable()
    chrome_major = str(version_key(chrome_version)[0])

    if args.profile == "pixel":
        ua = build_pixel_compat_ua(chrome_version, args.android, args.device)
        mode = "pixel-compat-full"
    else:
        ua = build_reduced_android_ua(chrome_version)
        mode = "reduced-android-mobile"

    (patch_dir / PATCH_NAME).write_text(render_patch(ua), encoding="utf-8")
    update_patch_list(patch_list)

    metadata = {
        "chrome_stable": chrome_version,
        "chrome_major": chrome_major,
        "user_agent": ua,
        "source": source_url,
        "mode": mode,
        "device": args.device if args.profile == "pixel" else None,
        "android": args.android if args.profile == "pixel" else None,
    }
    (repo / "build" / "CROMITE_RE_UA.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Chrome Android Stable: {chrome_version}")
    print(f"UA mode: {mode}")
    print(f"Generated UA: {ua}")
    print(f"Patch: build/patches/{PATCH_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
