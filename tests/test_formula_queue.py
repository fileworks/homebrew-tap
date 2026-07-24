from __future__ import annotations

import unittest
from collections.abc import Callable

from _support import import_scripts

import_scripts()

import bump_formula
import formula_queue


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

        def updater(formula: str, version: str) -> bump_formula.BumpOutcome:
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
