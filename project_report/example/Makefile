all: compile clean

compile:
	pdflatex report.tex
	bibtex report.aux
	pdflatex report.tex
	pdflatex report.tex

clean:
	rm -rf *.log *.aux *.bbl *.blg