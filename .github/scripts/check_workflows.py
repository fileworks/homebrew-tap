"""Fail when workflow expressions enter executable shell source."""

from pathlib import Path


def main() -> None:
    workflow = Path(".github/workflows/bump.yml").read_text(encoding="utf-8")
    run_blocks = workflow.split("run: |")[1:]
    forbidden = ("${{ inputs.", "${{ github.event.inputs.", "${{ needs.")
    for block in run_blocks:
        shell = block.split("\n  ", 1)[0]
        for marker in forbidden:
            if marker in shell:
                raise SystemExit(f"Unsafe workflow expression in shell source: {marker}")


if __name__ == "__main__":
    main()
