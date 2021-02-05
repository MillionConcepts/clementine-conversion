# clementine pds3 -> pds4 conversion software repository

## introduction

This repository contains software and ancillary materials used to translate
and modernize imaging data and metadata from the Deep Space Science Experiment's
Clementine-1 Orbiter ("Clementine"). This conversion effort specifically
included the five PDS3 data sets originally collected in the "Mission to
the Moon" archive (MttMA) Volume Series and currently held by the Planetary
Data System (PDS) Imaging Node (IMG):

* CLEM1-L/E/Y-A/B/U/H/L/N-2-EDR-V1.0 (raw / EDR data)
* CLEM1-L-U-5-DIM-BASEMAP-V1.0 (single-band 'basemap' mosaic based on images 
taken using the Ultraviolet/Visible Camera (UVVIS)'s 750-nm filter)
* CLEM1-L-U-5-DIM-UVVIS-V1.0 (multispectral mosaic from UVVIS)
* CLEM1-L-N-5-DIM-NIR-V1.0 (multispectral mosaic from the Near-Infrared Camera (NIR))
* CLEM1-L-H-5-DIM-MOSAIC-V1.0 (single-band 'strip' mosaic generated from
images taken using the High-Resolution Camera (HIRES)'s 750-nm
filter)

**All contents of this repository should be regarded with skepticism. The 
products they were used to produce have not yet been reviewed by the PDS.
We will do our best to update this repository to reflect the results of PDS
peer review, but it should currently be regarded as preliminary.**

### purpose of this repository

This software is intended basically as an extension of the documentation
provided in the bundle. We consider this form of software-as-documentation
essential for understanding scientific data.<sup>[1](#footnote1)</sup> 
Because the PDS does not archive software<sup>[2](#footnote2)</sup> other than
source code narrowly intended to describe a particular algorithm (which this
is not), we have placed this repository on GitHub. It contains files necessary
to understand, replicate, correct, and modify most of our process of
converting these PDS3 data sets into a PDS4 bundle.

For this reason, we strongly recommend that anyone who produces new versions
of the Clementine Imaging Bundle publicly available also modify or fork this
repository -- or at least clearly document what happened to the data products
after they were processed by the software in this repository. Otherwise, this
repository will no longer be useful documentation; it could even become
misleading.

### tips for use

* We recommend using the Anaconda distribution of Python and creating a
```conda``` environment using the provided
[environment.yml](/src/environment.yml) file. 
* Using this code to decompress Clementine EDR products in CLEM-JPEG format 
requires [DOSBOX](https://www.dosbox.com/). Also, while the [PDS4 Validate
Tool](https://nasa-pds.github.io/validate/) is not required to perform the
conversion process, we recommend that users have a copy on hand.
* This software will work on macOS or Linux. We recommend that Windows users use
[Windows Subsystem for Linux](https://ubuntu.com/wsl), a virtualized Linux
environment produced by Microsoft.
* One index file used by the software is not included in this repository 
because it is too large to be stored on GitHub. In lieu of a permanent 
solution, we are currently serving it [from Google Drive](https://drive.google.com/file/d/1cnQ0yCiL7aL0LR-uR3lqU0RWsleKw3_D).
After decompression, place it in /src/clementine/directories.
* This is not, and is not intended to be, a ready-to-go installable application
or general-purpose library. Users will likely need to make modifications for
their individual working environments. In some cases, notes on this are
included in comments or text blocks in individual files. 
 * This software has *absolutely not been tested with any users other than 
ourselves.* We are happy to provide advice, to receive bug reports on issues 
that may have resulted during software export and transcription that render 
it unusable for persons other than ourselves, and *especially* happy to receive 
reports on software behavior that may have mangled output data or metadata. 
Please file GitHub issues.

### what this repository is not / limitations of this repository

This repository is not a mirror of the output PDS4 bundle. The bundle is
several hundred gigabytes in volume and contains over 10 million files; GitHub
is not an appropriate platform from which to serve the archive. Users who
simply wish to access data in the bundle should go to IMG's servers: **TODO:
LINK GOES HERE WHEN LIVE.**  Similarly, this repository is not a mirror of the
input PDS3 data sets. PDS3 products to use this software on
can be found on [volumes CL_0001 through CL_6022 in this
directory](https://pds-imaging.jpl.nasa.gov/data/clementine/), also hosted by
IMG.

It does not exhaustively explain every step of the conversion and labeling
process. This is primarily because much of the process took place manually.
Many products were unique and therefore not subject to systematic processing.
In some cases (such as the basemap polar tiles), the software in this archive
was used in one-off ways to convert these products; notes on most of these
cases are included in code comments. It also does not offer a complete
discursive walkthrough of our thought processes, rationale, workflow, etc. 

It does not contain all peripheral enabling software, like scripts to transfer
/ mirror the archive, name directories, and so on. These scripts are highly 
environment-specific and were often subject to manual adjustment; they would
not be useful additions to this repository. Similarly, a small number of
products in the document collection were made using GUI office applications
such as Adobe Acrobat and LibreOffice; it is impossible to include methods to
exactly replicate these processes.

Finally, it does not include the Clementine mission dictionary developed for this
conversion process. This dictionary is currently hosted in [a Million Concepts
GitHub Repository](https://github.com/MillionConcepts/ldd-clementine). **TODO:
ADD LINK TO OFFICIAL VERSION WHEN PUBLISHED**

## directory of contents

### /readmes

Copies of our readme files from the bundle to provide context for this
software. The data and browse readmes can be considered informal  
specifications for the outputs of this software.

### /src

Jupyter Notebooks and enabling Python modules for producing new versions of 
the Clementine data and metadata. More details are included in comments or 
Markdown cells within these modules and notebooks.

### /src/clemdcmp

CLEMDCMP.EXE, Tracie Sucharski's '90s Clementine EDR Swiss Army knife. Used 
to decompress Clementine EDR files from CLEM-JPEG format prior to conversion
to FITS.

### /src/directories

File indices used to help organize and generate files and metadata.

### /src/labels/clementine and subdirectories

Includes:
1. Templates used by ```converter.py``` and related modules to produce PDS4 labels.
2. A selection of individual labels, documentation and browse products from the bundle. 
Not a complete mirror of those collections; included for context.

### /src/pdr and subdirectories

A 'frozen' alpha fork of [```pdr```](https://github.com/MillionConcepts/pdr) 
specially modified for this project.

## other notes

### cautions on reuse of this software

You can do almost anything with this software that you like, subject only  to
the extremely permissive terms of the [BSD 3-Clause License](LICENSE).
However, we recommend that you be very careful about doing so. All  of this
software should be considered special-purpose, intended specifically  to work
with the products in the Clementine imaging bundle. In particular, it includes
'frozen' alpha forks of some currently-available and forthcoming software
projects, including [```pdr```](https://github.com/MillionConcepts/pdr) and
its  submodule ```pdr.converter```. We strongly recommend that the release or
primary development versions of included software be used in preference to the
contents of this repository for any other projects. Versions here have been
modified and evaluated specifically to work on these data sets **and may be
catastrophically unsuitable for any other purpose.**

Some of this software may serve as separable utilities for purposes other than
converting versions of the products in these data sets, of course. If you find
useful nuggets or patterns, we are very happy for you. However, in general, we
recommend great caution if using it for applications outside of its intended
purpose.

### style 

These modules were designed to be used to quickly diagnose and correct
problems in processes that had never before been performed. They are optimized
to be rapidly 'messed with' and modified in REPL  environments. They are
highly verbose, often use ```print()``` rather than or in addition to loggers,
have Jupyter Notebooks rather than non-interactive execution scripts, and so
on. Should you decide to convert the Clementine PDS3 archive to PDS4 several
dozen times in a row, we recommend making different style decisions.

Also note that the notebooks here present only an example of how the 
conversion software might be used to iterate over the PDS3 archive, perhaps in 
parallel. These procedural execution steps should not be considered 'canonical' 
(unless they missed or duplicated some products!) If you repeat or modify this process, 
we encourage you to optimize it in the way that makes most sense for your
operating environment. We often like running a bunch of notebooks in parallel
as "bulkheads": they silo points of failure in a large, slow process operating
on not-yet-fully understood data. Bugs can be fixed without interrupting the whole
shebang.<sup>[3](#footnote3)</sup>

We have some additional notes on performance considerations in some notebooks.

## authorship and acknowledgments

The contents of this repository were produced by [Million Concepts,
LLC](https://www.millionconcepts.com) under contract from the United States Geological
Survey. This document, along with most of the software and other materials in
this repository, was written by Michael St. Clair. ```pdr``` was created by
Chase Million and predates this project, although some  portions of the fork
included in this repository were specifically written by Chase and Michael for
this project. Adam Ianno also made significant contributions to this project.

This software relies on too much other software to individually cite it all,
but we would like to specifically call attention to:

* the PlanetaryPy project, especially Ross Beyer's [```pvl```](https://github.com/planetarypy/pvl)
* [GDAL](https://github.com/OSGeo/gdal/blob/master/CITATION), particularly the 
PDS3 driver written by Trent Hare and Robert Soricone, the PDS4 driver written 
by Even Rouault, and the GeoTiff driver written by Frank Warmerdam
* [NumPy](https://www.numpy.org)
* [AstroPy](https://github.com/astropy/)
* [Pandas](https://pandas.pydata.org/)
* Tracie Sucharski's [CLEMDCMP](https://pds-imaging.jpl.nasa.gov/data/clementine/cl_0088/software/pcdos/)

----

<a name="footnote1">1</a>: The Astrophysics Source Code Library provides [an
excellent bibliography of references](https://ascl.net/home/getwp/676) on
scientific software transmission and preservation. Alexandra Chassanoff and
Micah Altman's concept of ["curation as interoperability with the
future"](https://dspace.mit.edu/handle/1721.1/125435) is especially relevant
to our effort here.

<a name="footnote2">2</a>: See ["Policy on Software Archiving", PDS Management
 Council,
2016.](https://pds.nasa.gov/datastandards/documents/policy/SoftwareArchivingPosition06082016.pdf)
The PDS3 Clementine archive itself provides an interesting historical example
of a radically different philosophy towards the relationship of software to
scientific data archival. It is not an archive that includes software, it is
an archive built around software: every individual volume was an optical disk
that included software necessary to view and/or decompress the included data
products. It is still a pleasure to browse these [cleanly-built hypertext
documents](https://pds-imaging.jpl.nasa.gov/data/clementine/cl_5004/browse/brratio.htm),
which are in certain ways easier and quicker to navigate -- albeit far 
less powerful -- than modern tools like the Lunar Orbital Data Explorer.
It is less a pleasure to manipulate raw data in bespoke formats using decades-old, 
unmaintained software.

<a name="footnote3">3</a>: Erlang would probably be good for this.
