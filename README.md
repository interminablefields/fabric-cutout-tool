# fabric-cutout-tool
This tool helps measure and extract usable fabric space from a photo with cutouts.

## program description
Given a photo of a piece of fabric, this program will:
* segment the fabric from its background
* segment the cutout shapes within the fabric
* bound each cutout in a minimum-area rectangle
* save out two 4-channel PNGs: one with the original cutouts removed, one with the minimum-area rectangles¹ removed.
* save out a CSV containing millimeter dimension information for the fabric, boxes, etc.

Sample source and result files are available in the `images/` folder.

## usage
1. place a coin (default nickel) on the fabric.
2. take a bird's-eye picture of the fabric with the coin clearly visible. AI-generated example provided.
3. edit the constants at the top of the file with the desired source and destination file locations.
4. if not already installed, install `opencv-python`
5. run `python3 extract.py`

------
1. The minimum area rectangle represents the smallest possible rotated rectangle that fully encloses a given shape.
