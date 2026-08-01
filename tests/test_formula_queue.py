from __future__ import annotations

import json
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock

from _support import import_scripts

import_scripts()

import bump_formula
import formula_queue

LOCK_SHA256 = "a" * 64


def lock_url(formula: str) -> str:
    return (
        f"https://raw.githubusercontent.com/fileworks/{formula}/"
        f"{'b' * 40}/uv.lock"
    )


class FakeQueue:
    def __init__(self, records: list[formula_queue.QueueRecord] | None = None) -> None:
        self.open = list(records or [])
        self.all = list(self.open)
        self.completed: list[tuple[int, bump_formula.BumpOutcome]] = []
        self.failures: list[int] = []

    def records(self, *, state: str = "open") -> list[formula_queue.QueueRecord]:
        return list(self.all if state == "all" else self.open)

    def create(self, record: formula_queue.QueueRecord) -> int:
        created = formula_queue.QueueRecord(
            issue=len(self.all) + 1,
            formula=record.formula,
            version=record.version,
            source_repository=record.source_repository,
            source_run=record.source_run,
            lock_url=record.lock_url,
            lock_sha256=record.lock_sha256,
            intake_run=record.intake_run,
        )
        self.open.append(created)
        self.all.append(created)
        return created.issue

    def complete(
        self,
        record: formula_queue.QueueRecord,
        outcome: bump_formula.BumpOutcome,
    ) -> None:
        self.completed.append((record.issue, outcome))
        self.open = [item for item in self.open if item.issue != record.issue]

    def comment_failure(self, record: formula_queue.QueueRecord, _message: str) -> None:
        self.failures.append(record.issue)


def record(issue: int, formula: str, version: str, run: str) -> formula_queue.QueueRecord:
    return formula_queue.QueueRecord.from_payload(
        issue,
        {
            "formula": formula,
            "version": version,
            "source_repository": f"fileworks/{formula}",
            "source_run": run,
            "lock_url": lock_url(formula),
            "lock_sha256": LOCK_SHA256,
            "intake_run": str(1000 + issue),
        },
    )


class QueueTests(unittest.TestCase):
    def test_intake_is_idempotent_and_rejects_changed_replay(self) -> None:
        backend = FakeQueue()
        arguments = {
            "formula": "immich-export",
            "version": "1.2.3",
            "source_repository": "fileworks/immich-export",
            "source_run": "88",
            "lock_url": lock_url("immich-export"),
            "lock_sha256": LOCK_SHA256,
            "intake_run": "99",
        }
        first = formula_queue.persist_request(backend, **arguments)
        second = formula_queue.persist_request(backend, **arguments)
        self.assertEqual(first, second)
        with self.assertRaises(formula_queue.QueueError):
            formula_queue.persist_request(backend, **{**arguments, "version": "1.2.4"})

    def test_out_of_order_and_two_formula_requests_are_sorted(self) -> None:
        records = [
            record(1, "paperless-export", "2.0.0", "11"),
            record(2, "immich-export", "1.10.0", "12"),
            record(3, "immich-export", "1.2.0", "13"),
        ]
        ordered = formula_queue.ordered_records(records)
        self.assertEqual(
            [(item.formula, str(item.version)) for item in ordered],
            [
                ("immich-export", "1.2.0"),
                ("immich-export", "1.10.0"),
                ("paperless-export", "2.0.0"),
            ],
        )

    def test_replacement_of_pending_drain_loses_no_persisted_records(self) -> None:
        backend = FakeQueue(
            [
                record(1, "immich-export", "1.2.0", "11"),
                record(2, "paperless-export", "2.0.0", "12"),
                record(3, "immich-export", "1.3.0", "13"),
            ]
        )
        state = {
            "immich-export": bump_formula.ReleaseVersion.parse("1.0.0"),
            "paperless-export": bump_formula.ReleaseVersion.parse("1.0.0"),
        }

        def updater(
            formula: str,
            version: str,
            _lock_url: str,
            _lock_sha256: str,
        ) -> bump_formula.BumpOutcome:
            requested = bump_formula.ReleaseVersion.parse(version)
            outcome = (
                bump_formula.BumpOutcome.EQUAL
                if requested == state[formula]
                else bump_formula.BumpOutcome.UPDATED
            )
            state[formula] = max(state[formula], requested)
            return outcome

        formula_queue.drain(
            backend,
            updater=updater,
            publish=lambda *_args: None,
            main_version=state.__getitem__,
        )
        self.assertFalse(backend.open)
        self.assertEqual(state["immich-export"], bump_formula.ReleaseVersion.parse("1.3.0"))
        self.assertEqual(state["paperless-export"], bump_formula.ReleaseVersion.parse("2.0.0"))

    def test_failure_before_publication_remains_retryable(self) -> None:
        queued = record(1, "immich-export", "1.2.0", "11")
        backend = FakeQueue([queued])
        with self.assertRaises(formula_queue.QueueError):
            formula_queue.drain(
                backend,
                updater=lambda *_args: bump_formula.BumpOutcome.UPDATED,
                publish=lambda *_args: (_ for _ in ()).throw(RuntimeError("push failed")),
                main_version=lambda _formula: bump_formula.ReleaseVersion.parse("1.0.0"),
            )
        self.assertEqual([item.issue for item in backend.open], [1])
        self.assertEqual(backend.failures, [1])

    def test_record_closes_only_after_result_is_on_main(self) -> None:
        backend = FakeQueue([record(1, "immich-export", "1.2.0", "11")])
        with self.assertRaises(formula_queue.QueueError):
            formula_queue.drain(
                backend,
                updater=lambda *_args: bump_formula.BumpOutcome.UPDATED,
                publish=lambda *_args: None,
                main_version=lambda _formula: bump_formula.ReleaseVersion.parse("1.1.0"),
            )
        self.assertFalse(backend.completed)

    def test_equal_replay_completes_without_publish(self) -> None:
        backend = FakeQueue([record(1, "immich-export", "1.2.0", "11")])
        published = False

        def publish(*_args: object) -> None:
            nonlocal published
            published = True

        formula_queue.drain(
            backend,
            updater=lambda *_args: bump_formula.BumpOutcome.EQUAL,
            publish=publish,
            main_version=lambda _formula: bump_formula.ReleaseVersion.parse("1.2.0"),
        )
        self.assertTrue(published)
        self.assertEqual(backend.completed, [(1, bump_formula.BumpOutcome.EQUAL)])


