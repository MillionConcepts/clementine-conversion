"""
specialized utilities and PDSVersionConverter / PDS4Writer 
subclasses for converting clementine products

depends on a working install of DOSBOX in the user's $PATH
+ access to CLEMDCMP.EXE

doesn't work on Windows for a wide variety of reasons
"""

import datetime as dt
import os
import shutil
import xml.etree.ElementTree as et
from functools import partial
from operator import attrgetter
from typing import Dict, Optional

import numpy as np
import pandas as pd
import sh
from osgeo import gdal
from pandas.core.groupby import DataFrameGroupBy
from toolz import merge, pipe

from converter import PDSVersionConverter, PDS4Writer, get_element_block, \
    round_xml_tag, constrain_xml_tag
from converter_utils import fitsify, get_from_and_apply, eqloc

# context-product constants. designed to make it easy to update things
# if someone publishes a new version of the Moon.

TARGET_TAG_MAPPING = {
    'MOON': {
        '{target_name}': 'MOON',
        '{target_lidvid}': 'urn:nasa:pds:context:target:satellite.earth.moon'
                           '::1.1',
        '{target_type}': 'Satellite'
    },
    'EARTH': {
        '{target_name}': 'EARTH',
        '{target_lidvid}': 'urn:nasa:pds:context:target:planet.earth::1.3',
        '{target_type}': 'Planet'
    },
    'SKY': {
        '{target_name}': 'SKY',
        '{target_lidvid}': 'urn:nasa:pds:context:target:calibration_field'
                           '.sky::1.0',
        '{target_type}': 'Calibration'
    },
    'UNK': {
        '{target_name}': 'UNKNOWN',
        '{target_lidvid}': 'urn:nasa:pds:context:target:calibrator.unk::1.0',
        '{target_type}': 'Calibrator'
    }
}

INSTRUMENT_TAG_MAPPING = {
    'HIRES': {
        "{instrument_long_name}": "Lidar High-Resolution Imager or "
                                  "High-Resolution Imaging Camera (HIRES)",
        "{instrument_lidvid}": "urn:nasa:pds:context:instrument:hires.clem1"
                               "::1.0",
        "{instrument_context_name}": "LIDAR HIGH-RESOLUTION IMAGER",
        "{instrument_wavelength}": "Near Infrared"
    },
    'LWIR': {
        "{instrument_long_name}": "Long Wavelength (or Longwave) Infrared "
                                  "Camera (LWIR)",
        "{instrument_lidvid}": "urn:nasa:pds:context:instrument:lwir.clem1"
                               "::1.0",
        "{instrument_context_name}": "LONG WAVELENGTH INFRARED CAMERA",
        "{instrument_wavelength}": "Far Infrared"
    },
    'NIR': {
        "{instrument_long_name}": "Near Infared Camera (NIR)",
        "{instrument_lidvid}": "urn:nasa:pds:context:instrument:nir.clem1"
                               "::1.0",
        "{instrument_context_name}": "NEAR INFRARED CAMERA",
        "{instrument_wavelength}": "Near Infrared"
    },
    'UVVIS': {
        "{instrument_long_name}": "Ultraviolet/Visible Camera (UVVIS)",
        "{instrument_lidvid}": "urn:nasa:pds:context:instrument:uvvis.clem1"
                               "::1.0",
        "{instrument_context_name}": "ULTRAVIOLET/VISIBLE CAMERA",
        # note that instrument_wavelength is ignored for this instrument in
        # many products in order to specify the particular science facets
        # relevant to the filters being used
        "{instrument_wavelength}": "Visible"
    },
    'A-STAR': {
        "{instrument_long_name}": "Star Tracker Camera A",
        "{instrument_lidvid}": "urn:nasa:pds:context:instrument:a-star.clem1"
                               "::1.0",
        "{instrument_context_name}": "A STAR TRACKER CAMERA",
        "{instrument_wavelength}": "Visible"
    },
    'B-STAR': {
        "{instrument_long_name}": "Star Tracker Camera B",
        "{instrument_lidvid}": "urn:nasa:pds:context:instrument:b-star.clem1"
                               "::1.0",
        "{instrument_context_name}": "B STAR TRACKER CAMERA",
        "{instrument_wavelength}": "Visible"
    }
}

# canonical mappings to our mosaic categories and subcategories
# from original file / product name prefixes
# note that this creates ambiguity with the handful of basemap
# illumination geometry products, so don't naively use the mosaic
# converter on them without a bit of hacking
MOSAIC_PREFIX_MAPPING = {
    'h': 'hires',
    'b': 'basemap',
    'g': 'hires_polar',
    'n': 'nir',
    'u': 'uvvis',
    'p': 'uvvis_phase'
}

