# Preparing a new image sequence

## Deciding on a sequence

The hardest step is deciding on an appropriate sequence.
Usually this is a collaborative process within the Astro Pi team.

## Preparing the chosen sequence

Providing that a sequence has been chosen, there are a number
of steps that must be done in order for it to be usable by the
replay tool.

To assist with each step, there are a number of useful scripts in the [../src/scripts/asset-preparation-scripts/]() directory.

The steps needed to process the chosen image sequence are:

 - Upsampling photos (if desired) - ensuring that any size-related metadata in the Exif tags are also updated.
 - Renaming image files (to start from 0 and be zero-padded).
 - The images must be indexed into a `photo_index.csv` CSV file. This file file may contain additional columns, but must contain a single header line of `datetime,name` and the first and second columns of each line must be in the order below:
   - `datetime` The date the photo was taken.
   - `name` The name of the photo in the `photos` dir
 - The nearest [TLE file](https://en.wikipedia.org/wiki/Two-line_element_set) for the ISS must be provided and placed in the `data` dir. This is usually found by querying the [https://www.space-track.org]() website. An example query (pre-url-encoding) is:

    ```txt
    https://www.space-track.org/basicspacedata/query/class/tle/NORAD_CAT_ID/25544/EPOCH/>2023-05-03,<2023-05-04/orderby/EPOCH asc/limit/5/format/tle/emptyresult/show
    ```
    This query fetches the first 5 two line element lines in the range 2023-05-03 to 2023-05-04.
 - Missing `sense hat` data must be collated - perhaps by renaming the sense hat data collected by the original submission - or by other means. The sense hat file format is explained [./data_csv_schema.md](here).
 - The `sense hat` data may need to be changed to match the timestamps of the images.
 - The `metadata.json` file must be generated. The schema for this is accessible at [../src/astro_pi_replay/resources/metadata_schema.json]().
 - A variable-framerate `mp4` video of the images must be created, using the original `datetime_digitized` times as the basis for each frame.
 This is most easily done on a Linux machine (or Docker container) with `ffmpeg`, which includes a `-ts_from_file` option. First, the access times of each image file need to be modified (using `touch -d`) to reflect the value of `datetime_digitized`, and then the following command can be executed:

    ```bash
    ffmpeg -f image2 \
       -ts_from_file 2 \
       -i 'image_%03d.jpg' \
       -filter:v ffps=25 \
       video.mp4
    ```
 - The following tags must be removed from each image:
   * `gps_latitude`
   * `gps_latitude_ref`
   * `gps_longitude`
   * `gps_longitude_ref`
   * `gps_altitude`
   * `gps_altitude_ref`


## Deploying

The images are deployed using the [`../src/scripts/upload_assets.py`]() script. This script validates the `metadata.json` file, that no `exif` GPS tags are included, and a few other things before uploading the assets to the deployment bucket. To use it to upload a given `<SEQUENCE_ID>`, execute the commands below from the base `astro-pi-replay` directory (the directory containing the `pyproject.toml` file):

```bash
cd src
python3 -m scripts.upload_assets --upload-videos \
  --sequence-ids <SEQUENCE_ID>
```

This should upload things to the destination bucket, providing you can be authenticated (you may need to set, e.g. `AWS_PROFILE`).
