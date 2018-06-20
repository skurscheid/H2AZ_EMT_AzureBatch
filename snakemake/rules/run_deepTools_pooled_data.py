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
    a = config["program_parameters"][wildcards["application"]]["computeMatrix"]][wildcards["command"]]
    if wildcards["command"] == "reference-point":
        a["--referencePoint"] = wildcards.referencePoint
    return(a)


# rule computeMatrix_pooled_replicates:
#     version:
#         0.2
#     params:
#         deepTools_dir = home + config["deepTools_dir"],
#         program_parameters = lambda wildcards: ' '.join("{!s}={!s}".format(key, val.strip("\\'")) for (key, val) in cli_parameters_computeMatrix(wildcards).items())
#     threads:
#         lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
#     input:
#         file = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/bamCoverage/{mode}/{duplicates}/merged_replicates/{sample_group}_{mode}_{norm}.bw",
#         region = lambda wildcards: home + config["program_parameters"]["deepTools"]["regionFiles"][wildcards.region]
#     output:
#         matrix_gz = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/computeMatrix/{command}/{duplicates}/{referencePoint}/{sample_group}_{region}_{mode}.matrix.gz"
#     wrapper:
#         "file://" + wrapper_dir + "/deepTools/computeMatrix/wrapper.py"

rule bam_coverage_pooled_replicates:
    version:
        0.1
    params:
        deepTools_dir = home + config["deepTools_dir"],
        ignore = config["program_parameters"]["deepTools"]["ignoreForNormalization"],
        program_parameters = cli_parameters_bamCoverage
    threads:
        lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
    input:
        bam = merge_replicates("{assayID}/{runID}/{outdir}/{reference_version}/samtools/merge/{duplicates}/{sample_group}.bam")
    output:
        bigwig = "{assayID}/{runID}/{outdir}/{reference_version}/{application}/bamCoverage/{mode}/{duplicates}/merged_replicates/{sample_group}_{mode}_{norm}.bw"
    shell:
        """
            {params.deepTools_dir}/bamCoverage --bam {input.bam} \
                                               --outFileName {output.bigwig} \
                                               --outFileFormat bigwig \
                                               {params.program_parameters} \
                                               --numberOfProcessors {threads} \
                                               --normalizeUsingRPKM \
                                               --ignoreForNormalization {params.ignore}
        """

rule bigwig_compare_pooled_replicates:
    version:
        0.1
    params:
        deepTools_dir = home + config["deepTools_dir"],
        ignore = config["program_parameters"]["deepTools"]["ignoreForNormalization"]
    threads:
        lambda wildcards: int(str(config["program_parameters"]["deepTools"]["threads"]).strip("['']"))
    input:
        control = "{assayID}/{runID}/{outdir}/{reference_version}/deepTools/bamCoverage/{mode}/{duplicates}/merged_replicates/{control}_{mode}_{norm}.bw",
        treatment = "{assayID}/{runID}/{outdir}/{reference_version}/deepTools/bamCoverage/{mode}/{duplicates}/merged_replicates/{treatment}_{mode}_{norm}.bw"
    output:
        "{assayID}/{runID}/{outdir}/{reference_version}/{application}/{tool}/{mode}/{duplicates}/{scaleFactors}/{treatment}_vs_{control}_{mode}_{ratio}_{norm}.bw"
    shell:
        """
            {params.deepTools_dir}/bigwigCompare --bigwig1 {input.treatment} \
                                                 --bigwig2 {input.control} \
                                                 --outFileName {output} \
                                                 --ratio {wildcards.ratio} \
                                                 --numberOfProcessors {threads}
        """