# utilities

# cartographic utilities

# 'constants

# cardinal directions
CARDINALS = ('north', 'south', 'east', 'west')

# gdal.TranslateOptions dictionary for mosaic products
MOSAIC_GDAL_OPTION_DICT = {
    'format': 'PDS4',
    'creationOptions': [
        'IMAGE_FORMAT=GEOTIFF',
    ],
}


def fetch_pds4_bounds(label):
    bounds = {
        cardinal: pipe(
            et.fromstring(label).iter(),
            partial(filter, lambda element: cardinal in element.tag),
            next,
            attrgetter('text'),
            float
        )
        for cardinal in CARDINALS
    }
    return bounds


def format_edr_time(datetime: dt.datetime) -> str:
    """
    arbitrary time formatting function. microseconds must be retained
    to differentiate between files in some series.
    """
    return str(datetime.year) \
        + format(datetime.month, "0>2d") \
        + format(datetime.day, "0>2d") \
        + "t" \
        + format(datetime.hour, "0>2d") \
        + format(datetime.minute, "0>2d") \
        + format(datetime.second, "0>2d") \
        + format(datetime.microsecond / 1000000, "0>3.3f")[2:]


def dosbox_batch(directory, command, drive_letter="d"):
    """
    executes dosbox, mounts a directory to D:, switches to D:,
    and runs a command in that directory
    """
    return sh.dosbox(
        "-c",
        "mount " + drive_letter + " " + directory,
        "-c",
        drive_letter + ":",
        "-c",
        command,
    )


def clemdcmp(
        files,
        clemdcmp_directory,
        output_directory,
        instance_ix=0
):
    """
    decompress clementine files using CLEMDCMP.EXE

    file paths must be relative to clemdcmp_directory,
    and in DOS format. note that it will NOT write out
    filenames longer than {8}.{3}, so we just write them out
    to the clemdcmp directory as enumerated .IMG files and then
    move them elsewhere.

    WARNING: Make sure to crank up processor cycles in dosbox config
    before running this! You don't want to do this at authentic
    1997 speeds.

    TODO, maybe: add some kind of timeout to this. CLEMDCMP.EXE hangs
    forever, rather than crashing, when confronted with most
    forms of bad input.


    """
    # compose batch command -- dosbox does not support
    # FOR or START, so we have to do these recursion steps
    # in python

    # the temp .IMG files are a necessary dodge to deal with
    # the 8-letter name + 3-letter extension max length issue in DOS
    # -- alternatively we could write them to a temp directory
    # but that is not clearly better / less confusing
    command_list = [
        "clemdcmp -i " + file + " " + str(ix) + "_" + str(instance_ix) + ".IMG"
        for ix, file in enumerate(files)
    ]
    command_list.append("exit")
    # write batch command to disk
    with open(clemdcmp_directory + "procs" + str(instance_ix) + ".bat",
              "w") as file:
        for command in command_list:
            file.write(command + "\n")

    # run the batch command
    dosbox_batch(clemdcmp_directory,
                 "procs" + str(instance_ix) + ".bat")

    # move the temp files to output_directory with their original names
    moves = []
    for ix, file in enumerate(files):
        moves.append(sh.mv(
            clemdcmp_directory + str(ix) + "_" + str(instance_ix) + ".IMG",
            output_directory + file + ".img",
        ))
    return command_list


# it's challenging to trick gdal_translate into not writing to disk, and the
# skeleton in-memory Dataset objects gdal.Translate returns are usually not
# useful, so we just scratch to disk. (will make a tempfs if this needs to
# be faster)

"""
the conversion functions for the map-projected clementine
products use gdal for two purposes:
1. to convert the rasters to GeoTIFF
2. to compute PDS4 attributes related to the map projection
"""


def clementine_mosaic_time_tags(
        tile_name: str,
        source_groups: DataFrameGroupBy
) -> Dict[str, str]:
    """
    generate start / stop times for a basemap tile, referencing a
    pandas groupby object or similar made from one of the source index products
    """
    try:
        tile_sources = next(filter(
            lambda x: x[0].strip() == tile_name.upper(),
            source_groups
        ))[1]
        source_times = pd.to_datetime(tile_sources['start_time'])
    except StopIteration:
        print(
            "note: this product has no defined source start and stop times. "
            "using defaults.")
        return {
            '{start_time}': '1994-01-25T00:00:00Z',
            '{stop_time}': '1994-05-07T00:00:00Z'
        }
    return {
        '{start_time}': source_times.min().isoformat()[:-9] + 'Z',
        '{stop_time}': source_times.max().isoformat()[:-9] + 'Z'
    }


