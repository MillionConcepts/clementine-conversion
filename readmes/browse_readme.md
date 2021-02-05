# Clementine Imaging Browse Collection README file

This is a brief introduction to the browse collection for this bundle. This
collection precisely follows the directory structure and file naming
convention of this bundle's data collection; please refer to
/data/data_readme.md for a description of these conventions. This gives a
brief overview of the format of the individual browse products.

Each image in this bundle is a separate browse product with its own detached
.xml label; this label shares a base filename with the image file. We will not
discuss these labels separately.

## EDR

Every EDR product has one associated browse image:

```(observational product id)_browse.jpg```

This is a compressed representation of the associated EDR FITS image. We made 
these by JPEG-compressing the FITS images at full resolution and 90 quality
using the Python Imaging Library.

## basemap

Every basemap product (except for the geometry products) has one associated
browse image:

```(observational product id)_browse.jpg```

This is simply a compressed representation of the single-band mosaic
tile. These files were taken from the PDS3 archive; they are the largest-
available browse images from that archive.

## UVVIS

Browse images for this mosaic come in three flavors: 

```(observational product id)_bw.jpg``` (black-and-white)

```(observational product id)_ratio.jpg``` (color-ratio)

```(observational product id)_color.jpg``` ('enhanced' false color)

'bw' images are based on the UVVIS camera's 750-nm 'B' filter. 'ratio' images
use the ratio of 415 nm / 750 nm for their blue channel, the ratio of 750 nm /
950 nm for green, and the the ratio of 750 nm / 415 nm for red. 'color' images
use the value of 415 nm for their blue channel, 750 nm for green, and 950 nm
for red. These files were taken from the PDS3 archive; they are the largest-
available browse images from that archive.

The phase maps have no browse images.


## NIR 

Browse images for this mosaic also come in three flavors: 

```(observational product id)_bw.jpg``` (black-and-white)

```(observational product id)_ratio.jpg``` (color-ratio)

```(observational product id)_color.jpg``` ('enhanced' false color)

'bw' images are based on the NIR camera's 2000-nm 'D' filter. 'ratio' images
use the ratio of 1500 nm / 1100 nm for their blue channel, the ratio of 1500
nm / 2000 nm for green, and the unmodified value of 1500 for red. 'color'
images use the value of 1100 nm for their blue channel, 1500 nm for green, and
2000 nm for red. These files were taken from the PDS3 archive; they are the
largest- available browse images from that archive.

## HIRES

Every HIRES product has one associated browse image:

```(observational product id)_browse.jpg```

This is simply a compressed representation of the single-band mosaic
tile. These files were taken from the PDS3 archive; they are the largest-
available browse images from that archive.