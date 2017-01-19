__author__ = "Sebastian Kurscheid (sebastian.kurscheid@anu.edu.au)"
__license__ = "MIT"
__date__ = "2017-01-17"

# vim: syntax=python tabstop=4 expandtab
# coding: utf-8

from snakemake.exceptions import MissingInputException
import os

"""
Rules for running deepTools analysis on ChIP-Seq data
For usage, include this in your workflow.
"""

def cli_parameters_computeMatrix(wildcards):
    a = config["program_parameters"][wildcards.application][wildcards.tool][wildcards.mode]
    if wildcards.mode == "reference-point":
        a["--referencePoint"] = wildcards.referencePoint
    return(a)

rule bamCoverage_MNase:
    version:
        0.1
    params:
        deepTools_dir = config["deepTools_dir"],
        ignore = config["program_parameters"]["deepTools"]["ignoreForNormalization"]
    threads:
        lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
    input:
        "{assayID}/{runID}/{outdir}/{reference_version}/bowtie2/duplicates_marked/{unit}.Q10.sorted.MkDup.bam"
    output:
        "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/duplicates_marked/{unit}_{mode}_{norm}.bw"
    shell:
        """
        {params.deepTools_dir}/bamCoverage --bam {input} \
                                           --outFileName {output} \
                                           --outFileFormat bigwig \
                                           --MNase \
                                           --binSize 1 \
                                           --numberOfProcessors {threads} \
                                           --normalizeUsingRPKM \
                                           --ignoreForNormalization {params.ignore}\
                                           --smoothLength 30 \
                                           --skipNonCoveredRegions
        """

rule bamCoverage_MNase_RPKM_deduplicated:
    version:
        0.1
    params:
        deepTools_dir = config["deepTools_dir"],
        ignore = config["program_parameters"]["deepTools"]["ignoreForNormalization"]
    threads:
        lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
    input:
        "{assayID}/{runID}/{outdir}/{reference_version}/bowtie2/duplicates_removed/{unit}.Q10.sorted.DeDup.bam"
    output:
        "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/duplicates_removed/{unit}_{mode}_{norm}.bw"
    shell:
        """
        {params.deepTools_dir}/bamCoverage --bam {input} \
                                           --outFileName {output} \
                                           --outFileFormat bigwig \
                                           --MNase \
                                           --binSize 1 \
                                           --numberOfProcessors {threads} \
                                           --normalizeUsingRPKM \
                                           --ignoreForNormalization {params.ignore}\
                                           --smoothLength 30 \
                                           --skipNonCoveredRegions
        """


rule computeMatrix:
    version:
        0.1
    params:
        deepTools_dir = config["deepTools_dir"],
        program_parameters = lambda wildcards: ' '.join("{!s}={!s}".format(key, val.strip("\\'")) for (key, val) in cli_parameters_computeMatrix(wildcards).items())
    threads:
        lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
    input:
        file = expand("{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{unit}_{mode}_{norm}.bw",
                      assayID = "ChIP-Seq",
                      runID = "NB501086_0011_MNekrasov_MDCK_JCSMR_ChIPseq",
                      outdir = config["processed_dir"],
                      reference_version = config["references"]["CanFam3.1"]["version"][0],
                      application = "deepTools",
                      tool = "bamCoverage",
                      mode = "MNase",
                      duplicates = ["duplicates_marked", "duplicates_removed"],
                      unit = config["samples"]["ChIP-Seq"]["NB501086_0011_MNekrasov_MDCK_JCSMR_ChIPseq"],
                      norm = "RPKM"),
        region = lambda wildcards: home + config["program_parameters"]["deepTools"]["regionFiles"][wildcards.region]
    output:
        matrix_gz = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{referencePoint}/{region}_{mode}.matrix.gz"
    wrapper:
        "file://" + wrapper_dir + "/deepTools/computeMatrix/wrapper.py"

rule plotProfile:
    version:
        0.1
    params:
        deepTools_dir = config["deepTools_dir"]
    input:
        matrix_gz = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/computeMatrix/{mode}/{duplicates}/{referencePoint}/{region}_{mode}.matrix.gz"
    output:
        figure = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{referencePoint}/profile.{region}.pdf",
        data = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{referencePoint}/profile.{region}.data",
        regions = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{referencePoint}/profile.{region}.bed"
    shell:
        """
            {params.deepTools_dir}/plotProfile --matrixFile {input.matrix_gz} \
                                               --outFileName {output.figure} \
                                               --outFileNameData {output.data} \
                                               --outFileSortedRegions {output.regions} \
                                               --plotType se
        """

# rule computeMatrix_scaleRegions:
#     version:
#         0.1
#     params:
#         deepTools_dir = config["deepTools_dir"],
#         program_parameters = lambda wildcards: ' '.join("{!s}={!s}".format(key, val.strip("\\'")) for (key, val) in cli_parameters_computeMatrix(wildcards).items())
#     threads:
#         lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
#     input:
#         files = expand("deepTools/{data_dir}/{samples}.bw", samples = config["units"], data_dir = "bamCoverage"),
#         region = lambda wildcards: config["program_parameters"]["deepTools"]["regionFiles"][wildcards.region]
#     output:
#         matrix_gz = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{referencePoint}/{region}.{unit}_{mode}.matrix.gz"
#     wrapper:
#         "file://" + wrapper_dir + "/deepTools/computeMatrix/wrapper.py"