def clementine_mosaic_tags(label):
    """
    get values for "simple" tags found in all clementine mosaic products. (
    not all
    of these values are _used_ in all products.)
    """
    get_pds3 = get_from_and_apply(label)

    generic_dictionary = {}

    # note that target distance has units and solar doesn't
    generic_dimensionless_attrs = [
        # note that, unlike in the EDR PSD3 labels,
        # bandwidth and center wavelength are not
        # encoded as PVL values with units, just regular strings
        "bandwidth",
        "center_filter_wavelength",
        "edr_software_name",
        "filter_name",
        "frame_sequence_number",
        "gain_mode_id",
        "light_source_name",
        "mcp_gain_mode_id",
        "mission_phase_name",
        "offset_mode_id",
        "original_product_id",
        "producer_institution_name",
        "product_id",
        "revolution_number",
        "sequence_table_id",
        "spacecraft_solar_distance",
    ]

    for attr in generic_dimensionless_attrs:
        generic_dictionary["{" + attr + "}"] = get_pds3(attr.upper())

    supplemental_generic_items = {
        "{modification_date}": dt.datetime.now().isoformat()[:-16],
        "{product_creation_time}": get_pds3(
            "PRODUCT_CREATION_TIME",
            func=dt.datetime.isoformat
        ) + "Z",
    }

    return merge(generic_dictionary, supplemental_generic_items)


def clementine_edr_tags(label):
    """
    get values for "simple" tags found in all clementine EDR products. (not all
    of these values are _used_ in all products.)
    """
    get_pds3 = get_from_and_apply(label)

    generic_dictionary = {}

    generic_value_attrs = [
        "bandwidth",
        "center_dec",
        "center_filter_wavelength",
        "center_latitude",
        "center_longitude",
        "center_ra",
        "cryocooler_temperature",
        "cryocooler_duration",
        "declination",
        "emission_angle",
        "exposure_duration",
        "focal_plane_temperature",
        "horizontal_pixel_scale",
        "incidence_angle",
        "lens_temperature",
        "light_source_distance",
        "light_source_incidence_angle",
        "light_source_phase_angle",
        "local_hour_angle",
        "north_azimuth",
        "phase_angle",
        "right_ascension",
        "slant_distance",
        "smear_azimuth",
        "smear_magnitude",
        "sub_light_source_azimuth",
        "sub_light_source_latitude",
        "sub_light_source_longitude",
        "sub_solar_azimuth",
        "sub_solar_latitude",
        "sub_solar_longitude",
        "sub_spacecraft_azimuth",
        "sub_spacecraft_latitude",
        "sub_spacecraft_longitude",
        "target_center_distance",
        "twist_angle",
        "vertical_pixel_scale",
    ]

    # note that target distance has units and solar doesn't
    generic_dimensionless_attrs = [
        "edr_software_name",
        "filter_name",
        "frame_sequence_number",
        "gain_mode_id",
        "light_source_name",
        "mcp_gain_mode_id",
        "mission_phase_name",
        "offset_mode_id",
        "original_product_id",
        "producer_institution_name",
        "product_id",
        "revolution_number",
        "sequence_table_id",
        "spacecraft_solar_distance",
    ]

    generic_image_attrs = [
        "lines",
        "line_samples",
    ]

    for attr in generic_value_attrs:
        generic_dictionary["{" + attr + "}"] = get_pds3(attr.upper(), "value")
    for attr in generic_dimensionless_attrs:
        generic_dictionary["{" + attr + "}"] = get_pds3(attr.upper())
    for attr in generic_image_attrs:
        generic_dictionary["{" + attr + "}"] = get_pds3("IMAGE", attr.upper())

    # clean up items with "UNK" temperatures and such (all assigned
    # to non-nillable attributes in various namespaces)
    for attr in ["cryocooler_temperature", "focal_plane_temperature",
                 "lens_temperature", "cryocooler_duration"]:
        if generic_dictionary["{" + attr + "}"] == "None":
            generic_dictionary["{delete:" + attr + "}"] = True
    if (
            ("{delete:cryocooler_temperature}" in generic_dictionary)
            and ("{delete:focal_plane_temperature}" in generic_dictionary)
            and ("{delete:lens_temperature}" in generic_dictionary)
    ):
        generic_dictionary["{delete:device_temperatures}"] = True

    # clean up items with unknown sequence table id
    # (string-type attribute, retain as explicitly unknown) 
    if generic_dictionary["{sequence_table_id}"] == "":
        generic_dictionary["{sequence_table_id}"] = "UNKNOWN"

    # clean up items with unknown filters
    # (these are assigned to non-nillable attributes in the img namespace)
    for attr in ["bandwidth", "center_filter_wavelength"]:
        if generic_dictionary["{" + attr + "}"] == "None":
            generic_dictionary["{delete:filter_values}"] = True

    supplemental_generic_items = {
        "{modification_date}": dt.datetime.now().isoformat()[:-16],
        "{product_creation_time}": get_pds3(
            "PRODUCT_CREATION_TIME",
            func=dt.datetime.isoformat
        ) + "Z",
        "{start_time}": get_pds3(
            "START_TIME",
            func=dt.datetime.isoformat
        )[:-9] + "Z",
        "{uncorrected_start_time}": get_pds3(
            "UNCORRECTED_START_TIME",
            func=dt.datetime.isoformat
        )[:-9] + "Z"
    }

    return merge(generic_dictionary, supplemental_generic_items)


