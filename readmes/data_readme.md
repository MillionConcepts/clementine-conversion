# Clementine Imaging Data Collection README file

## introduction

This collection contains observational products from the Deep Space Science
Experiment's Clementine-1 orbiter ("Clementine"). 

It is essentially a conversion and reorganization of observational data from
those portions of the "Mission to the Moon" archive (MttMA) Volume Series held
by the PDS Imaging Node (IMG), specifically including the following five PDS3
data sets:

* CLEM1-L/E/Y-A/B/U/H/L/N-2-EDR-V1.0 ("EDR")  
* CLEM1-L-U-5-DIM-BASEMAP-V1.0 ("basemap") 
* CLEM1-L-U-5-DIM-UVVIS-V1.0 ("UVVIS mosaic")
* CLEM1-L-N-5-DIM-NIR-V1.0 ("NIR mosaic")
* CLEM1-L-H-5-DIM-MOSAIC-V1.0 ("HIRES mosaic")

The EDR data were collected between January and May 1994, during Clementine's
two Earth 'phasing loop' flybys, lunar insertion, systematic lunar mapping,
and transfer back to Earth orbit. They end on May 7, 1994, when a catastrophic
attitude control failure caused the termination of the remainder of
Clementine's planned observations. The mosaic products were subsequently
produced and published between 1995 and 1998 (some documentation in the NIR
dataset was revised slightly in 2007).

This document provides a brief description of the organization and format of
our versions of these observational products, along with notes on how they
differ from the contents of their source data sets, and on several interesting
or troubling features of the archive.

*Note: all paths are given relative to the bundle root.*

## EDR

### general discussion

The EDR component of this collection contains data from six separate
instruments (some of these are given more than one name in the literature, and
even in PDS context products, but these are the names we use in this bundle):

* High Resolution Camera (HIRES) -- 598877 products
* Longwave Infrared Camera (LWIR) -- 303942 products
* Near-Infrared Camera (NIR) -- 386773 products
* Star Tracker A (A-STAR or STA) -- 2741 products
* Star Tracker B (B-STAR or STB) -- 3493 products
* Ultraviolet/Visible Camera (UVVIS) -- 597891 products

This adds up to about 1.9 million observational data products. Between the
image files themselves, their detached PDS4 labels, and detached CSV versions
of the histograms included in the compressed PDS3 files, these products are
stored across roughly 5.7 million distinct files. We did not want to follow
the directory structure and naming convention of the MttMA, which was highly
constrained by the limitations of the ISO 9660 filesystems on which it was
originally distributed, including 8-letter names, 3-letter extensions, 650 MB
volume sizes, and an expectation that their users would not be able to rapidly
switch between separate 650 MB volumes due to loading times and a likely lack
of multiple optical drives. We wanted to cluster files more 'semantically' and
less 'mechanically.' 

However, even 25+ years later, computers struggle to deal with 5.7 million
files divided into 5+ million directories. The following choices attempt to
simultaneously optimize for semantic richness, structural consistency,
parsimony of total directories, and avoidance of large bottom-level
directories. Obviously, they fail on every count, although less poorly than
they could.

### EDR file formats

Most (>80%) of the Clementine observational data were compressed onboard
using a proprietary hardware-accelerated JPEG-style discrete cosine transform
compression algorithm designed by Matra named "CLEM-JPEG" (with several
different frequency tables named "CLEM-JPEG-0", "CLEM-JPEG-1", and so on).

For most purposes, including archival, the instrument team retained these data
in their native forms, whether compressed or uncompressed (aside from
depacketizing them into discrete binary files containing individual
observations). For archival, they also attached PDS3 labels, image histograms,
and sometimes browse images to each file. To permit use of the EDR products,
they included decompression and image-reading software in the archive. To
increase usability of the archive and meet PDS4 stadards, we have detached
these images from their metadata and ancillary data, decompressed those that
were compressed, and converted them to FITS format.  Although they are now
readable by general-purpose software, often contain visually-recognizable
features, and may have been subject to lossy compression, these products
remain "raw" in the sense that they have not been "scientifically" processed
-- radiometrically calibrated, corrected for instrument signature, or
otherwise modified to make them straightforwardly suitable for science
purposes. 

