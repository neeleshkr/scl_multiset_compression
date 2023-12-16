# Implementation of Multiset Compression in SCL

Sumer Kohli
Neelesh Ramachandran
Autumn 2023, EE 274 Final Project

### Introduction

In this work, we aim to understand how to utilize bits-back coding to achieve an improved compressionr ratio in a multiset compression setting. A multiset is a generalization of a set that allows for repetition of elements, where the critical information is contained in the elements and not their ordering (equivalently, the frequency map of the elements is what must be preserved.) 

Below, we outline the repository structure to identify where relevant contributory files are located. We also outline steps for reproducing the key figures in our final report.

### Structural Overview
- `scl/compressors/multiset_coder.py` contains a large portion of our technical contribution. It defines the multiset compressor encode and decode functions, the associated helper/secondary compressors, and all of our unit test cases. 
- `scl/compressors/multiset_utils.py` contains the MSBST custom data-structure, and associated functionality. This enables our multiset compressor to efficiently operate with large multiset sizes.

### Instructions to Reproduce Results
For initial SCL setup instructions, please see the [main SCL repository](https://github.com/kedartatwawadi/stanford_compression_library/) from which this project was forked.

To generate the plots in our report, we ran the commands below from the top-level of this repository. In some tests, we may have modified parameters such as number of keys, multiset size, or similar, but these should be readily interpretable from our paper submission.

Any packages or modules that are missing as compared to the base SCL installation (such as `tqdm`) should be readily available via `pip` (for example, `pip install tqdm`).

JSON Compression:
`py.test -s -v scl/compressors/multiset_coder.py -k test_json_map`

JSON Wallclock Runtimes:
`py.test -s -v scl/compressors/multiset_coder.py -k test_json_map_runtime` (distribution of time, and comparison to naive compressor)
`py.test -s -v scl/compressors/multiset_coder.py -k test_json_multiset_runtime` (runtime varying over multiset size)

Alphabet-Size Runtime:
`py.test -s -v scl/compressors/multiset_coder.py -k test_e2e_freq_map`

### Milestone report

Our milestone report, with more detail and broad overview, is at `README_multiset_milestone.md`.