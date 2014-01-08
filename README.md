running-prcp
============

This project contains a script to compute running totals for observerd
precipitation and normal precipitation from GHCN daily data.  It reads
files like "USC00010008.dly" (observed data) and
"USC00010008.normals.txt" (normals data) and generates .dat files
containing running totals.

(.dat is not an official file format; it is simply a format I adopted
for storing data in a way that is convenient for use by the NEMAC
climate explorer project.)