Each Clementine EDR product in this bundle now consists of three files:
1. ```*.xml``` label file
2. ```*.fits``` a FITS image array
3. ```*.csv``` a histogram of image values (taken directly from the compressed file) 

All FITS arrays are 8-bit (0-255) single-band images. Array size varies by
instrument:

* 576 x 384 for the star trackers
* 288 x 384 for UVVIS and HIRES
* 256 x 256 for NIR
* 128 x 128 for LWIR 

### EDR directory structure

#### instrument

All directory names start with:

/data/edr/(instrument)/

Where (instrument) can be 'hires', 'lwir', 'nir', 'sta', 'stb', or 'uvvis'.

#### filter

Instruments with filter wheels -- HIRES, NIR, and UVVIS -- are then further
subdivided into filter subdirectories, which we generally name with the
canonical center wavelength of the given filter in nanometers.

For HIRES, this can be: '0415', '0560', '0650', '0750', 'opaque', 'broadband',
or 'other'. 'Broadband' refers to the 400-800 nm broadband 'E' filter.
'Opaque' refers to the opaque 'F' filter. 'Other' denotes products that appear
to have no reliable filter information, products for which the filter wheel
was behaving oddly, or similar.

For UVVIS, this can be:'0415', '0750', '0900', '0950', '1000', 'broadband', or
'other'. 'Broadband' refers to the 400 to 950 nm  broadband 'F' filter.
'Other' again denotes products that have low-quality filter information. (The
bandpasses of UVVIS slightly belie its name; this is not a mistake.)

For NIR, this can be: '1100', '1250', '1500', '2000', '2600', '2780', or
'other'. 'Other' again denotes products that have low-quality filter
information.

#### mission phase

The next subdirectory level refers to mission phase. This can be:

* non-systematic-mapping phases
	* leo (Low-earth orbit, used only for certain early STA and STB 
	images)
	* epa (Earth phasing loop A prior to lunar insertion)
	* epb (Earth phasing loop B prior to lunar insertion)
	* lun_bef (Moon observations prior to systematic mapping)
	* sky_bef (sky observations prior to systematic mapping)
	* ear_aft (Earth observations after systematic mapping)
	* lun_aft (Moon observations after systematic mapping)
	* sky_aft (sky observations after systematic mapping)
	* unknown
* systematic lunar mapping phase, by latitude bin: 
	* (0-9)0(n or s)(0-9)0, the southernmost coordinate always  first; for
	example, '00n10' denotes observations intended to map areas of the lunar
	surface between the equator and 10 degrees north; '30s20' denotes
	observations intended to map areas of the lunar surface between 30 and
	20 degrees south. **WARNING:** these bins denote *general mission intent of 
	a general sequence of observations*, and are really something like sub-phase 
	names. They do **not** give the actual latitude or longitude of a particular 
	camera boresight (or even whether it is actually pointed at the lunar surface).

#### latitude / longitude (systematic mapping phase only)

Products from systematic mapping phase are then divided into a latitude
subdirectory and a longitude subdirectory. These values *do* refer to the
latitude and longitude of the camera boresight, rounded to the nearest degree,
in 90-degree s / n latitude and 0-360 degree e longitude, like '/11s/223e/' or
'/2n/4e/'.

Products without reliable boresight information or which are aimed at non-Moon targets
during the systematic mapping phase are placed into a '/no_boresight/' subdirectory 
at this level.

#### month + day

Products are further subdivided into four-digit month and day subdirectories.
(All products are from 1994.) For instance, products from March 6, 1994 are
placed into an '/0306/' subdirectory at this level.

