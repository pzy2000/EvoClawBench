BSTINPUTS := ./acl-style-files:
export BSTINPUTS

all: main.pdf

main.pdf: main.tex references.bib acl-style-files/acl.sty acl-style-files/acl_natbib.bst
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
	pdflatex -interaction=nonstopmode main.tex
	pdflatex -interaction=nonstopmode main.tex

clean:
	rm -f main.aux main.bbl main.blg main.log main.out main.pdf main.synctex.gz

.PHONY: all clean
