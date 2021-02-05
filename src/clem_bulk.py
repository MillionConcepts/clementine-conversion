"""
clem_bulk.py -- little support functions for clementine bulk conversion
notebooks
"""

import datetime as dt

import fs

from converter import PDSVersionConverter


def crude_time_log(
        logfile: str,
        writer: PDSVersionConverter,
        extra_time: str = ""
) -> None:
    with open(logfile, "a") as file:
        file.write(
            writer.pds4_label_file
            + ","
            + fs.path.split(writer.pds4_label_file)[1]
            + ","
            + fs.path.split(writer.filename)[1]
            + ","
            + dt.datetime.now().isoformat()
            + ","
            + extra_time
            + "\n"
        )


def swap_lat_and_scale(label_filename):
    # TODO: this is a hacky fix for a bug in gdal, or maybe an
    # incompatibility between it and a newer version of the cart LDD.
    # specifically, in polar_stereographic, the latitude_of_projection_origin
    # attribute needs to come before the scale_factor_at_projection_origin
    # attribute.
    # this hacky fix should be changed if gdal changes, although it probably
    # won't break anything.
    with open(label_filename) as file:
        label = file.read()
    lines = label.splitlines()
    lat_ix, lat_line = next(filter(
        lambda enum: 'latitude_of_projection_origin' in enum[1],
        enumerate(lines)
    ))
    scale_ix, scale_line = next(filter(
        lambda enum: 'scale_factor_at_projection_origin' in enum[1],
        enumerate(lines)
    ))
    if not scale_ix > lat_ix:
        #     continue
        pass
    lines[scale_ix] = lat_line
    lines[lat_ix] = scale_line
    with open(label_filename, 'w') as file:
        file.write("\n".join(lines))


def release_constructor(semaphore):
    """
    silly callback for sh. release semaphore when process exits.
    """

    def release_when_done(command, success, exit_code):
        semaphore.release()
        return 0

    return release_when_done


class BgViewer:
    """
    encapsulates a backgrounded sh.RunningCommand object
    to prevent its __str__ and __repr__ methods from blocking.
    useful only in REPL environments.
    """

    def __init__(self, running_command):
        self.running_command = running_command
        self.pid = self.running_command.pid

    def __repr__(self):
        if self.running_command.is_alive():
            return (
                    "running command "
                    + " ".join(
                        [byte.decode() for byte in self.running_command.cmd]
                    )
                    + " with PID "
                    + str(self.running_command.pid)
            )
        else:
            return self.running_command.__repr__()
