FROM jupyter/minimal-notebook

USER root

RUN apt-get update && apt-get install -y gcc
RUN conda install nodejs
RUN sudo /opt/conda/bin/npm install -g ijavascript
RUN ijsinstall

USER $NB_UID