# Aging_Fibroblasts
This accompanies the paper 'Inference and validation of causal genetic interactions in aging human fibroblasts' by Krieger et al.

This codebase was assembled and run in an environment corresponding to the Dockerfile in root, on a virtual machine configured as AWS r5.8xlarge (32 cores / 256 GB RAM), and when runtimes are documented, they correspond to these specs. 

## The Environment

The attached Dockerfile can be used to build a Docker image -- if this is unfamiliar, looking at the file will give the precise package versions needed for the code to run. I have frozen the package versions in place, so this repo should still work far into the future. 

## The Data
To simplify the data storage, all necessary data (around 70Gb) -- including scRNA (which is also stored on GEO) and CellPaint data -- are stored in a fractured, compressed form on a CloudFront server. To retrieve the data, navigate to this directory (after cloning this repo) and run

wget --recursive --no-parent https://d2kdv10sfptp7t.cloudfront.net/

This should make a subdirectory with the (fractured) data. To recombine the chunks, navigate to the subdirectory and run

python combine_pkl.py

The subdirectory should now contain two .pkl files, DataDict.pkl and MethodsDataDict.pkl. Either migrate these to this main directory, or make a one-line edit in the Jupyter notebooks so the appropriate pkl file loads into the appropriate notebook.

## The Notebooks

The codebase is split into two Jupyter notebooks, in an attempt to keep this as easily accessible as possible. ReplicateFigures.ipynb replicates every main-text figure in the paper (excluding those that are schematics, which are usually drawn in Inkscape). DemonstrateKeyMethods.ipynb walks through many of the steps necessary to derive key results in the paper.
