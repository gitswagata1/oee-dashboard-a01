"""Validation tests for the optional production CSV upload."""

from io import StringIO

import pytest

from upload_data import load_uploaded_data, uploaded_metadata


HEADER = (
    "date,shift,machine,mtype,hour,planned,run,ideal,aloss,"
    "ploss,qloss,total,ok,valid"
)
ROW = "2026-05-01,A,CNC-1,CN,9,60,50,45,10,5,0,100,98,1"


def parse(text: str):
    return load_uploaded_data(StringIO(text))


def test_valid_upload_and_metadata():
    data = parse(HEADER + "\n" + ROW + "\n" +
                 "2026-05-03,B,CNC-2,CN,15,60,40,35,20,5,0,80,75,0\n")
    assert len(data) == 2
    assert str(data["date"].dtype).startswith("datetime64")
    meta = uploaded_metadata(data)
    assert meta["period_start"] == "2026-05-01"
    assert meta["period_end"] == "2026-05-03"
    assert meta["period_days"] == 3
    assert meta["connected"] == 2
    assert meta["n_raw"] == 2
    assert meta["n_kept_valid"] == 1


def test_missing_required_columns():
    with pytest.raises(ValueError, match="Missing required columns:.*shift"):
        parse(HEADER.replace("shift,", "") + "\n" + ROW.replace(",A,", ","))


def test_empty_file():
    with pytest.raises(ValueError, match="no data rows"):
        parse(HEADER + "\n")


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("date", "not-a-date", "invalid dates"),
        ("planned", "broken", "invalid numbers"),
        ("run", "-5", "negative numbers"),
        ("valid", "2", "only 0 or 1"),
        ("hour", "25", "between 0 and 23"),
        ("ok", "101", "cannot exceed"),
    ],
)
def test_invalid_column_values(column, value, message):
    cells = dict(zip(HEADER.split(","), ROW.split(",")))
    cells[column] = value
    with pytest.raises(ValueError, match=message):
        parse(HEADER + "\n" + ",".join(cells.values()) + "\n")


def test_no_valid_rows():
    with pytest.raises(ValueError, match="no rows marked valid"):
        parse(HEADER + "\n" + ROW.rsplit(",", 1)[0] + ",0\n")


def test_whitespace_column_headers():
    data = parse(HEADER.replace("machine", " machine ") + "\n" + ROW + "\n")
    assert data["machine"].iloc[0] == "CNC-1"

def test_valid_production_row_cannot_have_zero_planned():
    cells = dict(zip(HEADER.split(","), ROW.split(",")))
    cells["planned"] = "0"
    with pytest.raises(ValueError, match="planned time greater than zero"):
        parse(HEADER + "\n" + ",".join(cells.values()) + "\n")


def test_resets_file_before_read():
    source = StringIO(HEADER + "\n" + ROW + "\n")
    source.read()
    assert len(load_uploaded_data(source)) == 1
