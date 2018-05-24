[![Build Status](https://travis-ci.org/blusquare/citationweb.svg?branch=master)](https://travis-ci.org/blusquare/citationweb)
[![Coverage Status](https://coveralls.io/repos/github/blusquare/citationweb/badge.svg?branch=master)](https://coveralls.io/github/blusquare/citationweb?branch=master)

_This README is very much WIP_

# What is this?
`citationweb` is a collection of Python tools to analyse a BibTeX bibliography, add citations from linked PDF files and visualise the resulting citation network structure.


## Installation
Before installing, make sure you have a supported Python3 version.

To install citationweb, simply use pip:
```
pip3 install git+https://github.com/blusquare/citationweb.git
```

#### For developers
If you desire to develop, create a new virtual environment, clone the code, then install using pip and including the testing dependencies:
```
git clone https://github.com/blusquare/citationweb.git
pip install citationweb/.[test_deps]
```

### Other dependencies
To extract references from PDFs, the very powerful (but unfortunately: retired) [`pdf-extract`](https://github.com/Crossref/pdfextract) is used.

Install it via:
```
gem install pdf-extract
```


## Usage
_TODO_
