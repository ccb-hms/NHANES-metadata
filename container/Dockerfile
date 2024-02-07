#
# Container image for CCB's NHANES metadata project
# Author: Jason Payne (based on Sam Pullman and Nathan Palmer's code)
# Copyright: Harvard Medical School
#
#
# docker build --progress plain --tag nhanes-metadata-workbench -f container/Dockerfile .
# docker \
#     run \
#         --rm \
#         --name nhanes-metadata-workbench \
#         -d \
#         -v LOCAL_DIRECTORY:/HostData \
#         nhanes-metadata-workbench

FROM rocker/binder:4.3.2

#------------------------------------------------------------------------------
# Basic initial system configuration
#------------------------------------------------------------------------------

USER root

# install standard Ubuntu Server packages
RUN yes | unminimize

# we're going to create a non-root user at runtime and give the user sudo
RUN apt-get update && \
	apt-get -y install sudo \
	&& echo "Set disable_coredump false" >> /etc/sudo.conf
	
# set locale info
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
	&& apt-get update && apt-get install -y locales \
	&& locale-gen en_US.utf8 \
	&& /usr/sbin/update-locale LANG=en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV TZ=America/New_York

WORKDIR /tmp

#------------------------------------------------------------------------------
# Install system tools and libraries via apt
#------------------------------------------------------------------------------

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
	&& apt-get install \
		-y \
		ca-certificates \
		curl \
		less \
		libgomp1 \
		libpango-1.0-0 \
		libxt6 \
		libsm6 \
		make \
		texinfo \
		libtiff-dev \
		libpng-dev \
		libicu-dev \
		libpcre3 \
		libpcre3-dev \
		libbz2-dev \
		liblzma-dev \
		gcc \
		g++ \
		openjdk-8-jre \
		openjdk-8-jdk \
		gfortran \
		libreadline-dev \
		libx11-dev \
		libcurl4-openssl-dev \ 
		libssl-dev \
		libxml2-dev \
		wget \
		libtinfo5 \
		openssh-server \
		ssh \
		xterm \
		xauth \
		screen \
		tmux \
		git \
		libgit2-dev \
		nano \
		emacs \
		vim \
		man-db \
		zsh \
		unixodbc \
		unixodbc-dev \
		gnupg \
		krb5-user \
		python3-dev \
		python3 \ 
		python3-pip \
		alien \
		libaio1 \
		pkg-config \ 
		libkrb5-dev \
		unzip \
		cifs-utils \
		lsof \
		libnlopt-dev \
		libopenblas-openmp-dev \
		libpcre2-dev \
		systemd \
		libcairo2-dev \
		libharfbuzz-dev \
		libfribidi-dev \
		cmake \
		qpdf \
	&& rm -rf /var/lib/apt/lists/*


#------------------------------------------------------------------------------
# Install basic R packages
#------------------------------------------------------------------------------

# use the remotes package to manage installations
RUN Rscript -e "install.packages('remotes')"

# configure and install rJava
RUN R CMD javareconf
RUN Rscript -e "remotes::install_cran('rJava', type='source')"

# install devtools
RUN Rscript -e "remotes::install_cran('devtools')"

#----------------------------------------------------------------------------------------------------
# install standard data science and bioinformatics packages
RUN Rscript -e "remotes::install_cran('Rcpp')"
RUN Rscript -e "remotes::install_cran('roxygen2')"
RUN Rscript -e "remotes::install_cran('tidyverse')"
RUN Rscript -e "remotes::install_cran('git2r')"
RUN Rscript -e "remotes::install_cran('getPass')"
RUN Rscript -e "remotes::install_cran('xlsx')"
RUN Rscript -e "remotes::install_cran('data.table')"
RUN Rscript -e "remotes::install_cran('dplyr')"
RUN Rscript -e "remotes::install_cran('forestplot')"
RUN Rscript -e "remotes::install_cran('splines')"
RUN Rscript -e "remotes::install_cran('tidyr')"
RUN Rscript -e "remotes::install_cran('stringr')"
RUN Rscript -e "remotes::install_cran('survival')"
RUN Rscript -e "remotes::install_cran('codetools')"
RUN Rscript -e "remotes::install_cran('glmnet')"
RUN Rscript -e "remotes::install_cran('glmpath')"
RUN Rscript -e "remotes::install_cran('testthat')"
RUN Rscript -e "remotes::install_cran('DBI')"
RUN Rscript -e "remotes::install_cran('odbc')"
RUN Rscript -e "remotes::install_cran('readr')"
RUN Rscript -e "remotes::install_cran('kableExtra')"
RUN Rscript -e "remotes::install_cran('plotROC')"
RUN Rscript -e "remotes::install_cran('sjPlot')"
RUN Rscript -e "remotes::install_cran('survey')"
RUN Rscript -e "remotes::install_cran('mitools')"
RUN Rscript -e "remotes::install_cran('tinytex')"
RUN Rscript -e "remotes::install_cran('bookdown')"
RUN Rscript -e "remotes::install_cran('reshape')"
RUN Rscript -e "remotes::install_cran('lme4')"
RUN Rscript -e "remotes::install_cran('survminer')"
RUN Rscript -e "remotes::install_cran('rvest')"

# # -- vanilla because there is a bug that causes the R intro / preamble text to get pushed into the compiler
# RUN Rscript --vanilla -e "remotes::install_cran('lme4', repos='"$R_REPOSITORY"')"
# RUN Rscript --vanilla -e "remotes::install_cran('survminer', repos='"$R_REPOSITORY"')"

# install R packages for connecting to SQL Server and working with resulting data sets
RUN Rscript -e "devtools::install_github('https://github.com/nathan-palmer/FactToCube.git', ref='v1.0.0')"
RUN Rscript -e "devtools::install_github('https://github.com/nathan-palmer/MsSqlTools.git', ref='v1.0.0')"
RUN Rscript -e "devtools::install_github('https://github.com/nathan-palmer/SqlTools.git', ref='v1.0.0')"

# additional packages for NHANES analyses
RUN Rscript -e "remotes::install_cran('broom')"
RUN Rscript -e "remotes::install_cran('Hmisc')"
RUN Rscript -e "remotes::install_cran('nonnest2')"
RUN Rscript -e "remotes::install_cran('reshape2')"
RUN Rscript -e "remotes::install_cran('jsonlite')"
RUN Rscript -e "remotes::install_cran('viridis')"
RUN Rscript -e "remotes::install_cran('optparse')"

# # need old version of rvest in order for the hack that parses URLs to work in the NHANES download script
# RUN Rscript -e "remove.packages('rvest')"
# RUN Rscript -e "remotes::install_cran('rvest', repos='https://packagemanager.posit.co/cran/__linux__/focal/2021-01-29')"

#install nhanesA and phonto from github in order to have the latest version (CRAN will take a while to update)
RUN Rscript -e "devtools::install_github('ccb-hms/phonto')"
RUN Rscript -e "devtools::install_github('cjendres1/nhanes@97f1850')"

# ------------------------------------------------------------------------------
# NHANES-metadata Creation Process 
# ------------------------------------------------------------------------------
RUN python3.9 -m pip install pydantic==1.7
RUN python3.9 -m pip install pandas==2.0.2
RUN python3.9 -m pip install Owlready2==0.40
RUN python3.9 -m pip install text2term==2.3.2

WORKDIR /tmp/NHANES-metadata/code

RUN python3.9 generate_ontology_tables.py
RUN python3.9 generate_ontology_mappings.py
RUN python3.9 generate_nhanes_mapping_report.py