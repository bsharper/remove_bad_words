#!/bin/env python
import os
import sys
import argparse

banner_width = 40
if 'BANNER_WIDTH' in os.environ.keys():
    banner_width = os.environ['BANNER_WIDTH']

parser = argparse.ArgumentParser(description="Prints a simple banner for multi-step scripts")
parser.add_argument('-c', '--center', help='Center text or not', action='store_true')
parser.add_argument('-w', '--width', default=banner_width, help='How wide to print the banner', type=int)
parser.add_argument('text', help='Text to print')
parser.add_argument('divider', help='Single character to use to create divider', default="=", nargs='?')
args = parser.parse_args()

divider = args.divider 
width = args.width
text = args.text
center = args.center

print (str(divider)*width)
if center:
    print (text.center(width))
else:
    print (text)
print (divider*width)
