"""Blockchain module tests do not touch the scientific model."""

import hashlib
import json

import pytest

from scripts.artifact_receipt import main
from src.blockchain.commitments import DOMAIN, SCHEMA, commitment, make_receipt, verify_receipt


def test_known_digest_and_exact_bytes(tmp_path):
    artifact = tmp_path / "binary.dat"
    artifact.write_bytes(b"\x00\xff\n")
    digest, size = commitment(artifact)
    assert digest == "0x" + hashlib.sha256(DOMAIN + b"\x00\xff\n").hexdigest()
    assert size == 3
    receipt = make_receipt(artifact)
    assert receipt == {
        "schema": SCHEMA, "algorithm": "sha256", "digest": digest, "size_bytes": 3
    }
    assert verify_receipt(artifact, receipt)
    assert "binary.dat" not in json.dumps(receipt)


def test_empty_and_tampered_artifact(tmp_path):
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"")
    receipt = make_receipt(artifact)
    assert verify_receipt(artifact, receipt)
    artifact.write_bytes(b"altered")
    assert not verify_receipt(artifact, receipt)


def test_rejects_invalid_receipts(tmp_path):
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"data")
    valid = make_receipt(artifact)
    invalid = [
        {**valid, "size_bytes": True},
        {**valid, "size_bytes": -1},
        {**valid, "digest": "0x1234"},
        {**valid, "digest": valid["digest"].upper()},
        {**valid, "algorithm": "keccak256"},
        {**valid, "schema": "v2"},
        {**valid, "path": "/private/data"},
        [],
    ]
    for receipt in invalid:
        with pytest.raises(ValueError):
            verify_receipt(artifact, receipt)
    assert not verify_receipt(artifact, {**valid, "digest": "0x" + "0" * 64})


def test_reject_directory(tmp_path):
    with pytest.raises(ValueError, match="not a regular file"):
        commitment(tmp_path)


def test_cli_round_trip_and_no_overwrite(tmp_path, capsys):
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"some result")
    receipt = tmp_path / "sub" / "receipt.json"
    options = ["--artifact", str(artifact), "--receipt", str(receipt)]
    assert main(["create", *options]) == 0
    assert main(["verify", *options]) == 0
    with pytest.raises(SystemExit) as duplicate:
        main(["create", *options])
    assert duplicate.value.code == 2
    artifact.write_bytes(b"changed")
    assert main(["verify", *options]) == 1
    assert "INVALID" in capsys.readouterr().out


def test_cli_refuses_same_path(tmp_path):
    artifact = tmp_path / "file"
    artifact.write_bytes(b"data")
    with pytest.raises(SystemExit) as result:
        main(["create", "--artifact", str(artifact), "--receipt", str(artifact)])
    assert result.value.code == 2
    assert artifact.read_bytes() == b"data"
