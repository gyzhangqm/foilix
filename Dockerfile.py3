FROM continuumio/miniconda3:4.4.10

MAINTAINER Guillaume Florent <florentsailing@gmail.com>

RUN conda install -y numpy scipy matplotlib pyqtgraph wxpython pyqt atom configobj pytest
RUN conda install -y -c gflorent corelib hydro libra

# foilix
WORKDIR /opt
# ADD https://api.github.com/repos/guillaume-florent/foilix/git/refs/heads/master version.json
RUN git clone --depth=1 https://github.com/guillaume-florent/foilix
WORKDIR /opt/foilix
RUN python setup.py install