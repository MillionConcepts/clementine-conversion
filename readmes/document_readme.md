# Clementine Imaging Document Collection README file

## introduction

This collection contains documentation related to the Deep Space Program
Science Experiment's Clementine-1 orbiter ("Clementine") and some of its raw
and derived observational data. It includes scientific background material,
discursive technical documentation, and indices intended to help users locate
and select products within this bundle's data collection. Most of the files in
this collection are copied, derived, or reformatted from those portions of the
"Mission to the Moon" archive (MttMA) Volume Series held by the PDS Imaging
Node (IMG), specifically including the following five PDS3 data sets:

* CLEM1-L/E/Y-A/B/U/H/L/N-2-EDR-V1.0 ("EDR")  
* CLEM1-L-U-5-DIM-BASEMAP-V1.0 ("basemap") 
* CLEM1-L-U-5-DIM-UVVIS-V1.0 ("UVVIS mosaic")
* CLEM1-L-N-5-DIM-NIR-V1.0 ("NIR mosaic")
* CLEM1-L-H-5-DIM-MOSAIC-V1.0 ("HIRES mosaic")

This document gives an overview of the directory structure of this collection
and its included files, along with some notes on how users might best make use
of them in order to understand the Clementine data as a whole. Some of the
contents of this file partially duplicate descriptions from product labels.

**IMPORTANT:** some of the documents in this collection are wholly or
partially deprecated by the ways in which the Clementine observational data
has been reformatted or reorganized in this bundle. Specific notes on these
deprecations are contained in this file (as well as individual product
labels).

## general notes

### file formats

Many of the files in this collection originally came in multiple formats,
including plain (ASCII or UTF-8) text, PostScript, Word 95, Excel 95, and PDF
1.2. As few of these files had embedded images or other meaningful rich text
features, we typically selected the plain text version of a document and
converted it to UTF-8 text. Our generated or concatenated tables are all in
UTF-8 CSV. In one case, we generated a PDF/A from many Excel 95 files whose
visual character we intended to retain; in another case, we kept an HTML / JS
file as HTML / JS. 

### file naming and concatenation

We have changed filenames and concatenated files fairly freely. The creators
of the MttMA were bound by the limitations of the ISO 9660 filesystem,
including 8-letter names, 3-letter extensions, 650 MB volume sizes, and an
expectation that their users would not be able to rapidly switch between
separate 650 MB volumes. 25 years later, we are not bound by those
limitations. We have often given files longer and more descriptive names,
chunked long tables in ways that felt semantically more sensible but would
have been physically impossible for the original archivists, and so on.

## directory listing

All paths are given relative to the root directory of the bundle. 

All files in this collection share base file names with their .xml PDS4
labels. For this reason, we have not listed labels separately.

### /document

Root directory of this collection.

#### document_readme.md

The file you are reading right now.

#### collection_document_inventory.csv

PDS4 inventory file for this collection.

----

### /catalog

Renamed copies of PDS3 .CAT catalog files from the original archive. These
files provide high-level overviews of important features of the mission,
instrument, archive, and associated concepts. *Note: the EDR data set did not
include catalog files.*

#### mission.txt       

PDS3 catalog file providing summary information on the Deep Space Program
Science Experiment as a whole.

#### insthost.txt       

PDS3 catalog file providing summary information on the Clementine-1 orbiter
itself.

#### basemap_dataset.txt

Provides high-level information regarding the Clementine basemap. **Warning:**
This document is partially deprecated -- this bundle is not organized or
formatted in the same ways as the PDS3 archive, and users should ignore
references to file types, storage media, directory structure, and so on.
However, it still contains valuable information on the data set's reduction
pipeline, provenance, and contents.

#### hires_dataset.txt

The same, but for the High-Resolution Camera (HIRES) mosaic.

#### nir_dataset.txt

The same, but for the Near-Infrared Camera (NIR) mosaic.

#### uvvis_dataset.txt