if __name__ == "__main__":
    unittest.main()


class BootstrapTests(unittest.TestCase):
    """An unpublished formula must be reported, never invented or retried."""

    def test_missing_formula_reports_bootstrap_instead_of_failing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "unpacksort.rb"
            with mock.patch.dict(
                bump_formula.FORMULAS,
                {**bump_formula.FORMULAS, "unpacksort": missing},
                clear=True,
            ):
                outcome = bump_formula.update_formula(
                    "unpacksort",
                    "1.0.0",
                    lock_url=lock_url("unpacksort"),
                    lock_sha256=LOCK_SHA256,
                    sdist_fetcher=lambda *_args: self.fail("PyPI must not be consulted"),
                )
        self.assertIs(outcome, bump_formula.BumpOutcome.BOOTSTRAP_REQUIRED)

    def test_bootstrap_request_completes_without_blocking_later_formulas(self) -> None:
        backend = FakeQueue(
            [
                record(1, "unpacksort", "1.0.0", "11"),
                record(2, "immich-export", "1.3.0", "12"),
            ]
        )
        published: list[str] = []

        def updater(
            formula: str,
            _version: str,
            _lock_url: str,
            _lock_sha256: str,
        ) -> bump_formula.BumpOutcome:
            if formula == "unpacksort":
                return bump_formula.BumpOutcome.BOOTSTRAP_REQUIRED
            return bump_formula.BumpOutcome.UPDATED

        def publish(item: formula_queue.QueueRecord, _outcome: object) -> None:
            published.append(item.formula)

        completed = formula_queue.drain(
            backend,
            updater=updater,
            publish=publish,
            main_version=lambda _formula: bump_formula.ReleaseVersion.parse("1.3.0"),
        )

        self.assertEqual(
            [(item.formula, outcome.value) for item, outcome in completed],
            [("immich-export", "updated"), ("unpacksort", "bootstrap_required")],
        )
        self.assertEqual(published, ["immich-export"])
        self.assertEqual(backend.failures, [])
        self.assertEqual(backend.open, [])

    def test_unpacksort_release_provenance_is_accepted(self) -> None:
        item = record(7, "unpacksort", "1.0.0", "42")
        self.assertEqual(item.formula, "unpacksort")
        with self.assertRaises(formula_queue.QueueError):
            formula_queue.QueueRecord.from_payload(
                8,
                {
                    "formula": "unpacksort",
                    "version": "1.0.0",
                    "source_repository": "fileworks/immich-export",
                    "source_run": "42",
                    "lock_url": lock_url("unpacksort"),
                    "lock_sha256": LOCK_SHA256,
                    "intake_run": "1008",
                },
            )


