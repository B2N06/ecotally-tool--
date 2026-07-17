"""PyInstaller entry point for the EcoTally desktop application."""

import sys


def _self_test() -> int:
    """Exercise the packaged analysis path without opening a window."""
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from ecotally.cli import analyze
    from ecotally.desktop import analysis_options

    with TemporaryDirectory(prefix="ecotally-self-test-") as directory:
        source = Path(directory) / "observations.csv"
        source.write_text(
            "site,species,abundance\n"
            "forest,oak,3\n"
            "forest,birch,1\n"
            "meadow,grass,4\n"
            "meadow,clover,2\n",
            encoding="utf-8",
        )
        report = analyze(source)
    sites = report.get("sites", [])
    if len(sites) != 2:
        raise RuntimeError("Packaged analysis self-test returned unexpected results")
    options = analysis_options(
        sampling=False,
        uncertainty=False,
        hill_profile=False,
        traits_path=None,
    )
    if options["bootstrap"] != 0:
        raise RuntimeError("Packaged desktop option mapping is unavailable")
    return 0


def _main() -> int:
    if "--self-test" in sys.argv[1:]:
        return _self_test()

    from ecotally.desktop import main

    main()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