#### hour

Products are then separated by two-digit (00-24) hour.

#### minute (non-systematic-mapping phases only)

Products from non-systematic-mapping phases then receive one more subdirectory
division, by two-digit (00-60) minute.

### EDR filenames

EDR filenames, (prior to filename extensions) have the structure:

```(year)(month)(day)t(hour)(minute)(second)(ms)_(instrument)_(target)_(filter)_(wavelength)```

The first portion of the filename is thus a collapsed ISO 8601 timestamp. (All times are
UTC.) 'Instrument' can take the same values as above; 'target' can be 'earth',
'moon', 'sky', or 'unk' (for 'unknown'); 'filter' is the single-letter name of
a filter; wavelength is  the canonical center wavelength of the filter.
'Filter' and the corresponding underscore are omitted for STA and STB. Filter
is always 'a' for LWIR's single filter. 'Wavelength' is the same as in the
directory names above, except: 
* for the UVVIS and HIRES broadband filters, we use the canonical 650 nm center
  wavelength instead of 'broadband'
* we use no wavelength appendage at all for the HIRES opaque 'f' filter
* we list the canonical 8750-nm center wavelength of the single LWIR filter rather than 
  omitting it 

Also, observations from instruments with filter wheels that have bad metadata
about which filter was in use omit the ```_(filter)_(wavelength)``` section
entirely.

**IMPORTANT:** this base filename is also the same as the final portion of a
product's PDS4 logical identifier (LID).

### examples

1. /data/edr/hires/0750/30s20/27s/280e/0305/17/19940305t174033140_hires_moon_d_750.fits
is an image generated from an observation of the lunar surface at 17:30:33.140
on March 5, 1994. It was taken by HIRES using its 750-nm "D" filter. The
camera boresight is centered somewhere near 27 degrees South  and 280 degrees
East. It was taken during systematic lunar mapping with intent to image 
latitudes within the 30 South - 20 South range. The product's LID is 
urn:nasa:pds:clementine:data:19940305t174033140_hires_moon_d_750.

2. /data/edr/uvvis/0415/40s30/38s/257e/0404/01/19940404t013557280_uvvis_moon_a_415.xml
is the PDS4 label for an observation of the lunar surface at 01:35:57.280 on
April 4, 1994. It was taken by UVVIS using its 415-nm "A" filter. The camera
boresight was centered somewhere near 38 degrees South and 257 degrees East.
It was taken during systematic lunar mapping with intent to image latitudes
within the 40 South - 30 South range. The product's LID is 
urn:nasa:pds:clementine:data:19940404t013557280_uvvis_moon_a_415.

3. /data/edr/uvvis/0950/ear_aft/0402/05/46/19940402t054632093_uvvis_earth_d_950.fits
is an image generated from an observation of the Earth at 05:46:32.093 on
April 5, 1994. It was taken by UVVIS using its 950-nm "D" filter. It was taken
after the end of a lunar mapping sweep. The product's LID is 
urn:nasa:pds:clementine:data:19940402t054632093_uvvis_earth_d_950.

4. /data/edr/lwir/50s40/45s/261e/0307/04/19940307t042257638_lwir_moon_a_8750.csv
is a histogram corresponding to an image generated from an observation of the
lunar surface at 04:22:57.638 on March 7, 1994. It was taken by LWIR using its
8750-nm "A" filter (like all LWIR observations). The camera boresight is
centered somewhere near 45 degrees South and  261 degrees East. It was taken
during systematic lunar mapping with intent to image latitudes within the 50
South - 40 South range. The product's LID is 
urn:nasa:pds:clementine:data:19940307t042257638_lwir_moon_a_8750.

### assorted caveats and errata

These notes should not be considered anything close to comprehensive. The
archive is very large.

#### decompression process