def clementine_edr_target_tags(label):
    """
    map target names to context product names / lidvid references
    """
    get_pds3 = get_from_and_apply(label)
    target_name = get_pds3('TARGET_NAME')
    target_dictionary = TARGET_TAG_MAPPING[target_name]
    target_based_deletions = {}
    if target_name == 'SKY':
        target_based_deletions['{delete:planetodetic}'] = True
    if target_name == "UNK":
        target_based_deletions['{delete:unknown_target}'] = True
    return merge(target_dictionary, target_based_deletions)


def clementine_edr_compression_tags(product_id, image_index):
    """
    CLEMDCMP.EXE does not retain information about the formerly-compressed file
    in its output label; we reference a table to do so.
    """
    try:
        line = eqloc(image_index, 'product_id', product_id)
        assert len(line) == 1
        line = line.iloc[0]

    except (AttributeError, AssertionError):
        print(
            "Warning: can't find file in the table or multiple entries exist "
            "in the table. Using placeholder values for Onboard_Compression. "
            "You should probably check this. "
        )
        return {
            "encoding_type_original": "None",
            "encoding_compression_ratio_original": "9999",
        }
    compression_dictionary = {}
    encoding_type = line.encoding_type
    if "JPEG" in encoding_type:
        compression_dictionary["{encoding_type_original}"] = "JPEG"
        compression_dictionary["{clem_jpeg_version}"] = encoding_type.strip()
    else:
        compression_dictionary["{encoding_type_original}"] = "None"
        compression_dictionary["{clem_jpeg_version}"] = "None"
    compression_dictionary[
        "{encoding_compression_ratio_original}"
    ] = line.encoding_compression_ratio

    return compression_dictionary


def clementine_edr_vector_tags(label):
    """
    compose tags related to position and velocity vectors in label --
    basically just flattening lists and flipping the sign of one of the vectors
    """
    sc_target_position_vector = label["SC_TARGET_POSITION_VECTOR"]
    sc_sun_position_vector = label["SC_SUN_POSITION_VECTOR"]
    sc_target_velocity_vector = label["SC_TARGET_VELOCITY_VECTOR"]
    sc_sun_velocity_vector = label["SC_SUN_VELOCITY_VECTOR"]
    return {
        "{sc_sun_position_vector_0_neg}": str(sc_sun_position_vector[0] * -1),
        "{sc_sun_position_vector_1_neg}": str(sc_sun_position_vector[1] * -1),
        "{sc_sun_position_vector_2_neg}": str(sc_sun_position_vector[2] * -1),
        "{sc_sun_velocity_vector_0}": str(sc_sun_velocity_vector[0]),
        "{sc_sun_velocity_vector_1}": str(sc_sun_velocity_vector[1]),
        "{sc_sun_velocity_vector_2}": str(sc_sun_velocity_vector[2]),
        "{sc_target_position_vector_0}": str(sc_target_position_vector[0]),
        "{sc_target_position_vector_1}": str(sc_target_position_vector[1]),
        "{sc_target_position_vector_2}": str(sc_target_position_vector[2]),
        "{sc_target_velocity_vector_0}": str(sc_target_velocity_vector[0]),
        "{sc_target_velocity_vector_1}": str(sc_target_velocity_vector[1]),
        "{sc_target_velocity_vector_2}": str(sc_target_velocity_vector[2]),
    }


