import json
import sys
from datetime import datetime, timezone
from pathlib import Path


class ValidationError(Exception):
    pass


default_hook = sys.excepthook


def exception_handler(exception_type, exception, traceback):
    if exception_type is ValidationError:
        print(f"{exception_type.__name__}: {exception}")
    else:
        default_hook(exception_type, exception, traceback)


sys.excepthook = exception_handler


def is_valid_submission(filename: str) -> bool:
    """
    Validates that the given filename, which should point to a result.json adheres
    file is a valid submission for Mission Space Lab 23-24.
    In the case of an error, the function raises a ValidationError immediately.
    Otherwise, if the given file is valid, returns True.

    filename - A string to a result.json file
    """
    if Path(filename).name != "result.json":
        raise ValidationError(
            f"Your file should be called result.json but is {filename}."
        )
    try:
        with open(filename) as f:
            results = json.loads(f.read())
    except json.JSONDecodeError:
        raise ValidationError(
            "Your file could not be parsed as JSON. Did you save it using json.dumps?"
        )

    for field in ["estimate_kmps", "estimate_start", "estimate_end"]:
        if field not in results:
            raise ValidationError(f"Couldn't find field '{field}' in your file.")

    try:
        float(results["estimate_kmps"])
    except ValueError:
        raise ValidationError("'estimate_kmps' should be parsable as a number (float)")
    sigfigs = len(str(results["estimate_kmps"]).replace(".", ""))
    if sigfigs > 5:
        raise ValidationError(
            "'estimate_kmps' should be no more than 5 significant "
            + f"figures but has {sigfigs}."
        )

    before = None
    datefields = ["estimate_start", "estimate_end"]
    for field in datefields:
        try:
            as_datetime = datetime.fromisoformat(results[field])
            if before is None:
                before = as_datetime
        except ValueError:
            raise ValidationError(
                f"Couldn't read '{field}' as a date. "
                + "Did you save it using datetime.isoformat()?"
            )
        if as_datetime.tzinfo is None:
            raise ValidationError(
                f"'{field}' must be in UTC timezone. "
                + "Did you set tzinfo=datetime.timezone.utc?"
            )
        elif as_datetime.tzinfo != timezone.utc:
            raise ValidationError(
                f"'{field}' must be in UTC timezone but "
                + f"is {str(as_datetime.tzinfo)}."
            )

        if before is not None and before > as_datetime:
            raise ValidationError(
                f"Cannot have '{datefields[0]}' after '{datefields[1]}'. Did you "
                + "write them the wrong way around?"
            )
    return True
