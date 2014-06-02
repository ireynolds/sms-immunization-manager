# In order to make the bibliography, you must, at minimum
# * Uncomment the call to bibtext below
#
# In order to make the app at all, run
#   sudo apt-get install tex-live zip -y
#

all: 
	make clean
	make compile
	make clean
	make package

clean:
	# Does not clean the report.zip or report.pdf
	rm -rf *.log *.aux *.bbl *.blg

compile:
	pdflatex report.tex
	bibtex report.aux
	pdflatex report.tex
	pdflatex report.tex

package:
	rm -rf report.zip
	zip -r report.zip report.pdf appendices/ README 