def clementine_edr_footprint_tags(label):
    """
    compose tags related to celestial and planetodetic footprints of image --
    basically just rearranging lists

    note that the errata on cl_0088 state that, although the edrsis
    specifies that the vertex order is: upper left, upper right, lower left,
    lower right; the vertex order is actually upper left, upper right,
    lower right, lower left.

    we have followed the order given in the errata.
    """
    latlon_vertices = np.vstack(
        [label["RETICLE_POINT_LATITUDE"], label["RETICLE_POINT_LONGITUDE"]]
    )
    radec_vertices = np.vstack(
        [label["RETICLE_POINT_RA"], label["RETICLE_POINT_DECLINATION"]]
    )
    footprint_dict = {
        "{reticle_0_0}": str(latlon_vertices[0][0]),
        "{reticle_0_1}": str(latlon_vertices[0][1]),
        "{reticle_0_2}": str(latlon_vertices[0][2]),
        "{reticle_0_3}": str(latlon_vertices[0][3]),
        "{reticle_1_0}": str(latlon_vertices[1][0]),
        "{reticle_1_1}": str(latlon_vertices[1][1]),
        "{reticle_1_2}": str(latlon_vertices[1][2]),
        "{reticle_1_3}": str(latlon_vertices[1][3]),
        "{reticle_radec_0_0}": str(radec_vertices[0][0]),
        "{reticle_radec_0_1}": str(radec_vertices[0][1]),
        "{reticle_radec_0_2}": str(radec_vertices[0][2]),
        "{reticle_radec_0_3}": str(radec_vertices[0][3]),
        "{reticle_radec_1_0}": str(radec_vertices[1][0]),
        "{reticle_radec_1_1}": str(radec_vertices[1][1]),
        "{reticle_radec_1_2}": str(radec_vertices[1][2]),
        "{reticle_radec_1_3}": str(radec_vertices[1][3]),
    }
    if "N/A" in list(latlon_vertices.flatten()):
        footprint_dict["{delete:footprint_vertices}"] = True
    return footprint_dict


def clementine_edr_instrument_tags(label):
    """
    just look up formatted values for the
    instrument as defined in INSTRUMENT_TAG_MAPPING
    and add some deletion rules
    """
    instrument_id = label["INSTRUMENT_ID"]
    instrument_info = INSTRUMENT_TAG_MAPPING[instrument_id]
    instrument_deletions = {}
    # mess with template to drop extra wavelengths in
    if instrument_id == 'UVVIS':
        instrument_deletions['{delete:uvvis_only}'] = True
    else:
        instrument_deletions['{delete:not_uvvis}'] = True
    # MCP, lens
    if instrument_id == 'HIRES':
        instrument_deletions['{delete:hires_only}'] = True
    else:
        instrument_deletions['{delete:not_hires'] = True
    # cryocooler
    if instrument_id not in ['NIR', 'LWIR']:
        instrument_deletions['{delete:cryocooler}'] = True
    # no optical filter
    if instrument_id in ['A-STAR', 'B-STAR']:
        instrument_deletions['{delete:star_only}'] = True
    return merge(
        {'{instrument_id}': instrument_id},
        instrument_info,
        instrument_deletions
    )


