#!/usr/bin/env python

# Last modified: November 12, 2016
# Author: Darrick Lee <y.l.darrick@gmail.com>
# This script converts a .tex file into a .html file to be copied into wordpress.
#
# Usage: python latex2wp_nt.py -i texfile.tex
#
# ASSUMPTIONS ABOUT .TEX FILE:
#	1) All standalone equations in \begin{equation} environment. Equations are written in a
#	   single line.
# 	2) There is only text inside the \textbf{} environment.

## IMPORT LIBRARIES ###########################################################
import os
from optparse import OptionParser

## PARSE OPTIONS ##############################################################
parser = OptionParser()
parser.add_option("-i", action="store", type="string", dest="texFile", help="Input .tex file", metavar="TEXFILE")

(options, args) = parser.parse_args()
texFileName = options.texFile

## COMMON HTML TAGS ###########################################################
pText = '<p style=\"font-size:15px;\">';
eqText = '<p align=center>'
defText = '<div style=\"border:2px;border-style:solid;border-color:#000000;padding:.7em;font-size:15px;margin-bottom:1em;\">'
olText = '<ol style=\"margin-top:1em;margin-bottom:1em;\">';
ulText = '<ul style=\"margin-top:1em;margin-bottom:1em;\">';
secText = '<p style=\"font-size:20px;\"> <strong>';
ssecText = '<p style=\"font-size:18px;\"> <strong>';

## HELPER FUNCTIONS ###########################################################
# find_all: This function finds the starting indices of substrings in a_str
def find_all(a_str, sub):
	start = 0;
	index_list = list();
	while True:
		start = a_str.find(sub, start);
		if start == -1: return index_list;
		index_list.append(start);
		start += len(sub);

# parse_textbf: This function converts all \textbf{-} statements into <	strong>-</strong>
def parse_textbf(a_str):
	# Find all instances of '\textbf{'
	tbf_list = find_all(a_str, '\\textbf{');

	# Replace each instance of \textbf{} with <strong> tags
	# Work in reverse order to avoid indices messing up
	for tbf in reversed(tbf_list):
		r_brac = a_str.find('}', tbf); # find the first instance of } after the \textbf{}
		text_string = a_str[tbf+8:r_brac]; # the string with only the text
		strong_string = ('<strong>' + text_string + '</strong>'); # the replacement string with <strong> tags
		a_str = a_str[0:tbf] + strong_string + a_str[r_brac+1:]; # replace the textbf string with the strong string

	return a_str;

# replace_shortcuts: This function replaces all shortcuts with their specified words
def replace_shortcuts(a_str, shortcut_key, shortcut_word):
	for (key, word) in zip(shortcut_key, shortcut_word):
		a_str = a_str.replace(key, word);

	return a_str;

## INITIALIZE FILES ###########################################################
# Generate .html output name
htmlFileName = os.path.splitext(texFileName)[0] + '.txt'
	 
# Load in the .tex file and .html file
tex = open(texFileName, 'r');
html = open(htmlFileName, 'w');

## PROCESS PREAMBLE ###########################################################
# Initialize the list of shortcuts
shortcut_key = list();
shortcut_word = list();

# Read lines until \begin{document}
line = tex.readline();
while(line[0:16] != '\\begin{document}'):

	# Add shortcuts to shortcut list
	if(line[0:11] == '\\newcommand'):
		# Find all '{' (l_brac) and '}' (r_brac) elements
		l_brac = find_all(line, '{');
		r_brac = find_all(line, '}');

		shortcut_key.append(line[l_brac[0]+1:r_brac[0]]);
		shortcut_word.append(line[l_brac[1]+1:r_brac[-1]]);
	
	line = tex.readline();

## PROCESS TEXT ###############################################################
def_env = 0; # Flag to determine whether or not we're in the definition environment
list_env = 0; # Flag to determine whether or not we're in a list (either ordered or unordered) environment
item_env = 0; # Flag to say that we're in a line starting with \item
def_count = 1; # Counter to count the number of definitions
line_count = 0; # Count lines, to display to console
sec_num = 0; # Section number
ssec_num = 1; # Subsection number

# Write the date
html.write('<p style=\"font-size:10px;\"> ENTER DATE HERE </p>\n');