The same, but for the Ultraviolet/Visible (UVVIS) mosaic.

#### hires_inst.txt

PDS3 instrument catalog file for HIRES. Provides concise, high-level summary
information on the instrument's objectives, observing history, and properties.

#### lwir_inst.txt

The same, but for the Long Wavelength Infrared Imager (LWIR). *Note: this file
is taken from CLEM1-L-LWIR-3-RDR-V1.0, a MttMA data set that is otherwise not
included in this archive.*

#### nir_inst.txt

The same, but for NIR.

#### star_inst.txt

The same, but for the star tracker cameras (A-STAR and B-STAR). *Note: this is
not actually a .CAT file; no catalog file is provided in the MttMA for the
star tracker cameras. This text was extracted from PDS4 context products for
these cameras, which itself claims to have taken the text from a no-longer-
extant PDS3 catalog at wundow.wustl.edu.*

#### uvvis_inst.txt

The same, but for UVVIS.

#### basemap_person.txt

Provides information on personnel associated with the basemap. **Warning:**
the contact information in all of these person.txt (originally PERSON.CAT)
documents is between 10 and 28 years old, and we have made no attempt to
verify or update it! We have retained these documents for historical and
citational purposes, not as contact lists.

#### hires_person.txt

The same, but for the HIRES mosaic.

#### nir_person.txt

The same, but for the NIR mosaic.

#### uvvis_person.txt

The same, but for the UVVIS mosaic.

#### basemap_ref.txt

PDS3 reference catalog file for the Clementine basemap. Provides a list of
references to external publications that the data providers cited in other
catalog or documentation files, or that they considered especially relevant to
potential users of the data.

#### hires_ref.txt

The same, but for the HIRES mosaic.

#### nir_ref.txt

The same, but for the NIR mosaic.

#### uvvis_ref.txt

The same, but for the UVVIS mosaic.

#### basemap_uvvis_nir_dsmap.txt

PDS3 map projection catalog file. This is the version from the NIR mosaic, but
the file -- and the sinusoidal map projection it describes -- is nearly
identical across the basemap, UVVIS, and NIR mosaic data sets. The projection
is also used for most of the HIRES mosaic.

#### hires_dsmap.txt               

PDS3 map projection catalog file for the HIRES mosaic, describing the polar
stereographic map projection used for the four polar HIRES mosaic segments.
Presumably, users were intended to refer to the basemap, UVVIS, or NIR data
volumes, and the file we have included here as basemap_uvvis_nir_dsmap.txt,
for a description  of the sinusoidal map projection shared between those
mosaics and the non-polar segments of the HIRES mosaic.

----

### /core 

This subdirectory contains documents that serve an explicit or implicit
Software Interface Specification (SIS) function, directly describing the
contents, provenance, and functionality of the data sets. *Note: only the EDR
had a formal SIS. The documentation for the mosaic sets is quite terse.*

#### edrsis.txt  

SIS (Software Interface Specification) for the Clementine EDR images.
**WARNING:** Portions of this document are deprecated. Users are encouraged to
disregard references to filesystems and storage media. Users are also
encouraged to disregard references to PDS3 label structure except inasmuch as
it sheds light on what what categories of metadata are available for this 
archive and when they might and might not be useful. Despite its deprecated
portions, it provides invaluable information about the provenance and contents
of the EDR data corpus.

#### edr_volinfo.txt

PDS3 volinfo file for the Clementine EDR data set. The function of PDS3
volinfo files was not standardized at this time. This one is a high-level
description of the Clementine mission as a whole with special attention to
observational practices relevant to the EDR data set. It can be considered a
kind of supplement to the mission catalog file.

#### basemap_volinfo.txt 

PDS3 volinfo file for the Clementine basemap. In contrast to the EDR volinfo
file, this volinfo file is essentially a brief SIS for the basemap.
**WARNING:** It should be considered partially deprecated. This bundle is not
organized or formatted in the same way as the PDS3 archive, and users should
ignore references to file types, storage media, and directory structure; users
should also disregard descriptions of PDS3 label features except inasmuch as
they shed light on what metadata were generated by the mapmakers. It
nevertheless provides a great deal of useful information on the contents,
history, calibration, reduction, and general character of this data set.

