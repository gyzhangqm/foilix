FROM continuumio/miniconda3:4.4.10

MAINTAINER Guillaume Florent <florentsailing@gmail.com>

RUN apt-get update && apt-get install -y libgtk2.0-0 libxxf86vm1 libgl1-mesa-dev libx11-xcb1 && rm -rf /var/lib/apt/lists/*

RUN conda install -y numpy scipy matplotlib pandas pyqtgraph wxpython pyqt atom configobj pytest
RUN conda install -y -c gflorent corelib hydro libra

# foilix
WORKDIR /opt
# ADD https://api.github.com/repos/guillaume-florent/foilix/git/refs/heads/master version.json
RUN git clone --depth=1 https://github.com/guillaume-florent/foilix
WORKDIR /opt/foilix
RUN python setup.py install

# xfoil executable
RUN apt-get update && apt-get install -y gfortran && rm -rf /var/lib/apt/lists/*
COPY foilix/xfoil/xfoil /opt/conda/lib/python3.6/site-packages/foilix/xfoil/xfoil