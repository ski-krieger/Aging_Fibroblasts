# Aging_Fibroblasts
This accompanies the paper 'Inference and validation of causal genetic interactions in aging human fibroblasts' by Krieger et al.

This codebase was assembled and run in an environment corresponding to the Dockerfile in root, on a virtual machine configured as AWS r5.8xlarge (32 cores / 256 GB RAM), and when runtimes are documented, they correspond to these specs. 

To simplify the data storage, all necessary data -- including scRNA (which is also stored on GEO) and CellPaint data -- are stored in a fractured, compressed form on a CloudFront server. TO RETRIEVE THE DATA****::::

The codebase is split into two Jupyter notebooks, in an attempt to keep this as easily accessible as possible. ReplicateFigures.ipynb replicates every main-text figure in the paper (excluding those that are schematics, which are usually drawn in Inkscape). DemonstrateKeyMethods.ipynb walks through many of the steps necessary to derive key results in the paper.
