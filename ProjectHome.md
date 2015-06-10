**svg2rlg** is a python tool to convert SVG files to reportlab graphics.

The tool can be used as a console application to convert SVG to PDF files.

Known problems ( AKA todo list):
  * Missing support for elliptical arcs in paths. It is belived to be possible to convert arcs to quadratic beziers.
  * Text handling is limited.
  * Style sheets not supported.

Note that some limitations are due to limitation in the reportlab graphics package:
  * No gradients
  * No text on path
  * No filling rules (only odd-even)

A wxpython tool is included in the distribution which does a
side by side comparison to the SVG test suite. Presently most
of the official SVG 1.1 test suite is prefect.