We decompressed these files from CLEM-JPEG format by executing the DOS version
of the mission's official decompression software (CLEMDCMP.EXE) within DOSBOX,
an open-source x86 / DOS emulator. The decompressed binary arrays produced by
CLEMDCMP look correct and appear to match all available metadata, but we
essentially treated it as a black box; we have no way to fully validate its
output.

There were a small number of images for which we were unable to parse the
output from CLEMDCMP. We suspect that these files are in some way corrupt, but
it is also possible that this is the result of some rare bug in CLEMDCMP or
some other portion of our conversion pipeline. We have not included these
files in this bundle. Their PDS3 product IDs are: lla0807f.222, lla3440m.230,
lla2912l.202, lla0977f.210, lla1744i.174, lna5725y.034, lla3357m.226,
lhb0557k.323, lla2996l.254, lla1355g.279, lla2236j.260, lla1914s.341,
lla2320j.268, lla1999i.280, and lla2167j.274.

#### image statistics 

We did not propagate image statistics from the PDS3 labels. This is because
they are often slightly wrong (generally because of an error identifying
MINIMUM; see /document/legacy/pds3_edr_errata.txt) and create PDS4 validation
errors. It is unclear whether this error was propagated into the image
histograms. They are *mostly*  right, however, so we suspect the values in
/document/index/edr_metadata_index.csv are still useful exploratory tools.

#### incorrectly named targets

A number of files, especially during the earth phasing loops and in the 
no_boresight' directories, are probably mislabeled as targeting the Moon when
they target something else, such as the Earth. There are for instance several
series of beautiful multispectral observations of weather patterns that are
most certainly not on the Moon. See /document/legacy/edr_pds3_errata.txt for
possible clues. Use this target information with caution. During the lunar 
mapping phases, this metadata appears to be more reliable.

#### timing

These files have no explicitly-defined stop times in metadata. Each EDR label
thus uses a single value for its start and stop times. Detail about exposure
duration is available in the img:exposure_duration attribute of each label.
More reliable information about the timing of some products can probably be 
generated using the kernels in CLEM1-L-SPICE-6-V1.0 [at NAIF].

#### duplicate products

There are 6751 pairs of EDR products with identical timestamps and nearly
identical other metadata. Their image arrays were all discovered after
decompression to be byte-level duplicates. These were apparently inserted into
separate mission-phase series by mistake. We have discarded one image from
each pair. See /document/index/duplicate_edr_products.csv for an index of
discarded duplicate products.

Note that this issue jumped out at us only because it interfered with our
filename scheme. We did not make an exhaustive search for metadata errors of
this type. It is worth noting that many other sets of byte-level duplicate
images exist in the archive, and that this is not necessarily symptomatic of
any archival error. The image arrays are small enough that, with a sample set
of this size, a reasonable number of duplicates would appear even if the
images had been generated from white noise, and many of the duplicate images
appear to be the result of detector high or low saturation -- for instance,
201543 of the images in the archive are simply 288x384 arrays of zeroes, and
another 29351 are 288x384 arrays uniformly valued 255.

#### UVVIS 'F' (broadband) filter

Except for a small number of early sky observations, most UVVIS 'F' broadband
filter images consist of pixels at or near high saturation. This does not
appear to have been caused by our conversion process -- it matches object
statistics in the original labels. It is unclear whether the filter was
damaged, these images are overexposed due to higher transmission of the
broadband filter compared to the narrowband filters, or there was some 
bug in transmission or downlink from the spacecraft specific to this filter.
We are inclined to believe they are overexposed or the filter was displaced,
as you can see portions of well-exposed image in a handful of these arrays 
that appear to capture the filter wheel mid-rotation.

## mosaic data sets

### introduction

The basemap, NIR, and UVVIS mosaics are nearly-complete maps of the lunar
surface, mostly in an equal-area sinusoidal projection at 100 m / pixel
(except at the poles and in certain special basemap products). The basemap was
generated from 750-nm "B" filter observations by UVVIS and used as a reference
for the UVVIS and NIR multispectral mosaics; these three mosaics all share
a tiling scheme.

