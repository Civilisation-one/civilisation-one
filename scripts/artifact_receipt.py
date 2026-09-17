"""Create or verify off-chain receipts; never broadcasts transactions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.blockchain.commitments import load_receipt, make_receipt, verify_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify"):
        subparser = subcommands.add_parser(command)
        subparser.add_argument("--artifact", type=Path, required=True)
        subparser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "create":
            if args.artifact.resolve() == args.receipt.resolve():
                raise ValueError("Receipt cannot overwrite the artifact")
            receipt = make_receipt(args.artifact)
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            with args.receipt.open("x", encoding="utf-8") as output:
                json.dump(receipt, output, sort_keys=True, indent=2)
                output.write("\n")
            print(f"Created receipt: {args.receipt} (digest {receipt['digest']})")
            return 0
        verified = verify_receipt(args.artifact, load_receipt(args.receipt))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print("VALID: artifact matches receipt" if verified else "INVALID: artifact differs from receipt")
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