#### hires_volinfo.txt 

Like basemap_volinfo.txt, but for the HIRES mosaic.

#### nir_volinfo.txt

The same, but for the NIR mosaic.

#### uvvis_volinfo.txt

The same, but for the UVVIS mosaic.

----

### /index

This subdirectory contains products intended to help users navigate the
observational data contained in this bundle. Most of them are plain-text
comma-separated value (CSV) tables designed to be compatible with a wide
variety of software tools, including standard spreadsheet programs and POSIX
command-line tools. (This format is formally named 'delimiter-separated value'
or 'PDS DSV 1' by the PDS.) 

#### *a note on large CSV files*

Because there are ~ 1.9 million products in the EDR, edr_index.csv and
edr_metadata_index.csv are quite large. They should either be accessed with
software intended especially for dealing with large CSV files or read in
parts. Appropriate tools include Microsoft Excel's Data Model, the
```read_csv()``` function from the ```pandas``` library for Python, or
MATLAB's ```readmatrix()``` function. Reading in parts can be accomplished
easily from the command line on  POSIX-ish operating systems like macOS or
Linux. For instance, if LibreOffice is installed, running ```head -n 1
edr_metadata_index.csv > temp.csv && head -n 200001 edr_metadata_index.csv |
tail -n 10000 >> temp.csv && libreoffice temp.csv``` will write the header and
lines 190000-200000 of the EDR metadata index to a temporary CSV file and open
it as a spreadsheet in LibreOffice Calc.

#### *a note on NIR and UVVIS source indices*

Detailed EDR source image information for the UVVIS and NIR mosaics is not
present in the MttMA. UVVIS mosaic documents reference a forthcoming 79th CD
with ancillary information that includes a source index, but if this 79th CD
was ever produced, it is not in the MttMA. Similarly, NIR mosaic documents
mention that a source index is available online, but the page it points to is
not presently maintained, and no source index appears to be hidden anywhere in
the MttMA.

#### basemap_edr_source_index.csv  
 
Index of basemap mosaic tiles and their EDR source products in DSV format.
This is concatenated from a variety of indices and metadata. 

*Notes* 
1. This index includes references to 11 EDR images with no assigned
basemap tile. These may have been files used in the creation of the basemap
but assigned to no specific tile; they may also have been included in one of
the PDS3 basemap source indices by mistake. 
2. No EDR source indices appear to be available for the basemap orthographic 
polar tiles. 
3. The basemap documentation notes that the latitude and longitude values for 
the referenced EDR images may differ from the latitude and longitude given in 
the labels of the EDR products, and that the values in this table are more 
'correct.' 

#### hires_edr_source_index.csv

A similar index, but for the HIRES mosaic. 

*Note:* There are 162 HIRES mosaic tiles referenced in this index that do not
appear to be in the MttMA. It is possible that these are identifiers retained
from a legacy naming system, or that they refer to tiles discarded during a QA
step prior to archival.

#### edr_index.csv  

Index of all EDR products included in this bundle's data collection, their
paths relative to the bundle root, and the PDS3 product IDs of their source
PDS3 products.

#### edr_metadata_index.csv

This file concatenates metadata indices from the 88 archive volumes of the
PDS3 version of this data set, and also gives the PDS4 LIDs we have assigned 
to the corresponding products in this collection. **WARNING:** Although we
believe that this concatenated index is likely to be very useful, we have not
rigorously validated some of these fields, and some of them do not map
transparently to fields in the PDS4 labels of these products due to
differences in standards. Please use it with caution.

#### duplicate_edr_products.csv  