The HIRES mosaic, by contrast, is made up of a series of "strips," each
containing all successfully calibrated and geolocated observations with the
HIRES camera's "D" (750-nm) filter from a single orbit. Each of these strips
is divided into individual tiles of ~1.75 degrees latitude and ~.05 degrees
longitudinal 'width' (note that, because the strip is curved, it may traverse
more longitude than its width). Successive tiles from a strip are
latitudinally adjacent to one another; tiles from separate strips are not
generally longitudinally adjacent to one another.

### file formats

These were originally archived as uncompressed raster arrays in the image
format sometimes referred to as "PDS3", with attached PDS3 labels. The UVVIS
and NIR mosaics also had detached ISIS "qube" labels. 

We converted all of these products to GeoTIFF files with detached PDS4 labels. 
Each product now consists of a .tif image file and a .xml label file.

Basemap and HIRES tiles are single-band; UVVIS tiles are 5-band; NIR tiles are
6-band. Image width and height vary by tile; however, most but not all tiles
in the basemap/NIR/UVVIS mosaics are 2127 pixels wide and most range in height
from 1700 to 2200 pixels.  Most of its tiles are between 150 and 450 pixels
wide and 2653 pixels high.

### array values

Array values for the mosaic files (other than the illumination geometry maps)
are in geometrically, photometrically, and radiometrically-normalized DN
(detector counts). The HIRES mosaic is given in single-byte integers; the
other mosaics are in two-byte signed integers.

Per the mosaic SIS files, applying the scale and offset values given in the
labels should convert array values to fractional reflectance. We encourage
caution, however, in the naive application of these scale and offset factors.
Aside from subtler calibration questions beyond the scope of this
documentation, there are some gross inconsistencies that may suggest technical
errors in archival or reduction. While we have not rigorously investigated
this across all mosaic sets, we found the following issues in casual spot
testing:

1. In a number of test cases, at least one band appeared notably off-scale. In
other words, after applying scale and offset, it contained many fractional
reflectance values roughly continuous with the other values in the array but <
0 or > 1. 
2. In a smaller number of test cases, at least one band appeared to
contain significant numbers of pixels with values quite close to the minimum
or maximum value of the data type (-32768 / 32767) that were _not_ among the
documented special constant values. These are most likely saturated pixels
that should have been but were not flagged with special constants.

### general notes on filenames

Unlike the EDR products, we have modified these products' names only slightly
from their originals. These modifications are intended for clarity and to help
distinguish them from copies of the MttMA files (and because, unlike the
original archivists, we are not constrained to 8-character filenames):

1. We have prepended the mosaic name to the filename
2. We have added an 'e' to the longitude 'field' 
3. We have separated 'fields' with underscores
4. We have converted filenames to lower case
5. In some special cases, we have added descriptive suffixes to the filename 
or changed it entirely to a descriptive name.

We have, however, strictly retained the nominal lat/lon assigned by the
original archivists in these filenames in order to preserve their tiling
schemes. Please note that these filenames refer to *tiling position*
(described under 'tiling schemes' below), not necessarily to actual lat/lon
extrema. They also use N/S latitude and 0 - 360 longitude, while
GDAL-generated values within the labels use -90 to 90 latitude and -180 to 180
longitude. 

**note to reviewers / curating facility**

*we weren't really sure what lat/lon convention you'd like to use. It will be
pretty straightforward to switch signs / etc. on these labels and filenames
if you'd prefer to make them completely consistent. --million concepts*

### filenames 

Most Basemap, UVVIS, and NIR tiles have names that follow this pattern:
```(mosaic)_(center latitude)(n or s)_(three-digit center longitude)e```

The basemap also includes a 500 m / pixel tileset; the naming convention
for these tiles is the same, except that they have ```_500m``` appended
to their filenames.

