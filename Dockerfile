FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Build tools + headers, in case any package (e.g. igraph, lxml) needs to
# compile from source rather than pull a prebuilt wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir \
    jupyterlab==3.4.4 \
    anndata==0.8.0 \
    cnsplots==0.2.0 \
    colour==0.1.5 \
    datashader==0.16.3 \
    gensim==3.6.0 \
    gravis==0.1.0 \
    holoviews==1.19.1 \
    igraph==0.10.8 \
    ipython==8.18.1 \
    lxml==5.2.2 \
    matplotlib==3.7.1 \
    networkx==3.2.1 \
    nodevectors==0.1.23 \
    numba==0.60.0 \
    numpy==1.24.2 \
    pandas==2.0.0 \
    scanpy==1.9.5 \
    scikit-learn==1.2.2 \
    scipy==1.10.1 \
    seaborn==0.12.2

WORKDIR /code
COPY . /code

EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]