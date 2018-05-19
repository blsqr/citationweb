[![Coverage Status](https://coveralls.io/repos/github/blusquare/citationweb/badge.svg?branch=master)](https://coveralls.io/github/blusquare/citationweb?branch=master)

# What is this?
`citationweb` is a collection of Python tools to analyse a BibTeX bibliography, add citations from linked PDF files and visualise the resulting citation network structure.

**Note:** As this is still a very early version, this toolkit is still very specific to a setup where BibDesk (Mac) manages the `.bib` bibliography file and adjusted to my personal needs – this might or might not change in the future.

# External Requirements
### `pdf-extract`
This is used for extracting citations from pdf files. In my setup, this always had to be installed manually using `gem build pdf-extract.gemspec` followed by `gem install pdf-extract-0.1.1.gem`

### `graph-tool`
The network analysis is performed with the `graph-tool` package. The easiest way to install this is using `brew install graph-tool --with-python3`, which takes a while but usually works.

*(Note, that — to my knowledge — this does not work with your Anaconda Python and you might need a brew python3...)*
