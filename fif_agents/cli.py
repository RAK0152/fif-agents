"""Local catalog and configuration diagnostics; launches remain standard ADK CLI."""

import argparse
import os

from .catalog import CASES
from .config import configure, project


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list", "doctor"])
    args = parser.parse_args()
    if args.command == "list":
        for number, case in enumerate(CASES, 1):
            print(f"{number:02d}  {case.slug:30s} {case.title}")
        return
    configure()
    errors = []
    try:
        print(f"GCP project: {project()}")
    except ValueError as exc:
        errors.append(str(exc))
    mode = os.getenv("FIF_AUTH_MODE", "vertex")
    print(f"Model mode: {mode}; model: {os.getenv('FIF_MODEL', 'gemini-2.5-flash')}")
    if mode == "api_key" and not os.getenv("GOOGLE_API_KEY"):
        errors.append("Set GOOGLE_API_KEY for api_key mode")
    try:
        import google.auth
        credentials, adc_project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        print(f"ADC discovered: {type(credentials).__name__}; default project: {adc_project}")
    except Exception as exc:
        errors.append(f"ADC unavailable: {exc}")
    for error in errors:
        print(f"ERROR: {error}")
    print("Doctor checks local configuration only; it does not validate API access, billing, or model availability.")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