class HistoricalSchemaTests(unittest.TestCase):
    """The queue outlives its own schema, so it must read its own history."""

    def _issues(self, state: str) -> list[list[dict[str, object]]]:
        # Issue 9 is real: a closed bump from before lock_url/lock_sha256 existed.
        historical = {
            "number": 9,
            "state": "closed",
            "body": json.dumps(
                {
                    "formula": "paperless-export",
                    "intake_run": "30197512308",
                    "source_repository": "fileworks/paperless-export",
                    "source_run": "30195659182",
                    "version": "1.0.0",
                }
            ),
        }
        current = {
            "number": 10,
            "state": "open",
            "body": json.dumps(
                {
                    "formula": "immich-export",
                    "version": "0.1.0",
                    "source_repository": "fileworks/immich-export",
                    "source_run": "1",
                    "lock_url": lock_url("immich-export"),
                    "lock_sha256": LOCK_SHA256,
                    "intake_run": "2",
                }
            ),
        }
        if state == "open":
            return [[current]]
        return [[historical, current]]

    def test_a_closed_entry_from_an_older_schema_is_skipped(self) -> None:
        backend = formula_queue.GitHubIssueQueue("fileworks/homebrew-tap")
        with mock.patch.object(
            formula_queue, "_run_json", lambda _argv: self._issues("all")
        ):
            records = backend.records(state="all")

        # Skipped, not fatal: reading it was what broke every bump after 1.0.0.
        self.assertEqual([record.issue for record in records], [10])

    def test_an_open_entry_that_cannot_be_parsed_still_raises(self) -> None:
        # Pending work nobody can process must not be silently dropped.
        broken = [[{"number": 11, "state": "open", "body": json.dumps({"formula": "x"})}]]
        backend = formula_queue.GitHubIssueQueue("fileworks/homebrew-tap")
        with mock.patch.object(formula_queue, "_run_json", lambda _argv: broken):
            with self.assertRaises(formula_queue.QueueError):
                backend.records(state="all")


class SupersededRequestTests(unittest.TestCase):
    """A request that can never succeed must not block the queue forever."""

    def _drain(self, main: str, requested: str, later: bool = True):
        records = [record(1, "immich-export", requested, "11")]
        if later:
            records.append(record(2, "paperless-export", "2.0.0", "12"))
        backend = FakeQueue(records)
        published: list[str] = []

        def updater(formula: str, *_args: str) -> bump_formula.BumpOutcome:
            if formula == "immich-export":
                raise bump_formula.BumpError(
                    "uv.lock project version does not match the requested release"
                )
            return bump_formula.BumpOutcome.UPDATED

        def main_version(formula: str) -> bump_formula.ReleaseVersion:
            return bump_formula.ReleaseVersion.parse(
                main if formula == "immich-export" else "2.0.0"
            )

        completed = formula_queue.drain(
            backend,
            updater=updater,
            publish=lambda item, _outcome: published.append(item.formula),
            main_version=main_version,
        )
        return completed, published

    def test_a_permanently_impossible_request_is_closed_as_stale(self) -> None:
        # The real case: immich-export 0.1.0 could never bump, because the tagged
        # uv.lock said 0.0.4 and a tag is immutable. main had moved to 0.1.1.
        completed, published = self._drain(main="0.1.1", requested="0.1.0")

        outcomes = {item.formula: outcome.value for item, outcome in completed}
        self.assertEqual(outcomes["immich-export"], "stale")
        # And it no longer blocks the formula queued behind it.
        self.assertEqual(outcomes["paperless-export"], "updated")
        self.assertEqual(published, ["paperless-export"])

    def test_a_failure_that_is_not_superseded_still_blocks_and_retries(self) -> None:
        # Main is behind the request, so this is a real failure to fix, not
        # history to discard. Losing it would silently drop a pending release.
        with self.assertRaises(formula_queue.QueueError):
            self._drain(main="0.0.4", requested="0.1.0", later=False)
