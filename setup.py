from setuptools import setup

setup(name='citationweb',
      version='0.1',
      description='A little tool to go through a BibDesk library file, extract citations from the attached PDF files and create a network of citations.',
      url='',
      author='Yunus Sevinchan',
      author_email='yunussevinchan@gmail.com',
      license='',
      packages=['citationweb'],
      install_requires=['pypdf2', 'pybtex'],
      dependency_links=[
        'https://github.com/CrossRef/pdfextract', # is a ruby gem
        'https://git.skewed.de/count0/graph-tool', # has to be built
      ],
      zip_safe=False)
