"""Package only deliverables, excluding local environments, caches and test builds."""
import argparse
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Package Source/ and an existing Report.pdf")
    parser.add_argument("--ids", nargs="+", required=True, help="Actual student IDs in submission order")
    parser.add_argument("--report", type=Path, required=True, help="Final PDF, including the Drive demo URL")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    options = parser.parse_args(argv)
    if not all(re.fullmatch(r"[A-Za-z0-9-]+", identifier) for identifier in options.ids):
        parser.error("Student IDs may contain only letters, digits and hyphens")
    if len(set(options.ids)) != len(options.ids):
        parser.error("Student IDs must be distinct")
    if not options.report.is_file() or options.report.suffix.lower() != ".pdf":
        parser.error("Provide the completed PDF report")
    with options.report.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            parser.error("The report does not have a PDF header")
    name = "_".join(options.ids)
    options.output.mkdir(parents=True, exist_ok=True)
    archive = options.output / f"{name}.zip"
    if archive.exists():
        parser.error(f"Archive already exists; use a new output directory: {archive}")
    files = [ROOT / filename for filename in ("main.py", "README.md", "requirements.txt",
                                              "pyproject.toml", "NOTICE.md")]
    for folder in ("src/proofledger", "tests", "docs", "tools", "examples"):
        files.extend(path for path in (ROOT / folder).rglob("*") if path.is_file()
                     and "__pycache__" not in path.parts and path.suffix != ".pyc")
    files.extend(path for path in (ROOT / "output").rglob("*") if path.is_file()
                 and path.suffix in {".csv", ".json", ".md"})
    with ZipFile(archive, "x", compression=ZIP_DEFLATED) as package:
        for path in sorted(set(files)):
            package.write(path, f"{name}/Source/{path.relative_to(ROOT).as_posix()}")
        package.write(options.report, f"{name}/Report.pdf")
    print(f"Created {archive} ({archive.stat().st_size / 1_000_000:.2f} MB)")
    print("Check the Drive video's public-link access in an incognito window before submission.")
    if archive.stat().st_size > 20_000_000:
        print("Archive exceeds 20 MB: the assignment requires sharing it through Google Drive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