# conversion classes
class ClemEDRConverter(PDSVersionConverter):
    """
    implements business logic for Clementine EDR PDS3 -> 4 version conversion

    expects an uncompressed file. specifically, it expects an uncompressed
    file with attached label and histogram, although it could probably make
    do with one you'd arranged some other way. We do this because although
    running CLEMDCMP on each file is very fast, initializing the DOSBOX
    environment takes several seconds, and there are a whole, whole
    lot of individual EDR files; you're talking about adding hundreds of hours
    to the full conversion process if you execute DOSBOX one time for each
    file.

    Workflow would then involve something like:
    (1) uncompress a batch of files with clemdcmp
    (2) make sure they're referenced in the index files (concatenated from
    the imgindx.tab files on each cl_00xx volume)
    (3) subsequently instantiate this converter with each file
    """

    def __init__(
            self,
            filename,
            *,
            template_directory="./labels/clementine/",
            image_index=None,
            template_override=None,
            **pdr_kwargs
    ):
        # default values for known attributes populated later
        self.LABEL = {}
        self.IMAGE = np.array([])
        self.IMAGE_HISTOGRAM = np.array([])
        self.filename = None
        self.fits_image_file = None
        self.histogram_file = None

        self.image_index = image_index

        super().__init__(filename, **pdr_kwargs)
        # stymie numpy's enthusiasm for 64-bit integers and roll into an
        # HDUList
        self.FITS_IMAGE = fitsify(self.IMAGE.astype("uint8"))

        if template_override is None:
            self.template = template_directory + 'edr_template.xml'
        else:
            self.template = template_override

        # 'basename' of the PDS4 product
        self.pds4_root = format_edr_time(self.LABEL["START_TIME"]) \
            + "_" + self.LABEL["INSTRUMENT_ID"].lower() \
            + "_" + self.LABEL["TARGET_NAME"].lower()

        if self.LABEL["FILTER_NAME"] != "N/A":
            self.pds4_root += "_" + self.LABEL["FILTER_NAME"].lower()
        if self.LABEL["CENTER_FILTER_WAVELENGTH"] != "N/A":
            self.pds4_root += "_" + str(
                self.LABEL["CENTER_FILTER_WAVELENGTH"].value)

    def generate_tag_mapping(self):
        """
        make a dictionary of mappings to tags in PDS4 label template.
        no arguments. looks for parameters primarily in self.LABEL;
        takes compression values from an external index.
        """
        try:
            histogram_file_size = os.stat(self.histogram_file).st_size
            fits_file_size = os.stat(self.fits_image_file).st_size
        except (AttributeError, FileNotFoundError, TypeError):
            print(
                "Converted histogram and/or FITS image files have not "
                + "been written yet or were not found. Using placeholder "
                + "9999 value for file sizes in label."
            )
            histogram_file_size = "9999"
            fits_file_size = 9999
        size_dictionary = {
            "{histogram_file_size}": str(histogram_file_size),
            "{fits_file_size}": str(fits_file_size),
        }
        generic_dictionary = clementine_edr_tags(self.LABEL)
        footprint_dictionary = clementine_edr_footprint_tags(self.LABEL)
        instrument_dictionary = clementine_edr_instrument_tags(self.LABEL)
        vector_dictionary = clementine_edr_vector_tags(self.LABEL)
        compression_dictionary = clementine_edr_compression_tags(
            self.LABEL["PRODUCT_ID"], self.image_index
        )
        target_dictionary = clementine_edr_target_tags(self.LABEL)
        return merge(
            size_dictionary,
            generic_dictionary,
            footprint_dictionary,
            vector_dictionary,
            compression_dictionary,
            instrument_dictionary,
            target_dictionary,
            {"{pds4_root}": self.pds4_root}
        )

    def write_pds4(
            self,
            output_directory,
            write_product_files=True,
            write_label_file=True,
            verbose=True
    ):
        """
        output file objects and label for a PDS4 product corresponding to
        this object. (string containing output directory -> None)
        """
        if verbose:
            print("Converting " + self.filename + " to PDS4.")
        self.fits_image_file = output_directory + self.pds4_root + ".fits"
        self.histogram_file = (
                output_directory + self.pds4_root + "_histogram.csv"
        )
        if write_product_files:
            if verbose:
                print("Writing image to " + self.fits_image_file)
            self.FITS_IMAGE.writeto(self.fits_image_file, overwrite=True)
            if verbose:
                print("Writing histogram to " + self.histogram_file)
            pd.Series(self.IMAGE_HISTOGRAM).to_csv(
                self.histogram_file,
                index=False,
                header=False,
                # PDS4 DSV records must terminate with CRLF! therefore only
                # Windows machines will produce compliant output by default.
                # the following argument corrects this.
                line_terminator="\r\n",
            )

        self.convert_label(
            output_directory, write_label_file, label_name=self.pds4_root,
            verbose=verbose
        )


