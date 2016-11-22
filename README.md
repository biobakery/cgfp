# **This repository is associated with a paper that is currently under review. Please do not distribute any of the protocols or scripts on this page.**

# A protocol for chemically-guided functional profiling (CGFP) in meta’omics data

----

[TOC]

----

## Authors

* Benjamin J. Levin (<mailto:blevin@fas.harvard.edu>)
* Eric Franzosa

----

## Description

This repository contains a protocol and several scripts to assist users in combining Sequence Similarity Network (SSN) information with ShortBRED output. This approach, called "chemically-guided functional profiling," is useful for studying large protein families in metagenomic and metatranscriptomic datasets.

SSNs are visual tools used to analyze large protein families. SSNs consist of nodes, which represent protein sequences, and edges, which connect nodes that share a sequence identity greater than a user-defined cutoff value. By carefully selecting an edge threshold, a SSN can be used to divide large protein families into putatively isofunctional clusters. Experimental validation is needed to verify that clusters are isofunctional, but a SSN can provide an excellent starting point.

ShortBRED is a method for quantifying the abundance of protein-encoding genes in metagenomes and metatranscriptomes. Given a set of amino acid sequences, ShortBRED first identifies short peptide markers unique to highly similar representative sequences and then quantifies the abundance of these markers in meta’omic datasets.

By combining the knowledge embedded within a SSN with ShortBRED quantification, one can determine the abundances of functionally distinct members of an enzyme superfamily in meta’omic datasets. First, an SSN is constructed for a given protein family of interest (PFOI), with the goal of dividing the family into isofunctional clusters. The abundances of members of the PFOI in meta’omics data are then determined using ShortBRED. Each member of the PFOI is linked to a cluster on the SSN, and so abundance information of entire clusters can be found by summing the abundances of each cluster’s members. Assuming clusters in the SSN are isofunctional, the abundances of particular biochemical functions in microbiomes can be determined.

----

## Citation

If you use the protocol or data files provided here, please cite our the following publication:

TBD

----

## Prerequisites

