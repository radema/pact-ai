from geas_ai.core.walker import walk_source_files, load_gitignore_patterns


def test_load_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("*.log\nnode_modules/")
    spec = load_gitignore_patterns(tmp_path)

    assert spec.match_file("test.log")
    assert spec.match_file("node_modules/package.json")
    assert spec.match_file(".geas/config.yaml")  # Default ignore
    assert not spec.match_file("src/main.py")


def test_walker_basic(tmp_path):
    # Setup structure
    # src/main.py
    # src/ignored.log
    # src/.geas/
    # tests/test_main.py

    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".gitignore").write_text("*.log")

    (tmp_path / "src/main.py").touch()
    (tmp_path / "src/ignored.log").touch()
    (tmp_path / "tests/test_main.py").touch()

    # .geas is ignored by default
    (tmp_path / "src/.geas").mkdir()
    (tmp_path / "src/.geas/file").touch()

    files = walk_source_files(tmp_path, ["src", "tests"])

    assert "src/main.py" in files
    assert "tests/test_main.py" in files
    assert "src/ignored.log" not in files
    assert "src/.geas/file" not in files


def test_walker_missing_scope(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src/file.py").touch()

    # "tests" is missing, should handle gracefully (skip it)
    files = walk_source_files(tmp_path, ["src", "tests"])

    assert files == ["src/file.py"]