class ClemMosaicConverter(PDSVersionConverter):
    """
    implements business logic for Clementine mosaic PDS3 -> 4 version
    conversion.

    Note that unlike some PDSVersionConverters, this never loads the converted
    GeoTIFF as an attribute of itself; do not attempt to use it by itself as a
    reader _and_ writer.

    Supports:

    Basemap
    -------
    Handles all tiles in the .1 and .5 km/pixel series.
    Does not handle the ortho polar maps -- their attached PDS3 labels are
    broken and they must be modified and fed to GDAL manually. Can also be
    used for the global maps and the illumination geometry maps, but some
    manual editing of labels is required (these are small series that only
    constitute ~10 products total).

    UVVIS
    -------
    Handles all tiles (both the primary multiband image tiles and the phase
    maps).

    NIR
    -------
    Handles all tiles.

    HIRES
    -------
    Handles all tiles, including the sinusoidal strip mosaic and the 4
    stereographic polar strip mosaics. Does not automatically add the suffix
    to the
    28 pairs of tiles with duplicate product IDs, but this can be done
    semi-manually -- adjust pds4_root before calling write_pds4().
    """

    def __init__(
            self,
            filename,
            *,
            template_directory="./labels/clementine/",
            source_groups: Optional[DataFrameGroupBy],
            template_override=None,
            **pdr_kwargs
    ):
        # default values for known attributes populated later
        self.geotiff_file_root = None
        self.convert_label = None
        # force lazy=True: since we use gdal to convert the raster to
        # GeoTIFF, parsing the array with pdr.read_image() is at best
        # a waste of time
        pdr_kwargs = merge(pdr_kwargs, {"lazy": True})
        super().__init__(filename, **pdr_kwargs)
        self.filename = filename
        self.tilename = os.path.split(filename)[1][:-4]
        try:
            self.mosaic = MOSAIC_PREFIX_MAPPING[self.tilename[0]]
        except KeyError:
            raise ValueError(
                "this filename doesn't look like a Clementine mosaic file."
            )

        if self.mosaic == 'hires':
            self.pds4_root = self.mosaic + '_' + self.tilename[1:4] \
                             + '_' + self.tilename[4:8] + 'e'
        elif self.mosaic == 'hires_polar':
            self.pds4_root = self.mosaic + '_' + self.tilename[1:4] \
                             + '_' + self.tilename[
                                 4] + '_peri_' + self.tilename[5:8] \
                             + 'e'
        else:
            self.pds4_root = self.mosaic + '_' + self.tilename[2:5] \
                             + '_' + self.tilename[5:9] + 'e'

        # flag the 500m/px subset of the basemap
        if self.tilename.startswith('bm'):
            self.pds4_root += '_500m'

        if template_override is None:
            self.template = template_directory + self.mosaic + '_template.xml'
        else:
            self.template = template_override
        self.source_groups = source_groups

    def generate_tag_mapping(self):
        """
        make a dictionary mapping values to tags in PDS4 label template.
        looks for values partly in self.LABEL, partly in
        cartography-specific chunks generated by gdal (passed
        as a string to this function), and partly in an index
        of source files.
        """

        # get the gdal label, generated by self.write_pds4()
        try:
            with open(self.geotiff_file_root + ".xml_gdal",
                      'r') as gdal_label_file:
                gdal_label_string = gdal_label_file.read()
        except (FileNotFoundError, UnicodeDecodeError, OSError):
            raise ValueError(
                "GDAL-written label portions not found or malformed. "
                "ClemMosaicConverter is highly dependent on GDAL for "
                "necessary portions "
                "of its output metadata; ClemMosaicConverter.write_pds4() "
                "must be run, or a placeholder must be otherwise provided, "
                "before a full tag mapping can be produced."
            )

        # there's some floating-point funny business that produces excessive
        # precision in some of GDAL's outputs. enforce precision of values
        # in source
        # dataset for attributes they affect.
        for tag in [
            'pixel_scale_x', 'pixel_scale_y', 'upperleft_corner_x',
            'upperleft_corner_y', 'scaling_factor', 'west_bounding_coordinate',
            'east_bounding_coordinate', 'north_bounding_coordinate',
            'south_bounding_coordinate', 'longitude_of_central_meridian',
            'value_offset', 'pixel_resolution_x', 'pixel_resolution_y'
        ]:
            gdal_label_string = round_xml_tag(gdal_label_string, tag, 11)

        # similarly with slightly out-of-bound values.
        for tag in [
            'north_bounding_coordinate', 'south_bounding_coordinate'
        ]:
            gdal_label_string = constrain_xml_tag(
                gdal_label_string, tag, -90, 90, 0.01
            )
        for tag in [
            'east_bounding_coordinate', 'west_bounding_coordinate'
        ]:
            gdal_label_string = constrain_xml_tag(
                gdal_label_string, tag, -180, 180, 0.01
            )

        # TODO: a kludge-y thing is happening here. it should
        # be changed if GDAL's behavior is changed/updated,
        # although it will break nothing if it is not.
        # the gdal pds4 driver currently writes the
        # parsing_standard_id for the GeoTIFF header as 'TIFF/GeoTIFF'.
        # currently the PDS4 Information Model requires that this be 'TIFF 6.0'
        if '<parsing_standard_id>TIFF/GeoTIFF</parsing_standard_id>' \
                in gdal_label_string:
            gdal_label_string = gdal_label_string.replace(
                '<parsing_standard_id>TIFF/GeoTIFF</parsing_standard_id>',
                '<parsing_standard_id>TIFF 6.0</parsing_standard_id>',
            )
        generic_dictionary = clementine_mosaic_tags(self.LABEL)

        if self.mosaic in ['basemap', 'uvvis_phase']:
            instrument_context_name = 'UVVIS'
        elif self.mosaic == 'hires_polar':
            instrument_context_name = 'HIRES'
        else:
            instrument_context_name = self.mosaic.upper()
        instrument_dictionary = INSTRUMENT_TAG_MAPPING[instrument_context_name]
        target_dictionary = TARGET_TAG_MAPPING['MOON']
        # these are the mosaics for which detailed source image
        # information is readily available to us
        if self.mosaic in ['basemap', 'hires', 'hires_polar']:
            time_dictionary = clementine_mosaic_time_tags(
                self.tilename, self.source_groups
            )
        else:
            time_dictionary = {}
        gdal_dictionary = {
            '{gdal_discipline}': get_element_block(
                gdal_label_string,
                'Discipline_Area',
                '/cart:Cartography',
                include_initial=False
            ),
            '{gdal_file_area}': get_element_block(
                gdal_label_string,
                '/File',
                'Special_Constants',
                include_initial=False,
                include_final=False
            ),
        }

        return merge(
            generic_dictionary,
            instrument_dictionary,
            target_dictionary,
            time_dictionary,
            gdal_dictionary,
            {
                "{pds4_root}": self.pds4_root,
            }
        )

    def write_pds4(
            self,
            output_directory: str,
            write_product_files=True,
            write_label_file=True,
            clean_temp_label=True
    ) -> None:
        """
        output file objects and label for a PDS4 product corresponding to
        this object.
        """
        print("Converting " + self.filename + " to PDS4.")

        mosaic_gdal_options = MOSAIC_GDAL_OPTION_DICT.copy()

        # The PDS3 standard does not consistently define these offset
        # parameters.
        # for all Clementine mosaics, they are -1.
        gdal.SetConfigOption('PDS_LineProjOffset_Shift', '-1')
        gdal.SetConfigOption('PDS_SampleProjOffset_Shift', '-1')
        gdal.UseExceptions()
        if not write_product_files:
            mosaic_gdal_options['creationOptions'] \
                .append('CREATE_LABEL_ONLY=Yes')
        self.geotiff_file_root = output_directory + self.pds4_root
        print("Writing GeoTIFF to " + self.geotiff_file_root + ".xml")
        gdal.Translate(
            self.geotiff_file_root + ".xml",
            self.filename,
            options=gdal.TranslateOptions(**mosaic_gdal_options)
        )
        shutil.move(
            self.geotiff_file_root + ".xml",
            self.geotiff_file_root + ".xml_gdal"
        )
        self.convert_label(
            output_directory, write_label_file, label_name=self.pds4_root
        )
        if clean_temp_label:
            os.remove(self.geotiff_file_root + ".xml_gdal")


