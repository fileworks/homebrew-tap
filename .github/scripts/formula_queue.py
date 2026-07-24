"""Persist and drain formula bump requests through GitHub issues."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from bump_formula import (
    BumpError,
    BumpOutcome,
    FORMULAS,
    ReleaseVersion,
    read_formula_version,
    update_formula,
    validate_formula,
)

QUEUE_LABEL = "formula-bump"
_REPOSITORY_RE = re.compile(r"fileworks/(?P<formula>immich-export|paperless-export)")
_RUN_ID_RE = re.compile(r"[1-9]\d*")


class QueueError(RuntimeError):
    """A queue record or operation is invalid."""


@dataclass(frozen=True)
class QueueRecord:
    issue: int
    formula: str
    version: ReleaseVersion
    source_repository: str
    source_run: str
    intake_run: str

    @classmethod
    def from_payload(cls, issue: int, payload: Mapping[str, Any]) -> QueueRecord:
        expected = {
            "formula",
            "version",
            "source_repository",
            "source_run",
            "intake_run",
        }
        if set(payload) != expected:
            raise QueueError(f"Issue {issue} has an invalid queue schema")
        formula = validate_formula(str(payload["formula"]))
        source_repository = str(payload["source_repository"])
        source_match = _REPOSITORY_RE.fullmatch(source_repository)
        if source_match is None or source_match.group("formula") != formula:
            raise QueueError(f"Issue {issue} has mismatched source provenance")
        source_run = str(payload["source_run"])
        intake_run = str(payload["intake_run"])
        if _RUN_ID_RE.fullmatch(source_run) is None or _RUN_ID_RE.fullmatch(intake_run) is None:
            raise QueueError(f"Issue {issue} has an invalid run id")
        return cls(
            issue=issue,
            formula=formula,
            version=ReleaseVersion.parse(str(payload["version"])),
            source_repository=source_repository,
            source_run=source_run,
            intake_run=intake_run,
        )

    def payload(self) -> dict[str, str]:
        return {
            "formula": self.formula,
            "version": str(self.version),
            "source_repository": self.source_repository,
            "source_run": self.source_run,
            "intake_run": self.intake_run,
        }


class QueueBackend(Protocol):
    def records(self, *, state: str = "open") -> list[QueueRecord]: ...

    def create(self, record: QueueRecord) -> int: ...

    def complete(self, record: QueueRecord, outcome: BumpOutcome) -> None: ...

    def comment_failure(self, record: QueueRecord, message: str) -> None: ...


def ordered_records(records: Iterable[QueueRecord]) -> list[QueueRecord]:
    return sorted(records, key=lambda record: (record.formula, record.version, record.issue))


def persist_request(
    backend: QueueBackend,
    *,
    formula: str,
    version: str,
    source_repository: str,
    source_run: str,
    intake_run: str,
) -> int:
    candidate = QueueRecord.from_payload(
        0,
        {
            "formula": formula,
            "version": version,
            "source_repository": source_repository,
            "source_run": source_run,
            "intake_run": intake_run,
        },
    )
    for existing in backend.records(state="all"):
        if existing.intake_run == candidate.intake_run:
            if existing.payload() != candidate.payload():
                raise QueueError("The intake run id is already associated with different data")
            return existing.issue
    return backend.create(candidate)


def drain(
    backend: QueueBackend,
    *,
    updater: Callable[[str, str], BumpOutcome],
    publish: Callable[[QueueRecord, BumpOutcome], None],
    main_version: Callable[[str], ReleaseVersion],
) -> list[tuple[QueueRecord, BumpOutcome]]:
    completed: list[tuple[QueueRecord, BumpOutcome]] = []
    failures: list[str] = []
    for record in ordered_records(backend.records()):
        try:
            outcome = updater(record.formula, str(record.version))
            publish(record, outcome)
            visible = main_version(record.formula)
            if visible < record.version and outcome is not BumpOutcome.STALE:
                raise QueueError(
                    f"{record.formula} {record.version} is not present on main after publication"
                )
            backend.complete(record, outcome)
            completed.append((record, outcome))
        except Exception as exc:  # noqa: BLE001 - retain every failed record for retry
            message = str(exc).replace("\n", " ")[:500]
            backend.comment_failure(record, message)
            failures.append(f"#{record.issue}: {message}")
    if failures:
        raise QueueError("Queue drain incomplete: " + "; ".join(failures))
    return completed


def _run_json(arguments: list[str]) -> Any:
    result = subprocess.run(arguments, check=True, capture_output=True, text=True)
    return json.loads(result.stdout) if result.stdout else None


class GitHubIssueQueue:
    def __init__(self, repository: str) -> None:
        if repository != "fileworks/homebrew-tap":
            raise QueueError("Queue repository must be fileworks/homebrew-tap")
        self.repository = repository

    def records(self, *, state: str = "open") -> list[QueueRecord]:
        response = _run_json(
            [
                "gh",
                "api",
                "--method",
                "GET",
                "--paginate",
                "--slurp",
                f"repos/{self.repository}/issues",
                "-f",
                f"state={state}",
                "-f",
                f"labels={QUEUE_LABEL}",
                "-f",
                "per_page=100",
            ]
        )
        pages = response if isinstance(response, list) else []
        issues = [
            issue
            for page in pages
            if isinstance(page, list)
            for issue in page
        ]
        records: list[QueueRecord] = []
        for issue in issues:
            if not isinstance(issue, Mapping) or "pull_request" in issue:
                continue
            try:
                payload = json.loads(str(issue.get("body", "")))
            except json.JSONDecodeError as exc:
                raise QueueError(f"Issue {issue.get('number')} has invalid JSON") from exc
            if not isinstance(payload, Mapping):
                raise QueueError(f"Issue {issue.get('number')} body is not an object")
            records.append(QueueRecord.from_payload(int(issue["number"]), payload))
        return records

    def _ensure_label(self) -> None:
        subprocess.run(
            [
                "gh",
                "label",
                "create",
                QUEUE_LABEL,
                "--repo",
                self.repository,
                "--color",
                "1d76db",
                "--description",
                "Durable exporter formula bump request",
                "--force",
            ],
            check=True,
        )

    def create(self, record: QueueRecord) -> int:
        self._ensure_label()
        result = _run_json(
            [
                "gh",
                "api",
                "--method",
                "POST",
                f"repos/{self.repository}/issues",
                "-f",
                f"title=[formula-bump] {record.formula} {record.version} ({record.intake_run})",
                "-f",
                f"body={json.dumps(record.payload(), sort_keys=True, separators=(',', ':'))}",
                "-f",
                f"labels[]={QUEUE_LABEL}",
            ]
        )
        if not isinstance(result, Mapping) or not isinstance(result.get("number"), int):
            raise QueueError("GitHub did not return a queue issue number")
        return int(result["number"])

    def _comment(self, issue: int, body: str) -> None:
        subprocess.run(
            [
                "gh",
                "api",
                "--method",
                "POST",
                f"repos/{self.repository}/issues/{issue}/comments",
                "-f",
                f"body={body}",
            ],
            check=True,
        )

    def complete(self, record: QueueRecord, outcome: BumpOutcome) -> None:
        self._comment(
            record.issue,
            f"Verified `{record.formula}` `{record.version}` on `main` ({outcome.value}).",
        )
        subprocess.run(
            [
                "gh",
                "api",
                "--method",
                "PATCH",
                f"repos/{self.repository}/issues/{record.issue}",
                "-f",
                "state=closed",
                "-f",
                "state_reason=completed",
            ],
            check=True,
        )

    def comment_failure(self, record: QueueRecord, message: str) -> None:
        self._comment(record.issue, f"Drain attempt failed; record remains open: `{message}`")


def _publish(record: QueueRecord, outcome: BumpOutcome) -> None:
    if outcome is not BumpOutcome.UPDATED:
        return
    subprocess.run(["git", "add", str(FORMULAS[record.formula])], check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"chore: bump {record.formula} to {record.version}",
        ],
        check=True,
    )
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
    subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)


def _main_version(formula: str) -> ReleaseVersion:
    return read_formula_version(FORMULAS[formula], formula)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    intake = subparsers.add_parser("intake")
    intake.add_argument("--formula", required=True)
    intake.add_argument("--version", required=True)
    intake.add_argument("--source-repository", required=True)
    intake.add_argument("--source-run", required=True)
    intake.add_argument("--intake-run", required=True)
    subparsers.add_parser("drain")
    args = parser.parse_args(argv)
    backend = GitHubIssueQueue(args.repository)
    try:
        if args.command == "intake":
            issue = persist_request(
                backend,
                formula=args.formula,
                version=args.version,
                source_repository=args.source_repository,
                source_run=args.source_run,
                intake_run=args.intake_run,
            )
            print(issue)
        else:
            drained = drain(
                backend,
                updater=update_formula,
                publish=_publish,
                main_version=_main_version,
            )
            for record, outcome in drained:
                print(f"#{record.issue} {record.formula} {record.version}: {outcome.value}")
    except (BumpError, QueueError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