The PDS3 EDR archive contains 6751 pairs of products with nearly identical
metadata, specifically including identical timestamps. After decompression, we
discovered that the image arrays and histograms of each pair were byte- level
duplicates. We believe that these are duplicate observations inserted into
separate mission-phase series by mistake. We have discarded one image from
each pair. This is an index of which products we discarded and which we
retained.

#### mosaic_tiling_scheme.html, mosaic_tiling_scheme.gif    

The original CD-ROMs for the mosaic data sets contained a variety of
interesting HTML-based tools to help users explore the data. While most are no
longer relevant to this reformatted archive, this is one we thought continued
to serve a purpose. The Clementine basemap, NIR, and UVVIS mosaics share a
tiling scheme, which we have retained in the filenames of the PDS4 versions of
those tiles. (The HIRES mosaic uses the basemap for geometric reference, but
has its own tiling scheme.) This product consists of an HTML document and a
gridded GIF; the HTML document uses a simple JavaScript function to display
the Clementine mosaic tile name of any location on the moon's surface in
response to the movement of a user's mouse over the GIF. We have stripped some
volume-level references and refactored it slightly to conform to modern HTML
and JS standards, and believe that it remains a very useful index to the
mosaic data products. It should work in any major browser, and is also
somewhat interesting to examine as plain text / image.

#### orbit_timeline_booklet.pdf

The PDS3 Clementine EDR data set includes several hundred Excel 95 worksheets
describing important events during each orbit / revolution. They are not in a
straightforward tabular format; they are visually rich and use cell colors,
variable column width, and so on to help make semantic distinctions. The brief
description given for these worksheets explicitly notes their incompatibility
with PDS3 standards, observes that they include many abbreviations and code
names, and promises well-documented versions in a forthcoming ancillary CD-ROM
set accompanying SPICE files. This may refer to the event kernels (EKs) later
released in the data set CLEM1-L-SPICE-6-V1.0 (currently held by NAIF).
However, these EKs appear to only incompletely incorporate the contents of
these worksheets. Because there is no complete documentation, we were unable
to find a good way to translate them into  PDS4-compliant tables. Moreover,
these were working mission documents, and their specific visual presentation
is of at least historical interest. We have therefore simply converted these
spreadsheets to PDF/A and bundled them into a ~ 1000-page booklet. 

----

### /legacy

This subdirectory contains files that are in some sense *entirely* deprecated 
in the PDS4 version of this archive, but which we felt should be retained in
order to help users identify the sources of anomalies that may have been 
migrated into this bundle or unintentionally produced in our migration
process.

#### basemap_pds3_errata.txt

Final version (from volume CL_3015) of the Clementine basemap errata. Some
errors and anomalies discussed in this document are corrected or rendered
irrelevant by this PDS4 bundle. However, some are likely completely
uncorrectable, some were beyond the scope of this  migration effort, and some
may have been unintentionally propagated into this bundle, so this document
remains useful for anyone attempting to trace anomalies in the basemap data.

#### edr_pds3_errata.txt

The same, but for the EDR. (This is the final version, from CL_0088.)

#### hires_pds3_errata.txt

The same, but for the HIRES mosaic. (All versions of these errata are the same
aside from minor formatting differences.)

#### nir_pds3_errata.txt

The same, but for the NIR mosaic.

#### uvvis_pds3_errata.txt

The same, but for the UVVIS mosaic.

#### edr_pds3_arcsis.txt

Archive SIS (Software Interface Specification) for the PDS3 version of the
Clementine EDR data set. Please note that this document is totally deprecated
in the sense that this bundle does not follow the filesystem scheme, volume
structure, or naming conventions of that archive.

#### clemdcmp.txt

Brief description of the PCDOS version of the CLEMDCMP software developed by
Tracie Sucharski at USGS. This software was designed to decompress and
reformat Clementine EDR files in the bespoke JPEG-like discrete cosine
transform compression format used onboard the spacecraft. This is the version
of the software we used to decompress the Clementine EDR files prior to
reformatting them as FITS. We have not included the executable itself in this
bundle.