* **Sequence Similarity Network (SSN) for Protein Family of Interest (PFOI).** SSNs can be generated using Enzyme Function Initiatives-Enzyme Similarity Tool (EFI-EST) at [http://efi.igb.illinois.edu/efi-est/](http://efi.igb.illinois.edu/efi-est/). In addition to tutorial on the EFI-EST website, their online tutorial, see [this review](http://www.dx.doi.org/10.1016/j.bbapap.2015.04.015) for more information on SSN construction. For chemically-guided functional profiling to be successful, SSNs must be well-constructed. Ideally, the clusters within an SSN should be known to represent isofunctional proteins. The code and tutorial below assume that the SSN has been generated from an InterPro family. If another option was used, such as with user-supplied sequences, the general workflow would be identical, but the scripts below would not apply.

* **Cytoscape.** A program used to visualize SSNs. Cytoscape can be downloaded from [www.cytoscape.org](http://www.cytoscape.org). The tools below have been validated with Cytoscape 3.2.1.

* **ShortBRED.** A method to quantify protein families in metagenomes and metatranscriptomes with high specificity. Detailed instructions for installing and running ShortBRED can be found at [https://bitbucket.org/biobakery/shortbred/wiki/Home](https://bitbucket.org/biobakery/shortbred/wiki/Home). For users having issues with installing or running ShortBRED, please direct questions to <mailto:shortbred-users@googlegroups.com>.

* **Background protein reference**. ShortBRED requires a "protein universe" to aid in finding peptide markers for proteins of interest. We recommend UniRef90 for this purpose, [which can be downloaded here](http://www.uniprot.org/help/uniref). UniRef90 is a comprehensive, non-redundant representation of the proteins in UniProt (clustered at 90% amino acid identity).

* **Metagenomes of interest.** User-provided metagenomes and metatranscriptomes can be used in this protocol. Publicly available datasets can be used for this analysis as well. The [Human Microbiome Project](http://hmpdacc.org/HMASM/) has made available hundreds of metagenomes. [MG-RAST](http://metagenomics.anl.gov/) and the [EBI metagenomics database](https://www.ebi.ac.uk/metagenomics/) are additional, excellent resources for acquiring shotgun meta’omic sequencing data for a variety of projects and microbial community types.

* **CGFP scripts.** Two scripts, compatible with Python 2.7+, are required to complete the protocol. [Download those scripts + demo data here](https://bitbucket.org/biobakery/cgfp/get/default.zip). Alternatively, you may directly clone this repository: ``hg clone https://bitbucket.org/biobakery/cgfp``.

----

## Protocol

### Processing an SSN

#### 1. Extracting Data from the SSN

Two tables must be exported from the SSN of interest. The tables of node and edge information can be exported from Cytoscape. Open the SSN of interest and select ``File`` > ``Export`` > ``Table`` and select the node table from the list that appears. Repeat the process, selecting the edge table to obtain both tables (see figure below).

   **ADD FIGURE ONE**

 From these two tables, two additional files need to be generated. We have provided a script that can construct those files: `parse_ssn.py`. This script outputs 1) a list of UniProt accession codes for all sequences on the network and 2) a mapping file to link each node to the cluster it belongs to. The list of accession codes will be used to download the FASTA sequences for all members of the PFOI. The other file, the mapping file, is used to link members of the PFOI to the clusters they belong to. Although the EFI-EST and Cytoscape calculate and illustrate nodes and edges, for our purposes it is more helpful to divide the network into connected components and assign a cluster number to each component. The mapping file links each sequence to the cluster to which it belongs. If the SSN contains isofunctional clusters, then all sequences with the same cluster number (i.e. in the same connected component) correspond to proteins with the same function. 

 The script to generate the accession code list and the mapping file can be run as follows:

```
./scripts/parse_ssn.py $NODES $EDGES -e $N -a $ACCESSION -c $CLUSTERS
```

Where:

* `$NODES` is the nodes table exported from the SSN.

* `$EDGES` is the edges table exported from the SSN.

* `-a $ACCESSION` is the location of the output file containing the UniProt accession codes for all sequences in the network. This flag is optional.

* `-c $CLUSTERS` is the location of the output file containing the cluster mapping file. This flag is optional.

* `-e $N` is an additional edge filter. Instead of forcing users to regenerate a new SSN or remove edges in Cytoscape if the SSN is to be refined (i.e. increase the edge threshold), this flag forces the script to only consider edges connecting nodes sharing greater than _N_% identity. This flag is optional.

 If the SSN was not generated from an InterPro family, this script will not work. A list of accession codes and a cluster mapping file will need to be made manually or with an application-specific script.

----

#### 2. Obtaining FASTA Sequences

The sequences for all of the proteins in the SSN need to be obtained. Using the list of UniProt accession codes obtained in the previous step, sequences can be downloaded easily from [http://www.uniprot.org/uploadlists/](http://www.uniprot.org/uploadlists/). After uploading the list of sequences, confirm that the default options to convert the accession codes (UniProtKB AC/ID) to UniProtKB output and select ``Go`` (see figure below).


 **ADD FIGURE 2**

On the results page, select ``Download`` and download all of the sequences as ``FASTA (canonical)`` (see figure below). Be sure to unzip the file if a compressed version is downloaded.

 **ADD FIGURE 3**

If the SSN was not generated with an InterPro family, the sequence list will need to be constructed either manually or with an application-specific script.

----

### Running ShortBRED

#### 3. Running ShortBRED-Identify

ShortBRED-Identify is used to find markers for similar members of the PFOI. It requires a FASTA file containing all sequences of interest and a reference list, typically UniRef90. Only the list of markers is needed for subsequent analysis, but temporary files should be retained if ShortBRED-Identify needs to be rerun with modified parameters.

A typical ShortBRED-Identify call is provided below. Note that ShortBRED-Identify takes ~100 CPU-hours to find markers for ~1,000 sequences, but the rate-limiting steps are parallelized and can benefit from the use of multiple CPU cores. For a full list of flags, run ``./shortbred_identify.py -h``.

```
./shortbred_identify.py --threads $THREADS --goi $GOIFASTA --ref  $UNIREF90 --markers $MARKERS --tmpdir $TMP
```
 
Where:

* `$THREADS` is the number of threads for ShortBRED to use. This is important when running this script on computational clusters.

* `$GOIFASTA` is the location of a FASTA file containing all of the sequences for proteins on the SSN. This file was generated in Step 2 of this protocol.

* `$UNIREF90` is the location of UniRef90 (see Prerequisites).

* `$MARKERS` is the location of the output marker file generated by ShortBRED.

* `$TMP` is the location for ShortBRED to store temporary files. Some of these files are useful for analysis and troubleshooting and it is recommended they be saved.

----

#### 4. Running ShortBRED-Quantify

ShortBRED-Quantify is run with the markers generated in Step 3 against a user-provided metagenome (or metatranscriptome). A typical ShortBRED-Quantify call is provided below. This script will need to be run for each metagenome of interest. For a full list of flags, run ``./shortbred_quantify.py -h``.

```
./shortbred_quantify.py --threads $THREADS --markers $MARKERS --wgs $METAGENOME --results $RESULTS.txt --tmp $TMP
```

Where:

* `$THREADS` is the number of threads for ShortBRED to use.

* `$MARKERS` is the location of the marker file generated in Step 2.

* `$METAGENOME` is the location of the metagenome to be queried (see Prerequisites).

* `$RESULTS` is the location of where to store the resulting output file.

* `$TMP` is the location for ShortBRED to store temporary files. This flag is not necessary, but highly useful for troubleshooting and detailed analysis.

----

### Merging and analyzing ShortBRED results

#### 5. Compiling ShortBRED Results

ShortBRED-Quantify outputs one `$RESULTS` file for each metagenome analyzed. For analyzing more than one metagenome, we have written a script to combine the output from multiple results files: `merge_shortbred.py`. It can be run as follows:

```
./scripts/merge_shortbred.py $RESULTS_1 $RESULTS_2 … $RESULTS_N --clusters-file $CLUSTERS
```

Where:

* `$RESULTS` files are ShortBRED-Quantify output files.

* `$CLUSTERS` is the cluster mapping file generated in Step 1.

* Additional flags are available, including where to save protein and cluster abundances files and to normalize samples to counts per microbial genome if average genome size is available. For more information, run `./merge_shortbred.py -h`

This script takes as inputs a list of locations of results files (from Step 4) and the cluster mapping file (from Step 2) and outputs two tables: one with results for each protein and one where proteins from the same cluster in the SSN have had their abundances summed.

----

#### 6. Output normalization

The `merge_shortbred.py` script can be used to normalize the output to counts per microbial genome. To do this calculation, append the flag `-g $AGS`, where `$AGS` is a two column file: the first column has metagenome identifiers and the second column lists the average genome size. Average genome sizes (AGS) have been previously computed [for many of the HMP metagenomes](http://dx.doi.org/10.1186/s13059-015-0611-7) using the software system [MicrobeCensus](https://github.com/snayfach/MicrobeCensus). MicrobeCensus can be applied to compute AGS values for additional metagenomes. If you use MicrobeCensus or the AGS values bundled with the CGFP workflow, [please cite this publication](http://dx.doi.org/10.1186/s13059-015-0611-7).

Alternatively, `merge_shortbred.py` can normalize protein abundance information to relative abundance (sum=1) units. This does not require any additional files. If no extra normalization options are specified, the table is output in RPKM units (reads per kilobase of sequence per million sample reads).

----

#### 7. Downstream analysis

 The tables produced by `merge_shortbred.py` can be analyzed in any number of ways. For example, heatmap-style visualization provides a convenient summary of the entire merged abundance table. [`hclust2`](https://bitbucket.org/nsegata/hclust2) provides a Python interface for heatmap construction (along with feature selection and feature/sample clustering).