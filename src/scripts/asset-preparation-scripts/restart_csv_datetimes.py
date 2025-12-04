from datetime import datetime, datetime_CAPI, timedelta
from pathlib import Path
from typing import Optional
import argparse
import logging


DEFAULT_HEADER_LINES_LEN: int = 1
DEFAULT_DELIMITER: str = ","
DATETIME_COL: str = "datetime"
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"

def resequence(
    csv_file: Path, 
    delimiter: str,
    header_lines_len: int,
    start: datetime
) -> None:
    logging.debug(f"Resequencing {csv_file} from {start.isoformat()}")
    logging.debug(f"header_lines_len: {header_lines_len}")

    with csv_file.open() as f:
        lines = f.read().strip().splitlines()
    
    # if we specify there are 2 header lines,
    # then we want at least 3 lines
    if not len(lines) >= header_lines_len + 1:
        raise RuntimeError(
                f"Not enough lines in {csv_file} for it " +
                f"to have {header_lines_len} header lines")

    headers = lines[:header_lines_len]
    found_col: Optional[int] = None
    for header_line in headers:
        for i, col_name in enumerate(header_line.split(delimiter)):
            if col_name == DATETIME_COL:
                if found_col:
                    raise RuntimeError(
                            f"Multiple {DATETIME_COL} header columns found")
                else:
                    found_col = i
    if found_col is None:
        raise RuntimeError(
                f"Could not find {DATETIME_COL} column in the headers"
        )
    else:

        # print the headers
        for header in headers:
            print(header)

        # 2022-05-06 16:46:48.000000
        actual_start: Optional[datetime] = None
        for line in lines[header_lines_len:]:
            line_elements: list[str] = line.split(delimiter)
            line_datetime: datetime = datetime.strptime(
                    line_elements[found_col],
                    DATETIME_FORMAT)

            delta: timedelta
            if actual_start is None:
                actual_start = line_datetime
                delta = timedelta(seconds=0)
            else:
                delta = line_datetime - actual_start


            new_datetime: datetime = start + delta

            # overwrite
            line_elements[found_col] = new_datetime.strftime(
                    DATETIME_FORMAT)

            print(delimiter.join(line_elements))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            prog=Path(__file__).stem,
            description="Re-sequences the datetimes in the given " + \
            "csv to start from the given start time, and prints " + \
            "the new file to stdout."
    )
    parser.add_argument(
            "csv_file", type=Path,
           help="The Path to the csv file to re-sequence."
    )
    parser.add_argument(
            "start", type=str,
           help="The start datetime to use in ISO format."
    )
    parser.add_argument(
            "--headers", type=int, default=DEFAULT_HEADER_LINES_LEN,
            help="How many lines that include headers. " +
            f"Defaults to {DEFAULT_HEADER_LINES_LEN}."
    )
    parser.add_argument(
            "--delimiter", type=str, default=DEFAULT_DELIMITER,
            help="The delimiter to use. Defaults to a comma"
    )

    args = parser.parse_args()

    start: datetime = datetime.fromisoformat(args.start)

    resequence(
            args.csv_file, args.delimiter, 
            args.headers, start)
