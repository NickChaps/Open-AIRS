# SPDX-License-Identifier: Apache-2.0
"""Command-line interface for validation, assessment and drift review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .engine import assess, assess_inventory, diff_assessments, pack_impact
from .errors import AirFrameworkError
from .io import dump_json, load_json
from .judge import (
    client_from_environment,
    qualify_with_llm,
    write_qualification_bundle,
)
from .profiles import assess_profile, load_profile_packs
from .routing import apply_routes
from .validation import (
    validate_assessment_note,
    validate_extraction_record,
    validate_inventory,
    validate_pack,
    validate_pack_profile,
    validate_review_record,
    validate_route_profile,
)


def _write(value: Any, output: str | None, compact: bool) -> None:
    rendered = dump_json(value, pretty=not compact)
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="air-framework",
        description="Evaluate governed objects against auditable rule packs.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate_inventory_parser = commands.add_parser(
        "validate-inventory", help="Validate an inventory snapshot"
    )
    validate_inventory_parser.add_argument("inventory")

    validate_pack_parser = commands.add_parser("validate-pack", help="Validate a rule pack")
    validate_pack_parser.add_argument("pack")

    validate_extraction_parser = commands.add_parser(
        "validate-extraction", help="Validate an extraction and analysis record"
    )
    validate_extraction_parser.add_argument("extraction")

    validate_review_parser = commands.add_parser(
        "validate-review", help="Validate a human review record"
    )
    validate_review_parser.add_argument("review")

    validate_note_parser = commands.add_parser(
        "validate-note", help="Validate a readable assessment note"
    )
    validate_note_parser.add_argument("note")

    assess_parser = commands.add_parser("assess", help="Assess one object with one pack")
    assess_parser.add_argument("--inventory", required=True)
    assess_parser.add_argument("--pack", required=True)
    assess_parser.add_argument("--target", required=True)
    assess_parser.add_argument("--output")
    assess_parser.add_argument("--assessed-at")
    assess_parser.add_argument("--include-not-matched", action="store_true")
    assess_parser.add_argument("--compact", action="store_true")

    assess_all_parser = commands.add_parser(
        "assess-all", help="Assess every compatible object in an inventory"
    )
    assess_all_parser.add_argument("--inventory", required=True)
    assess_all_parser.add_argument("--pack", required=True)
    assess_all_parser.add_argument("--output")
    assess_all_parser.add_argument("--assessed-at")
    assess_all_parser.add_argument("--include-not-matched", action="store_true")
    assess_all_parser.add_argument("--compact", action="store_true")

    diff_parser = commands.add_parser("diff", help="Compare two assessment records")
    diff_parser.add_argument("before")
    diff_parser.add_argument("after")
    diff_parser.add_argument("--output")
    diff_parser.add_argument("--compact", action="store_true")

    impact_parser = commands.add_parser(
        "impact", help="Dry-run a candidate pack against an inventory"
    )
    impact_parser.add_argument("--inventory", required=True)
    impact_parser.add_argument("--before-pack", required=True)
    impact_parser.add_argument("--after-pack", required=True)
    impact_parser.add_argument("--assessed-at")
    impact_parser.add_argument("--output")
    impact_parser.add_argument("--compact", action="store_true")

    route_parser = commands.add_parser(
        "route", help="Apply an organisation-owned route profile to assessment records"
    )
    route_parser.add_argument("--profile", required=True)
    route_parser.add_argument("--assessment", required=True, action="append")
    route_parser.add_argument("--output")
    route_parser.add_argument("--compact", action="store_true")

    validate_routes_parser = commands.add_parser(
        "validate-routes", help="Validate an organisation route profile"
    )
    validate_routes_parser.add_argument("profile")

    assess_profile_parser = commands.add_parser(
        "assess-profile", help="Assess one object with a version-pinned pack profile"
    )
    assess_profile_parser.add_argument("--inventory", required=True)
    assess_profile_parser.add_argument("--profile", required=True)
    assess_profile_parser.add_argument("--target", required=True)
    assess_profile_parser.add_argument("--assessed-at")
    assess_profile_parser.add_argument("--output")
    assess_profile_parser.add_argument("--compact", action="store_true")

    validate_profile_parser = commands.add_parser(
        "validate-profile", help="Validate a pack-selection profile and all pins"
    )
    validate_profile_parser.add_argument("profile")

    qualify_parser = commands.add_parser(
        "qualify",
        help="Run LLM fact extraction, deterministic packs and a readable LLM note",
    )
    qualify_parser.add_argument("--inventory", required=True)
    qualify_parser.add_argument("--profile", required=True)
    qualify_parser.add_argument("--target", required=True)
    qualify_parser.add_argument("--output-dir", required=True)
    qualify_parser.add_argument("--language", default="fr")
    qualify_parser.add_argument("--model")
    qualify_parser.add_argument("--base-url")
    qualify_parser.add_argument("--provider-name", default="openai-compatible")
    qualify_parser.add_argument("--api-key-env", default="AIR_LLM_API_KEY")
    qualify_parser.add_argument(
        "--response-format",
        choices=["json_schema", "json_object"],
        default="json_schema",
    )
    qualify_parser.add_argument("--reasoning-effort")
    qualify_parser.add_argument("--max-tokens", type=int, default=5000)
    qualify_parser.add_argument("--timeout", type=float, default=120.0)
    qualify_parser.add_argument("--assessed-at")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-inventory":
            validate_inventory(load_json(args.inventory))
            print(f"valid inventory: {args.inventory}")
        elif args.command == "validate-pack":
            validate_pack(load_json(args.pack))
            print(f"valid pack: {args.pack}")
        elif args.command == "validate-extraction":
            validate_extraction_record(load_json(args.extraction))
            print(f"valid extraction record: {args.extraction}")
        elif args.command == "validate-review":
            validate_review_record(load_json(args.review))
            print(f"valid review record: {args.review}")
        elif args.command == "validate-note":
            validate_assessment_note(load_json(args.note))
            print(f"valid assessment note: {args.note}")
        elif args.command == "assess":
            result = assess(
                load_json(args.inventory),
                load_json(args.pack),
                args.target,
                assessed_at=args.assessed_at,
                include_not_matched=args.include_not_matched,
            )
            _write(result, args.output, args.compact)
        elif args.command == "assess-all":
            result = assess_inventory(
                load_json(args.inventory),
                load_json(args.pack),
                assessed_at=args.assessed_at,
                include_not_matched=args.include_not_matched,
            )
            _write(result, args.output, args.compact)
        elif args.command == "diff":
            result = diff_assessments(load_json(args.before), load_json(args.after))
            _write(result, args.output, args.compact)
        elif args.command == "impact":
            result = pack_impact(
                load_json(args.inventory),
                load_json(args.before_pack),
                load_json(args.after_pack),
                assessed_at=args.assessed_at,
            )
            _write(result, args.output, args.compact)
        elif args.command == "route":
            result = apply_routes(
                [load_json(path) for path in args.assessment], load_json(args.profile)
            )
            _write(result, args.output, args.compact)
        elif args.command == "validate-routes":
            validate_route_profile(load_json(args.profile))
            print(f"valid route profile: {args.profile}")
        elif args.command == "assess-profile":
            profile, packs = load_profile_packs(args.profile)
            result = assess_profile(
                load_json(args.inventory),
                profile,
                packs,
                args.target,
                assessed_at=args.assessed_at,
            )
            _write(result, args.output, args.compact)
        elif args.command == "validate-profile":
            profile, _ = load_profile_packs(args.profile)
            validate_pack_profile(profile)
            print(f"valid pack profile: {args.profile}")
        elif args.command == "qualify":
            profile, packs = load_profile_packs(args.profile)
            client = client_from_environment(
                model=args.model,
                base_url=args.base_url,
                api_key_env=args.api_key_env,
                provider_name=args.provider_name,
                response_format=args.response_format,
                reasoning_effort=args.reasoning_effort,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
            )
            bundle = qualify_with_llm(
                load_json(args.inventory),
                profile,
                packs,
                args.target,
                client,
                language=args.language,
                assessed_at=args.assessed_at,
            )
            write_qualification_bundle(bundle, args.output_dir)
            print(f"qualification bundle: {Path(args.output_dir).resolve()}")
        return 0
    except AirFrameworkError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
