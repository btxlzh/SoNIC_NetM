#!/bin/sh
# $1 as input file
# $2 as output pdf file
gnuplot << EOF
set terminal postscript eps size 4.5,3 enhanced color font 'Helvetica,20' linewidth 2
#set terminal postscript eps color enhanced "Time" linewidth 4 rounded fontscale 1.0
# Note you need gnuplot 4.4 for the pdfcairo terminal.
#
#set terminal pdfcairo font "Gill Sans,9" linewidth 3 rounded fontscale 0.8 
#
# Line style for axes
set style line 80 lt rgb "#808080"

# Line style for grid
set style line 81 lt 0  # dashed
set style line 81 lt rgb "#808080"  # grey

set grid back linestyle 81
set border 3 back linestyle 80 # Remove border on top and right.  These
# borders are useless and make it harder
# to see plotted lines near the border.
# Also, put it in grey; no need for so much emphasis on a border.
set xtics nomirror
set ytics nomirror

#set log x
#set mxtics 10    # Makes logscale look good.

# Line styles: try to pick pleasing colors, rather
# than strictly primary colors or hard-to-see colors
# like gnuplot's default yellow.  Make the lines thick
# so they're easy to see in small plots in papers.
set style line 1 lt rgb "#A00000" lw 2 pt 1
set style line 2 lt rgb "#00A000" lw 2 pt 2 
set style line 3 lt rgb "#5060D0" lw 2 pt 3 
set style line 4 lt rgb "#F25900" lw 2 pt 4
set style line 5 lt rgb "#006400" lw 2 pt 5
set style line 6 lt rgb "#8B0000" lw 2 pt 6
set style line 7 lt rgb "#483D8B" lw 2 pt 7
set style line 8 lt rgb "#FFD700" lw 2 pt 8
set style line 9 lt rgb "#FF69B4" lw 2 pt 9

set xlabel "Probe Rate(Gbps)"
set ylabel "Queuing Delay Variance"

set key top right

set xrange [0:10]

set yrange [-10:23000]
set output "result.eps"
plot \
   "tmp" using 1:9 w p lt 3 ps 0.5 pt 6 title ""


EOF