class ClemBrowseWriter(PDS4Writer):
    """
    ultra-simple browse label writer. doesn't move the images 
    around or anything.
    """

    def __init__(
            self,
            base_product_id,
            dataset,
            browse_image_type=None,
            *,
            template_directory="./labels/clementine/browse/"
    ):
        self.dataset = dataset
        self.base_product_id = base_product_id
        self.browse_image_type = browse_image_type
        if browse_image_type is None:
            if self.dataset not in ['basemap', 'hires', 'edr']:
                raise ValueError(
                    "Must specify which type of browse image for NIR and "
                    "UVVIS.")
            self.pds4_root = base_product_id + '_' + 'browse'
        else:
            if self.dataset in ['basemap', 'hires', 'edr']:
                raise ValueError("This set only has one type of browse image.")
            self.pds4_root = base_product_id + '_' + browse_image_type

        super().__init__(self.pds4_root)
        self.template = template_directory + dataset + '_browse_template.xml'

    def generate_tag_mapping(self):
        """
        make a dictionary of mappings to tags in PDS4 label template.
        """
        return {
            "{product_id}": self.base_product_id,
            "{browse_image_type}": self.browse_image_type
        }

    def write_pds4(self, output_directory, verbose=False):
        self.write_label(output_directory, True, label_name=self.pds4_root,
                         verbose=verbose)