The HIRES naming convention is similar, except that there is an additional
digit of longitude, with an implied decimal place. See 'tiling scheme' below
for notes on these latitude and longitude values. The polar tiles also include
appended information on their respective pole and periapsis.

### directory structure

#### basemap, UVVIS, and NIR

**/data/(mosaic)/(latitude)**
Subdirectories, from 87s/ to 87n/, containing all tiles with that nominal
center latitude.

**/data(mosaic)/(latitude)/(longitude bin)**
Subdirectories -- 000, 100, 200, and 300 -- containing all tiles of a given
center latitude with center longitudes between, respectively, 0-100, 100-200,
200-300, and 300-360 degrees East.

#### basemap only

**/data/basemap/global_and_polar/**

This directory contains several special basemap products: 
1. reduced-resolution maps of the lunar nearside, farside, and entire surface
2. polar maps in orthographic projection
3. emission, phase, and incidence angle maps for the lunar nearside and farside

**/data/basemap/big/**

This directory contains an additional lunar tileset at 500m / pixel.

#### UVVIS only

**/data/uvvis/phase/**

**/data/uvvis/phase/(latitude)/**

**/data/uvvis/phase/(latitude)/(longitude bin)/**

An additional directory tree of phase backplane tiles matching the UVVIS / basemap
/ NIR tile sets.

#### HIRES

**/data/hires/(longitude)/**

Subdirectories each containing an entire HIRES 'strip' -- all tiles projected
at that central longitude.

**/data/hires/polar/(pole)(periapsis)/**

The polar portions of the HIRES mosaic are divided into four separate polar
stereographic projections -- one for each orbital periapsis for each pole
(split in this way because the mapmakers found that this produced more
visually uniform tiles).

**/data/hires/polar/(pole)(periapsis)/(latitude bin)/**

Subdirectories containing all polar HIRES tiles for that pole and orbital
periapsis.

### tiling schemes

A single scheme is shared by the basemap, the UVVIS mosaic, and the NIR
mosaic. See /document/index/mosaic_tiling_scheme.html for a quick reference to
this scheme. Implied latitudes and longitudes in these filenames are not
selected in a totally consistent fashion, although they generally roughly
match the center of the tile.

The HIRES strip mosaic is georeferenced to the basemap, but does not share
this tiling scheme. The longitude implied in each HIRES tile's name is its
central longitude of projection: the longitude at which the orbit during which
the images that make up the strip were taken crossed the lunar equator. (This
longitude may or may not actually fall within a particular tile.) Note that
this is four digits; there is an implied decimal after the third. The implied
latitude is one of the latitude extrema of the tile, rounded to the nearest
integer (**not**, as stated in some documentation, the central latitude of the
tile). The selection of northernmost or southernmost extremum is not totally
consistent, but it is generally the one closest to the equator, and successive
tiles in a strip always have distinct implied latitudes. 

The HIRES polar stereographic mosaics use yet another convention; the implied
latitude and longitude of each tile are simply its central latitude and
longitude.

### examples

/data/uvvis/17n/300/uvvis_17n_309e.tif is a GeoTIFF file containing a tile
from the UVVIS mosaic centered at 17 degrees North and 309 degrees East.

/data/hires/0228/hires_07n_0228e.tif is a GeoTIFF file containing a tile from
a HIRES mosaic strip projected along 22.8 degrees East longitude. The southern
end of the tile terminates at 7 degrees North.

/data/hires/polar/sn/79s/hires_polar_79s_n_peri_006e.xml is a PDS4 label
for a HIRES tile from the south polar submosaic generated from north orbital
periapsis images, centered at 79 degrees South and 6 degees East.


## assorted mosaic errata and caveats

### mosaic bounding boxes

The bounding boxes defined in the labels of these products differ from the
MAXIMUM_LATITUDE, MAXIMUM_LONGITUDE, MINIMUM_LATITUDE, and MINIMUM_LONGITUDE
parameters in the PDS3 labels of their source products. There are several
reasons for this:

1. Most importantly, the MAXIMUM_LATITUDE, MAXIMUM_LONGITUDE,
MINIMUM_LATITUDE, and MINIMUM_LONGITUDE parameters are not defined
consistently in the PDS3 labels. Each parameter does contain a latitude or
longitude value from one of the image's corners, but the corner is not
selected consistently (it appears to be selected according to whether it
matches the tile's nominal latitude / longitude within the tiling scheme) and
is not necessarily a corner at which the latitude or longitude parameter takes
on an extremum value. For this reason, we have not propagated these parameters
to any part of the PDS4 labels and instead use values computed by GDAL from
the map projection.
2. Which points of the tile are used as 'easternmost' and which 'westernmost'
are sometimes selected differently, at least partly due to the Clementine
DIM's original choice of a 0 - 360 longitude scheme as opposed to GDAL's
standardized -180 - 180 longitude scheme. 
3. This shouldn't actually be a source of disparity, but is important to
mention. GDAL computes geotransforms partly using the PDS3
LINE_PROJECTION_OFFSET and SAMPLE_PROJECTION_OFFSET parameters. See
```ParseSRS()``` in the gdal PDS driver (presently served at
https://github.com/OSGeo/gdal/tree/master/gdal/frmts/pds/pdsdataset.cpp).
However, PDS3 datasets do not consistently define these offsets. This issue
existed as early as the 1990s; the Clementine archivists were specifically
aware of inconsistencies between their mosaic, the Venus Magellan FMAP, and
the Mars Viking Orbiter MDIM (see Eric Eliason's memo "Discrepancies of
Projection Offset Parameters Among USGS-Produced Planetary Digital Global
Maps," appended to errata for each of the mosaic sets, e.g.
/document/legacy/basemap_pds3_errata.txt). The GDAL developers are also aware
of this issue (see https://trac.osgeo.org/gdal/ticket/5941 and comments on
```ParseSRS()```) and offer configuration options to change this offset for
alternatively-compliant datasets: ```PDS_SampleProjOffset_Shift``` and
```PDS_LineProjOffset_Shift```. According to the specification of these
parameters in multiple files across the MttMA, the value of each of these
offsets for the Clementine data should be -1. This is accounted for in our
conversion code and should produce no disparities, but we are not entirely
confident that the original definition of line 1 / sample 1 was fully
consistent across every tile of all the mosaics.

### missing offset/scale in hires

The PDS3 labels of the source products for /data/hires/2084/hires_39s_2084e.xml 
and /data/hires/2084/hires_48s_2084e.xml had 'NaN' values for PDS3 parameters
OFFSET and SCALING_VALUE. We have simply omitted the related attributes from
these PDS4 labels.

### hires overlapping or cut-off tiles

28 of the tiles in the HIRES mosaic appear to be split between two separate
files on two separate volumes -- they are two apparently-contiguous image
files with the same PDS3 product ID. In all cases, this occurs when a strip is
split across two volumes and a single tile crosses the equator. We have
appended the original volume number to the product IDs and filenames of these
tiles in order to distinguish them from one another. Some map projection
values in some of these tiles look suspiciously as if they may have
accidentally been north-south mirrored, and we urge caution in their use.

### missing or unconverted products

#### basemap

We did not include products from this PDS3 set that we considered essentially
duplicative, specifically including reduced-resolution browse images and
reduced-resolution polar maps.

#### uvvis

Several pieces of documentation refer to reduced-resolution global maps
similar to those in the basemap data set to be released in ancillary CDs
following the 78 CDs of the primary series. However, these do not appear to be
present in the MttMA.

### extra tiles in hires source index

There are 162 tiles referenced to in the HIRES EDR source product index that
do not appear to be in the MttMA. It is possible that these are identifiers
retained from a legacy naming system, or that they refer to tiles discarded
during a QA step prior to archival.

