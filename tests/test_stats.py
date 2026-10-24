import json

import pytest

from csv_insight.cli import main
from csv_insight.stats import summarise_column, summarise_csv

SAMPLE = """name,age,city
Amina,30,Nairobi
Brian,25,Mombasa
Chloe,,Nairobi
Dan,41,Nairobi
"""


def test_numeric_column():
    s = summarise_column("age", ["30", "25", "", "41"])
    assert s.kind == "numeric"
    assert (s.count, s.missing) == (3, 1)
    assert (s.minimum, s.maximum, s.median) == (25, 41, 30)
    assert s.mean == pytest.approx(32.0)


def test_text_column_reports_top_values():
    s = summarise_column("city", ["Nairobi", "Mombasa", "Nairobi"], top=1)
    assert s.kind == "text"
    assert s.top_values == [("Nairobi", 2)]
    assert s.unique == 2


def test_mixed_column_is_text():
    assert summarise_column("x", ["1", "two", "3"]).kind == "text"


def test_all_missing_column_is_text():
    s = summarise_column("x", ["", " "])
    assert (s.kind, s.count, s.missing) == ("text", 0, 2)


def test_short_rows_count_as_missing():
    summaries = summarise_csv(["a,b", "1,2", "3"])
    assert summaries[1].missing == 1


def test_empty_input_raises():
    with pytest.raises(ValueError):
        summarise_csv([])


def test_cli_text_output(tmp_path, capsys):
    path = tmp_path / "people.csv"
    path.write_text(SAMPLE, encoding="utf-8")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "age (numeric)" in out
    assert "Nairobi (3)" in out


def test_cli_json_output(tmp_path, capsys):
    path = tmp_path / "people.csv"
    path.write_text(SAMPLE, encoding="utf-8")
    assert main([str(path), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert [c["name"] for c in data] == ["name", "age", "city"]


def test_cli_missing_file(capsys):
    assert main(["does-not-exist.csv"]) == 1
    assert "error" in capsys.readouterr().err
