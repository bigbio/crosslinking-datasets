# METI Pipeline: Proteomics Data Processing & Organism Identification

A robust Nextflow pipeline for automated retrieval, processing, organism identification, and advanced proteomics analysis of mass spectrometry data from the PRIDE database.

---

## Table of Contents

- [Overview](#overview)
- [What's New](#whats-new---two-pass-sage-workflow)
- [Scientific Background](#scientific-background)
- [Pipeline Architecture](#pipeline-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Parameters](#parameters)
- [Output Structure](#output-structure)
- [Resume & Caching](#resume--caching)
- [Documentation](#documentation)
- [Container Details](#container-details)
- [Troubleshooting](#troubleshooting)

---

## Overview

This pipeline automates the complete workflow for:
1. **Downloading** PRIDE proteomics datasets (PXD accessions)
2. **Converting** raw mass spectrometry files (.raw → .mzML)
3. **Sequencing** peptides using de novo sequencing (Casanovo)
4. **Identifying** source organisms from peptide sequences (Peptonizer2000)
5. **Auto-detecting** experimental metadata (instrument, fragmentation, acquisition type)
6. **Extracting** publication metadata using LLM (optional)
7. **Advanced database search** with PTM discovery (SAGE/PTM-Shepherd, optional)
8. **Aggregating** all results into unified JSON output

The pipeline is containerized using Singularity, GPU-accelerated where available, and designed for reproducibility and scalability.

### Key Features

- **Batch processing**: Process multiple PXDs from a CSV file
- **LLM metadata extraction**: Automatically extract SDRF-compliant metadata from publications using OpenAI API
- **Auto-detection**: Automatically detect instrument, fragmentation type, and experimental parameters
- **Two-Pass Sage Workflow**: Open search for PTM discovery → Closed search with validated PTMs + quantification
- **Generalized PTM Support**: Works with any PTM combination (phospho, ubiquitin, acetyl, etc.)
- **Dynamic Quantification**: Automatically applies detected labeling type (LFQ, TMT, iTRAQ, SILAC)
- **Resume support**: Automatic caching and resume on failure
- **Flexible filtering**: Customizable confidence thresholds for peptide and organism identification

---

## What's New - Two-Pass SAGE Workflow

### Architecture Improvements (v2.0)

The pipeline now implements a **sophisticated two-pass SAGE search workflow** for enhanced PTM detection and quantification:

#### Pass 1: Open Search (PTM Discovery)
- **Precursor tolerance**: ±500 Da (wide window for any mass shift)
- **Mods**: None (all mods removed for unbiased PTM detection)
- **Purpose**: Identify all possible post-translational modifications
- **Output**: PTM-Shepherd analysis with high-confidence PTM candidates

#### Pass 2: Closed Search (Refined with Quantification)
- **Precursor tolerance**: ±20 ppm (high accuracy)
- **Mods**: Validated PTMs from Pass 1 + Carbamidomethyl (C +57.02146)
- **Quantification**: LFQ or detected labeling type (TMT, iTRAQ, SILAC)
- **Purpose**: Refined identification with discovered PTMs + accurate quantification

### Example Results: Phosphoproteomics Sample (PXD000070)

| Metric | Pass 1 (Open) | Pass 2 (Closed) | Improvement |
|--------|---------------|-----------------|-------------|
| Total PSMs | 261,509 | 21,746 | Refined |
| Phospho PSMs | 170 (0.065%) | 2,450 (11.27%) | **14.4x** ↑ |
| Pyrophospho | — | 1,279 (5.88%) | Novel |
| Quantification | Disabled | LFQ Enabled | Restored |

### Generalized Architecture

- **Old**: `--phospho_ClosedSearch` (phospho-specific only)
- **New**: `--ClosedSearch --variable_mods "{...}"` (any PTM combination)
- **Benefit**: Single pipeline for phospho, ubiquitin, acetyl, sumoylation, etc.

**Supported Labeling Types** (auto-detected):
- LFQ (Label-Free Quantification)
- TMT6, TMT10, TMT11, TMT16
- iTRAQ4, iTRAQ8
- SILAC

---

## Scientific Background

### The Challenge: Metaproteomic Organism Identification

In metaproteomics and proteomics quality control, a fundamental question is: **"What organism(s) produced these proteins?"** This pipeline addresses this by:

1. **De novo peptide sequencing**: Using Casanovo, a deep learning model that predicts peptide sequences directly from MS/MS spectra without requiring a reference database
2. **Taxonomic inference**: Using Peptonizer2000, which maps peptide sequences to taxonomic clades using a Bayesian framework

### Why De Novo Sequencing?

Traditional database search approaches require:
- Prior knowledge of the organism
- Complete reference proteomes
- Exact sequence matches

De novo sequencing with Casanovo:
- Works on **any organism**, including novel or uncharacterized species
- Handles sequence variants and modifications
- Enables taxonomic identification when the organism is unknown

### Peptonizer2000: Bayesian Taxonomic Assignment

Peptonizer2000 uses:
- **UniProt peptide mappings** across the tree of life
- **Bayesian inference** to assign probabilities to taxonomic clades
- **Regularization parameters** (alpha, beta, prior) to balance specificity vs. sensitivity

The tool outputs ranked taxonomic hypotheses, allowing researchers to identify contamination, verify sample identity, or explore metaproteomic composition.

---

## Pipeline Architecture

### Four-Process Workflow

```
┌──────────────────┐
│   fetch_pxd      │  Download PRIDE data, convert .raw → .mzML
│                  │  Extract run metadata
└────────┬─────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│  organism_id     │              │  sage_search     │
│                  │              │                  │
│  Casanovo        │              │  SAGE database   │
│  Peptonizer2000  │              │  search          │
│  Organism ID     │              │  PTM-Shepherd    │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         └──────────┬──────────────────────┘
                    ▼
         ┌──────────────────┐
         │ aggregate_results│  Combine all results into JSON
         │                  │
         └──────────────────┘
```

### Process 1: `fetch_pxd`

**Purpose**: Retrieve and prepare mass spectrometry data from PRIDE

**Steps**:
1. Query PRIDE API for project metadata and file listings
2. Download raw files via FTP (with automatic HTTPS fallback)
3. Convert Thermo `.raw` files to open `.mzML` format using ThermoRawFileParser
4. Extract technical metadata (scan counts, acquisition parameters) using mzML_assessor

**Output**: 
- `PXD######/`: Downloaded data directory
- `PXD######_PRIDEmetadata.json`: Project metadata
- `*.mzML`: Converted mass spectrometry files
- `runAssessor/study_metadata.json`: Technical metadata

**Key Features**:
- Automatic retry logic with exponential backoff for network failures
- HTTPS-first download strategy (firewall-friendly)
- Intelligent caching via `storeDir` (see [Resume & Caching](#resume--caching))

### Process 2: `organism_id`

**Purpose**: Identify organisms through de novo sequencing and taxonomic mapping

**Steps**:

1. **Casanovo De Novo Sequencing**
   - Predicts peptide sequences from MS/MS spectra
   - Uses deep learning transformer architecture
   - Generates `.mztab` output with per-amino-acid confidence scores
   - Automatically falls back to CPU if GPU fails

2. **Peptide Quality Filtering**
   - Filters by minimum length (>10 amino acids)
   - Filters by confidence score (configurable via `--casanovo_thresholds`, default: 60%, 70%, 80%)
   - Removes contaminants by digest matching against `UniversalContaminats.fasta`

3. **Peptonizer2000 Taxonomic Assignment**
   - Requires minimum number of peptides (configurable via `--min_peptides_for_peptonizer`, default: 100)
   - Maps peptides to UniProt taxonomic database
   - Runs Bayesian inference with multiple parameter sets:
     - α (alpha): Peptide uniqueness weight [0.7, 0.8, 0.9, 0.99]
     - β (beta): Taxonomic specificity weight [0.6, 0.7, 0.8, 0.9]
     - Prior: Base probability [0.1, 0.3, 0.5]
   - Restricts search to curated taxon list (e.g., common PRIDE organisms)

### Process 3: `sage_search` (Optional)

**Purpose**: Database search for peptide-spectrum matching and post-translational modification (PTM) identification

**Steps**:

1. **SAGE Database Search**
   - Ultra-fast database search engine for peptide identification
   - Supports both open search (wide precursor tolerance) and closed search modes
   - Downloads organism-specific FASTA from UniProt based on taxonomic ID
   - Generates PSM (peptide-spectrum match) tables with scoring metrics

2. **PTM-Shepherd Analysis**
   - Identifies and quantifies post-translational modifications
   - Performs PTM localization on peptide sequences
   - Generates modification summary statistics
   - Creates diagnostic plots and modification profiles

**Output**:
- `sage_results/results.sage.tsv`: SAGE PSM table
- `sage_results/results.json`: SAGE configuration and statistics
- `sage_results/psm.ptmshepherd.tsv`: PTM-Shepherd annotated PSMs
- `sage_results/global.modsummary.tsv`: PTM summary across dataset
- `sage_results/global.profile.tsv`: PTM localization profiles

**Activation**: Set `--run_sage true` and `--taxid <NCBI_taxid>` to enable this process

### Process 4: `aggregate_results`

**Purpose**: Combine all pipeline outputs into a unified JSON report

**Steps**:

1. **Metadata Integration**
   - Collects PRIDE project metadata (title, organism, instruments, publications)
   - Gathers technical run metadata (scan counts, ion source, analyzer type)
   - Timestamps the aggregation process

2. **Result Compilation**
   - Integrates organism identification results from Peptonizer2000
   - Includes SAGE/PTM-Shepherd results if available
   - Consolidates filtered peptide lists at multiple confidence thresholds
   - Preserves full provenance information for reproducibility

**Output**:
- `PXD######_aggregated_results.json`: Comprehensive JSON containing all pipeline outputs, metadata, and analysis results in a single structured file

**Output**:
- `organism_results/CasanovoSequence/`: Casanovo `.mztab` files
- `*_filtered{60,70,80}pct.tsv`: Filtered peptide lists at different thresholds
- `Peptonizer2000_data/*/peptonizer_result.csv`: Taxonomic assignments

---

## Installation

### Prerequisites

- **Nextflow** ≥ 21.10.3
- **Singularity** ≥ 3.5 (for containerized execution)
- **NVIDIA GPU** (optional, for accelerated Casanovo)
- **~50GB disk space** per PXD dataset (varies by project size)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PipelineProduction
   ```

2. **Build the Singularity containers on your system**:

   ```bash
   sudo singularity build containers/pride-fetch.sif containers/pride-fetch.def
   sudo singularity build containers/organism-id.sif containers/organism-id.def
   ```

3. **Verify installation**:
   ```bash
   nextflow -version
   singularity --version
   
   # Test containers
   singularity exec containers/pride-fetch.sif python --version
   singularity exec containers/organism-id.sif casanovo --help
   ```

---

## Usage

### Quick Start Example

See [EXAMPLE.sh](EXAMPLE.sh) for a complete example command:

```bash
# Run pipeline on 3 PXDs with up to 3 raw files each, with LLM extraction
export OPENAI_API_KEY="your-api-key-here"  # Required for LLM extraction
nextflow run main.nf \
  --pxd_csv PXDs.csv \
  --num_pxds 3 \
  --max_raw_files 3 \
  --run_llm_extraction true
```

### Basic Commands

**Process multiple PXDs from a CSV file:**
```bash
nextflow run main.nf \
  --pxd_csv PXDs.csv \
  --num_pxds 5 \
  --max_raw_files 3
```

**With LLM-based metadata extraction from publications:**
```bash
export OPENAI_API_KEY="your-api-key-here"
nextflow run main.nf \
  --pxd_csv PXDs.csv \
  --num_pxds 3 \
  --run_llm_extraction true
```

**With SAGE database search:**
```bash
nextflow run main.nf \
  --pxd_csv PXDs.csv \
  --num_pxds 2 \
  --run_sage true \
  --taxid 9606
```

### Advanced Usage

**With Custom Filtering Thresholds:**

```bash
nextflow run main.nf \
  --pxd_csv PXDs.csv \
  --num_pxds 3 \
  --casanovo_thresholds 70,80,90 \
  --min_peptides_for_peptonizer 50
```

**Use Cases**:
- **Lower thresholds** (e.g., `50,60,70`): For challenging organisms or low-quality data
- **Higher thresholds** (e.g., `80,85,90`): For high-quality data requiring stringent filtering
- **Fewer minimum peptides** (e.g., `50`): For exploratory analysis or sparse data
- **More minimum peptides** (e.g., `200`): For robust taxonomic assignments with higher confidence

### Resume from Previous Run

The pipeline automatically resumes (configured in `nextflow.config`):

## Parameters

### Required

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--pxd_csv` | CSV file containing PXD identifiers (column: "PXD") | `PXDs.csv` |

### Core Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--num_pxds` | All | Number of PXDs to process from the CSV |
| `--max_raw_files` | All | Maximum raw files to process per PXD (useful for testing) |
| `--outdir` | `results` | Output directory for results |
| `--download_dir` | `work/downloads` | Directory for downloaded PRIDE data |

### LLM Metadata Extraction (Optional)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--run_llm_extraction` | `false` | Enable LLM-based metadata extraction from publications |
| `--pride_database_path` | `/data/20250927` | Path to PRIDE publication database (container path) |
| `--llm_workers` | `1` | Number of parallel OpenAI API calls per PXD |

**Requirements for LLM extraction:**
- Set `OPENAI_API_KEY` environment variable
- Access to PMC publication database at configured path
- Adds ~1-2 minutes per PXD (API call time)

### Organism Identification

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--contaminants_fasta` | `assets/UniversalContaminats.fasta` | FASTA file of contaminant proteins |
| `--taxid_list_file` | `assets/taxid_lists/CommonPRIDEtaxids.txt` | Taxon IDs to restrict Peptonizer search |
| `--casanovo_thresholds` | `60,70,80` | Confidence thresholds (percentages) for peptide filtering |
| `--min_peptides_for_peptonizer` | `100` | Minimum peptides required to run Peptonizer2000 |

### Database Search (Optional)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--run_sage` | `false` | Enable SAGE database search and PTM identification |
| `--taxid` | None | NCBI taxonomic ID for FASTA download (required if `--run_sage true`) |
| `--sage_config` | `assets/default_sage.config` | SAGE configuration file |

### Containers

| Parameter | Description |
|-----------|-------------|
| `--fetch_container` | Path to PRIDE fetch Singularity container |
| `--organism_container` | Path to organism identification container |
| `--sage_container` | Path to SAGE/PTM-Shepherd container |
| `--llm_container` | Path to LLM extraction container |

### Taxon Lists

Pre-configured taxon lists in `assets/taxid_lists/`:
- **CommonPRIDEtaxids.txt**: Common organisms in PRIDE (human, mouse, yeast, E. coli)
- **EcoliAlltaxids.txt**: All E. coli strains and subspecies
- **MoreThan10Projects_taxids.txt**: Organisms with >10 PRIDE projects

---

## Output Structure

```
results/
├── PXD000001/
│   ├── PXD000001_aggregated_results.json      # ← **MASTER OUTPUT**
│   ├── PXD000001/                              # Downloaded PRIDE files
│   │   ├── PXD000001_PRIDEmetadata.json
│   │   ├── *.mzML                              # Converted mass spec files
│   │   └── runAssessor/
│   │       └── study_metadata.json             # Auto-detected metadata
│   ├── organism_results/                       # Organism identification
│   │   └── CasanovoSequence/
│   │       └── PXD000001_filename/
│   │           ├── *.mztab                     # Raw Casanovo output
│   │           ├── *_processed.tsv             # Parsed PSMs
│   │           ├── *_filtered{60,70,80}pct.tsv # Confidence-filtered peptides
│   │           └── Peptonizer2000_data/
│   │               └── *_filtered80pct_slim/
│   │                   └── peptonizer_result.csv  # ← Taxonomic assignments
│   ├── llm_results/                            # LLM-extracted metadata (optional)
│   │   ├── PubText.json                        # Publication text
│   │   └── gpt-*-*/
│   │       └── PXD000001_Metadata.json         # ← SDRF-format metadata
│   ├── sage_results/                           # Database search (optional)
│   │   ├── results.sage.tsv                    # SAGE PSM table
│   │   ├── psm.ptmshepherd.tsv                 # PTM-annotated PSMs
│   │   └── global.modsummary.tsv               # PTM summary
│   └── taxid_warnings.json                     # Taxid validation warnings (optional)
├── PXD000002/
│   └── ...
└── ...
```

### Aggregated Results JSON Structure

The `PXD######_aggregated_results.json` file contains all pipeline outputs in a unified structure:

```json
{
  "pxd_id": "PXD042173",
  "pipeline_version": "1.0",
  "aggregation_timestamp": "2026-01-23T15:11:51.396655",
  
  "input_paths": {
    "pxd_dir": "PXD042173",
    "organism_dir": "organism_results",
    "sage_results_dir": "/dev/null",
    "llm_results_dir": "llm_results",
    "pride_json_dir": "/data/20250927/pride_json",
    "taxid_warnings": "taxid_warnings.json"
  },
  
  "runAssessor": {
    "files": {
      "<absolute_path_to_file.mzML>": {
        "ROIs": { /* TMT/iTRAQ reporter ion detection */ },
        "instrument_model": {
          "accession": "MS:1002732",
          "name": "Orbitrap Fusion Lumos",
          "rank": "1"
        },
        "spectra_stats": {
          "acquisition_type": "DDA",
          "fragmentation_type": "HR_HCD",
          "high_accuracy_precursors": "true",
          "n_ms2_spectra": 45563,
          "n_charge_4_precursors": 31328,
          /* ... additional scan/charge statistics */
        },
        "summary": {
          "fragmentation_type": "HR_HCD",
          "labeling": {
            "call": "none",
            "scores": { /* TMT/iTRAQ scoring */ }
          }
        }
      }
    },
    "knowledge": {
      "instrument_model": "Orbitrap Fusion Lumos",
      "instrument_models": { "Orbitrap Fusion Lumos": 10 }
    },
    "search_criteria": {
      "acquisition_type": "DDA",
      "fragmentation_type": "HR_HCD",
      "high_accuracy_precursors": "true",
      "labeling": "none"
    },
    "spectra_stats": { /* Aggregated statistics across all files */ },
    "state": { "code": "OK", "status": "OK", "version": "v0.1" }
  },
  
  "organism_identification": {
    "results": [
      {
        "file_path": "organism_results/.../peptonizer_result.csv",
        "filter_threshold": 80,
        "num_predictions": 10,
        "columns": ["taxon_name", "taxon_id", "score"],
        "data": [
          {
            "taxon_name": "Homo sapiens",
            "taxon_id": 9606,
            "score": 0.8450090885162354
          }
          /* ... additional ranked organisms */
        ]
      }
      /* ... results for each mzML file */
    ],
    "summary": {
      "num_files_processed": 10,
      "total_predictions": 93,
      "filter_thresholds_used": [80]
    }
  },
  
  "PTM-shepherd": null,  /* or PTM results if SAGE was run */
  
  "pride_metadata": {
    "accession": "PXD042173",
    "title": "Proteome-scale recombinant standard datasets for XL-MS",
    "projectDescription": "...",
    "sampleProcessingProtocol": "...",
    "dataProcessingProtocol": "...",
    "keywords": ["Crosslinking mass spectrometry", "..."],
    "instruments": [
      {
        "cvLabel": "MS",
        "accession": "MS:1002732",
        "name": "Orbitrap Fusion Lumos"
      }
    ],
    "organisms": [
      {
        "cvLabel": "NEWT",
        "accession": "9606",
        "name": "Homo sapiens (human)"
      }
    ],
    "references": [ /* Publication details */ ]
  },
  
  "taxid_warnings": {
    "pxd": "PXD042173",
    "warnings": [],
    "summary": {
      "total_warnings": 0,
      "files_with_taxid": 10,
      "files_without_taxid": 0
    }
  },
  
  "processing_summary": {
    "runAssessor_found": true,
    "organism_results_found": true,
    "sage_results_found": false,
    "llm_metadata_found": true,
    "pride_metadata_found": true,
    "taxid_warnings_found": true,
    "total_data_files": 10
  },
  
  "llm_extracted_metadata": {
    "filename.raw": {
      "Source Name": ["Source_batch"],
      "Assay Name": ["Source_batch_filename"],
      "Raw Data File": ["filename.raw"],
      "Characteristics[Organism]": ["human proteins"],
      "Characteristics[OrganismTaxid]": ["9606"],
      "Comment[Instrument]": ["Orbitrap Fusion Lumos..."],
      "Comment[FragmentationMethod]": ["HCD..."],
      /* ... additional SDRF-compliant metadata fields */
    }
    /* ... metadata for each raw file */
  }
}
```

### Key Output Components

| Component | Description |
|-----------|-------------|
| **`pxd_id`** | PRIDE project accession identifier |
| **`pipeline_version`** | Version of the METI pipeline used |
| **`aggregation_timestamp`** | ISO 8601 timestamp of aggregation |
| **`input_paths`** | Paths to all input data sources used in aggregation |
| **`runAssessor`** | Auto-detected MS instrument, acquisition, and fragmentation metadata per file |
| **`organism_identification`** | Ranked taxonomic assignments from Peptonizer2000 with scores |
| **`PTM-shepherd`** | Post-translational modification results (if `--run_sage true`) |
| **`pride_metadata`** | Complete PRIDE project metadata from public repository |
| **`taxid_warnings`** | Validation warnings for taxonomic ID consistency |
| **`processing_summary`** | Status flags indicating which pipeline components completed |
| **`llm_extracted_metadata`** | LLM-extracted SDRF-compliant metadata per raw file (if `--run_llm_extraction true`) |

### Individual Output Files

| File | Description |
|------|-------------|
| `peptonizer_result.csv` | Ranked taxonomic assignments with posterior probabilities (per mzML file, per threshold) |
| `study_metadata.json` | Auto-detected experimental metadata from runAssessor (instrument, fragmentation, etc.) |
| `PXD######_PRIDEmetadata.json` | PRIDE project metadata (title, organism, instruments, publications) |
| `PXD######_Metadata.json` | LLM-extracted SDRF metadata per raw file (if LLM enabled) |
| `results.sage.tsv` | SAGE database search PSMs (if SAGE enabled) |
| `global.modsummary.tsv` | PTM-Shepherd modification summary statistics (if SAGE enabled) |
| `*_filtered{60,70,80}pct.tsv` | Peptides passing quality filters at different confidence thresholds |
| `taxid_warnings.json` | Taxonomic ID validation warnings and mismatches |

---

## Resume & Caching

### How Nextflow Resume Works

Nextflow's `-resume` feature allows the pipeline to skip already-completed tasks by:

1. **Hashing task inputs**: Script, parameters, input files
2. **Checking the work directory**: If a matching hash exists with valid outputs, reuse it
3. **Marking as CACHED**: Task shows as `[CACHED]` in execution logs

### Pipeline-Specific Optimizations

This pipeline uses three strategies for reliable caching:

#### 1. `storeDir` for Downloaded Data

```groovy
process fetch_pxd {
    storeDir "${params.download_dir}/${pxd}"
    // ...
}
```

**Effect**: 
- Outputs are stored directly in `work/pride/PXD######/` (not in work hash directories)
- If the directory exists, the process is **skipped entirely**
- Data persists across pipeline runs and manual work directory cleaning

#### 2. Lenient Cache Mode

```groovy
cache 'lenient'
```

**Effect**:
- Uses file size + modification time for cache validation (not MD5 checksums)
- Faster for large files (no checksum computation)
- More forgiving when file metadata changes but content doesn't

#### 3. Non-Overwriting publishDir

```groovy
publishDir "${params.outdir}", mode: 'copy', overwrite: false
```

**Effect**:
- Doesn't re-copy files that already exist in results directory
- Speeds up resume when final outputs are already present

### Best Practices

**✅ DO:**
- Keep your `work/` directory intact between runs
- Use the same parameters when resuming
- Let Nextflow manage caching automatically

**❌ DON'T:**
- Delete `work/` unless you want a fresh run
- Change parameters that affect task hashing (script changes, input paths)
- Manually modify files in `work/` directories

### Force Fresh Run

To start from scratch:

```bash
# Option 1: New work directory
nextflow run main.nf -w work_fresh --pxd PXD023343 ...

# Option 2: Clean work directory
rm -rf work/
nextflow run main.nf --pxd PXD023343 ...
```

---

## Container Details

### pride-fetch.sif

**Base**: micromamba:1.5.8-focal (Ubuntu 20.04)

**Tools**:
- Python 3.11
- ThermoRawFileParser (Bioconda)
- pyteomics (MS file parsing)
- requests, pandas, lxml

**Purpose**: Lightweight environment for data retrieval and RAW→mzML conversion

### organism-id.sif

**Base**: Ubuntu 24.04

**Tools**:
- Python 3.11
- **Casanovo 5.1.0**: De novo peptide sequencing with transformer architecture
- **Peptonizer2000**: Bayesian taxonomic assignment (from GitHub)
- **Snakemake**: Workflow management for Peptonizer2000
- **PyTorch**: GPU support for Casanovo
- pyteomics, scikit-learn, pandas

**GPU Configuration**:
- CUDA-enabled for GPU acceleration
- Automatic CPU fallback if GPU unavailable
- Containerized with `--nv` flag for GPU access

**Environment Variables**:
```bash
PEPTONIZER2000_HOME=/opt/Peptonizer2000
CASANOVO_HOME=/opt/casanovo
MPLCONFIGDIR=/tmp/matplotlib
NUMBA_CACHE_DIR=/tmp/numba_cache
```

### sage.sif

**Base**: Python 3.11 with CUDA support

**Tools**:
- **SAGE**: Ultra-fast database search engine for proteomics
- **PTM-Shepherd**: Post-translational modification identification and localization
- **Java Runtime**: Required for PTM-Shepherd
- pandas, numpy, pyteomics, matplotlib

**Purpose**: Database search and PTM discovery for comprehensive peptide identification

**GPU Configuration**:
- GPU-accelerated database search
- Containerized with `--nv` flag for GPU access

**Key Paths**:
```bash
PTMSHEPHERD_JAR=/opt/ptmshepherd/ptmshepherd.jar
```

---

## Troubleshooting

### Pipeline restarts instead of resuming

**Cause**: Nextflow couldn't find cached outputs or detected changed inputs

**Solutions**:
1. Verify `work/pride/PXD######/` exists with data
2. Check that parameters haven't changed
3. Ensure `storeDir` is configured in `main.nf` (should be after recent updates)
4. Check `.nextflow.log` for cache misses

### Casanovo GPU errors

**Symptoms**:
```
RuntimeError: CUDA out of memory
RuntimeError: No CUDA GPUs are available
```

**Solutions**:
- Pipeline automatically retries on CPU with `CUDA_VISIBLE_DEVICES=""`
- Check GPU availability: `nvidia-smi`
- Reduce batch size (requires Casanovo config modification)

### Peptonizer2000 fails with "ModuleNotFoundError: rbo"

**Cause**: Missing Python dependency

**Solution**: Rebuild container (now includes `rbo==0.1.3` in organism-id.def)

### "Permission denied" when building containers

**Cause**: Singularity build requires root

**Solution**:
```bash
sudo singularity build containers/organism-id.sif containers/organism-id.def
```

Or use `--fakeroot` if available:
```bash
singularity build --fakeroot containers/organism-id.sif containers/organism-id.def
```

### Work directory filling up disk

**Solution**: Clean old runs periodically
```bash
# Clean all work files
nextflow clean -f

# Clean specific run
nextflow clean <run-name> -f
```

**Tip**: Downloaded PRIDE data in `work/pride/` persists due to `storeDir` and won't be deleted by `nextflow clean`.

---

## Credits

**Pipeline Development**: METI Project Team

**Key Tools**:
- **Casanovo**: Yilmaz et al. (2022), Nature Methods
- **Peptonizer2000**: Vaudel et al., Compomics
- **ThermoRawFileParser**: Hulstaert et al. (2020)
- **Nextflow**: Di Tommaso et al. (2017)

**Data Source**: PRIDE Archive (ProteomeXchange)

---

## License

This project is available under the MIT License.

---

## Quick Reference Card

```bash
# Build containers (one-time setup)
sudo singularity build containers/pride-fetch.sif containers/pride-fetch.def
sudo singularity build containers/organism-id.sif containers/organism-id.def
sudo singularity build containers/sage.sif containers/sage.def

# Run pipeline - organism ID only
nextflow run main.nf \
  --pxd PXD023343 \
  --download_dir $PWD/work/pride \
  --outdir $PWD/results \
  --contaminants_fasta $PWD/assets/UniversalContaminats.fasta \
  --taxid_list_file $PWD/assets/taxid_lists/CommonPRIDEtaxids.txt

# Run pipeline - with SAGE PTM identification
nextflow run main.nf \
  --pxd PXD023343 \
  --download_dir $PWD/work/pride \
  --outdir $PWD/results \
  --contaminants_fasta $PWD/assets/UniversalContaminats.fasta \
  --taxid_list_file $PWD/assets/taxid_lists/CommonPRIDEtaxids.txt \
  --run_sage true \
  --taxid 9606

# Resume automatically handles caching - just re-run the same command!
```

## Usage

### Basic usage

```bash
nextflow run main.nf \
    --input samplesheet.csv \
    --outdir results \
    -profile local
```

### With Docker

```bash
nextflow run main.nf \
    --input samplesheet.csv \
    --outdir results \
    -profile docker
```

### On SLURM cluster

```bash
nextflow run main.nf \
    --input samplesheet.csv \
    --outdir results \
    -profile slurm
```

## Input

The pipeline requires a CSV samplesheet with the following columns:

- `sample`: Sample name
- `file_path`: Path to raw mass spectrometry file
- `organism`: Expected organism (optional)

Example:

```csv
sample,file_path,organism
sample1,/path/to/file1.raw,human
sample2,/path/to/file2.raw,mouse
```

## Documentation

Complete documentation is organized in the [`docs/`](docs) directory:

### Architecture Documentation
- [**COMPLETE_INTEGRATION_SUMMARY.md**](docs/architecture/COMPLETE_INTEGRATION_SUMMARY.md) - Full system architecture and integration points
- [**IMPLEMENTATION_NOTES.md**](docs/architecture/IMPLEMENTATION_NOTES.md) - Implementation details and design decisions
- [**DIA_INTEGRATION_SUMMARY.md**](docs/architecture/DIA_INTEGRATION_SUMMARY.md) - DIA-NN workflow integration
- [**TAXID_DETERMINATION.md**](docs/architecture/TAXID_DETERMINATION.md) - Taxonomy ID detection logic

### User Guides & Features
- [**AUTO_DETECTION_FEATURE.md**](docs/guides/AUTO_DETECTION_FEATURE.md) - Auto-detection of experimental parameters
- [**LLM_EXTRACTION_SUMMARY.md**](docs/guides/LLM_EXTRACTION_SUMMARY.md) - LLM-based metadata extraction
- [**PARALLEL_EXECUTION.md**](docs/guides/PARALLEL_EXECUTION.md) - Parallel processing strategies
- [**PIPELINE_VERIFICATION.md**](docs/guides/PIPELINE_VERIFICATION.md) - Pipeline verification and testing procedures

## Output

The pipeline produces:

- `casanovo/`: Peptide sequences from de novo sequencing
- `peptonizer2000/`: Organism identification results
- `sage_results/`: Database search and PTM identification (when `--run_sage true`)
  - `pass1_open_search/`: Open search PTM discovery results
  - `pass2_closed_search/`: Closed search with validated PTMs and quantification
  - `validated_ptms.json`: PTMs validated for pass 2
  - `global.modsummary.tsv`: PTM summary statistics
- `tech_metadata/`: Technical metadata from MS files
- `collate/`: Combined results and summary reports
- `pipeline_info/`: Pipeline execution reports

## Parameters

### Required

- `--pxd_csv`: Path to CSV file with PXD accessions (default: PXDs.csv)
- `--outdir`: Output directory

### SAGE & Quantification

- `--run_sage`: Enable SAGE database search and PTM identification (default: false)
- `--taxid`: NCBI Taxonomy ID for SAGE FASTA download (required if `--run_sage true`)
- `--max_raw_files`: Maximum .raw files to download per PXD (default: 10)

### Optional

- `--max_memory`: Maximum memory (default: 128.GB)
- `--max_cpus`: Maximum CPUs (default: 16)
- `--max_time`: Maximum time (default: 240.h)
- `--run_llm_extraction`: Enable LLM metadata extraction (default: false)

## Profiles

- `local`: Run locally
- `docker`: Use Docker containers
- `singularity`: Use Singularity containers
- `slurm`: Run on SLURM cluster
- `test`: Run with test data

## Dependencies

- Nextflow >= 21.10.3
- Docker or Singularity (for containerized execution)
- Casanovo
- Peptonizer2000
- ThermoRawFileParser
- SAGE (for database search)
- PTM-Shepherd (for PTM discovery)

## Credits

This pipeline was developed for the METI project.

## License

This project is licensed under the MIT License.
````