# Read lines until \end{document}
line = tex.readline();
line = line.strip(); # remove whitespace at the beginning and end of line
while(line[0:14] != '\\end{document}'):
	print((str(line_count)+ ': ' + str(def_env)));
	# \begin{equation}
	if(line[0:16] == '\\begin{equation}'):
		html.write(eqText); # center the equation
		html.write(' $latex '); # begin latex environment
		line = tex.readline(); # read next line, where equation is stored
		line = replace_shortcuts(line, shortcut_key, shortcut_word); # shortcuts
		line = line.strip();
		html.write(line.strip()); # enter stripped line (no whitespace before and after)
		html.write('$</p>\n'); # end latex environment
		line = tex.readline(); # read next line; this will be \end{equation}
		line = line.strip();

	# \section{...}
	elif(line[0:9] == '\\section{'):
		sec_num += 1; # Increment section number
		html.write(secText); # start ssec environment
		html.write((str(sec_num) + '   '))
		html.write(line[9:-1])
		html.write('</strong></p>\n');
		ssec_num = 1; # Reset subsection number

	# \subsection{...}
	elif(line[0:12] == '\\subsection{'):
		html.write(ssecText); # start ssec environment
		html.write((str(sec_num)+'.'+str(ssec_num)+'   '))
		html.write(line[12:-1])
		html.write('</strong></p>\n');
		ssec_num += 1; # Increment subsection number

	# \begin{definition}
	elif(line[0:18] == '\\begin{definition}'):
		html.write(defText); # create box around definition
		html.write('<strong> Definition ' + str(def_count) + '</strong> '); # definition label
		def_count += 1; # increment definition counter
		def_env = 1; # set flag for definition environment

	# \end{definition}
	elif(line[0:16] == '\\end{definition}'):
		def_env = 0;
		html.write('</div>\n');

	# \begin{enumerate}
	elif(line[0:17] == '\\begin{enumerate}'):
		html.write(olText); # begin ordered list environment
		list_env = 1;

	# \end{enuemrate}
	elif(line[0:15] == '\\end{enumerate}'):
		html.write('</ol>\n'); # end ordered list environment
		list_env = 0;

	# \begin{itemize}
	elif(line[0:15] == '\\begin{itemize}'):
		html.write(ulText); # begin unordered list environment
		list_env = 1;

	# \end{itemize}
	elif(line[0:13] == '\\end{itemize}'):
		html.write('</ul>\n'); # end unordered list environment
		list_env = 0;

	# \[ (the beginning of commutative diagram)
	elif(line[0:2] == '\\['):
		html.write('ENTER COMMUTATIVE DIAGRAM HERE\n'); # placeholder for commutative diagram

		# Continue to read lines until reaching '\]'
		line = tex.readline();
		line = line.strip();
		while(line[0:2] != '\\]'):
			line= tex.readline();
			line = line.strip();

	# \begin{figure}
	elif(line[0:14] == '\\begin{figure}'):
		html.write('ENTER FIGURE HERE\n'); # placeholder for figure

		# Continue to read lines until reaching '\end{figure}'
		line = tex.readline();
		line = line.strip();
		while(line[0:12] != '\\end{figure}'):
			line = tex.readline();
			line = line.strip();

	# Any other text that is not an empty line
	elif(line != ''):
		# check for \item in case we are in the enumerate tex environment
		if(line[0:5] =='\\item'):
			html.write('<li> '); # begin ordered list element
			line = line[6:]; # remove the \item from the line
			line_env = 1;
		elif(def_env == 0):
			html.write(pText);

		# replace bolded text and shortcuts
		line = parse_textbf(line); # bold text
		line = replace_shortcuts(line, shortcut_key, shortcut_word); # shortcuts
		line = line.replace('\\\\', ''); # remove \\ from text

		# replace every other $ with a $latex
		count = 0;
		split_line = line.split('$'); # split line at $

		html_line = ''; # initialize the new line
		# put everything back together, but put $latex at every other $
		for text in split_line:
			if(count == 0):
				html_line += text;
			elif((count%2)==1):
				html_line += ('$latex ' + text);
			else:
				html_line += ('$' + text);

			count += 1;
		html.write(html_line);

		if(def_env == 0):
			html.write('</p>\n');
		elif(list_env == 1):
			html.write('</li>');

	line = tex.readline();
	line = line.strip();
	line_count +=1;

tex.close();
html.close();
