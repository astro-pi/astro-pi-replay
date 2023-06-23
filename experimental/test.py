import subprocess
import sys
import io


def run_subprocess() -> tuple[str, str]:
    """
    Execute the given commands in a subprocess
    and stream the output to stdout and stderr while
    in real time while additioanlly collecting the
    output into variables for testing
    """
    with io.BytesIO() as extra_stream:
        with io.TextIOWrapper(
            extra_stream, encoding="utf-8", line_buffering=True
        ) as wrapper:
            streams = [sys.stdout, wrapper]
            # We're trying to stream output AND capture it without blocking
            with subprocess.Popen(
                ["python3", "-u", "foo.py"], stdout=subprocess.PIPE
            ) as proc:
                while True:
                    if proc.stdout is not None and proc.poll() is None:
                        byte = proc.stdout.read(1)
                        for stream in streams:
                            stream.buffer.write(byte)
                            stream.flush()
                    elif proc.stdout is not None:
                        # without an argument it reads until EOF
                        bytes = proc.stdout.read()
                        for stream in streams:
                            stream.buffer.write(bytes)
                            stream.flush()
                        break
                    else:
                        break

            print("Printing extra_stream")
            extra_stream.seek(0)
            stdout_str: str = extra_stream.read().decode()
    return stdout_str, ""


run_subprocess()
