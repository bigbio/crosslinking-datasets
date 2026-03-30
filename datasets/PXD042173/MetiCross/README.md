# PXD042173: Proteome-scale recombinant standard datasets for XL-MS

This directory contains enhanced metadata and configuration files for **PXD042173**, a crosslinking mass spectrometry (XL-MS) dataset from PRIDE. The data has been processed using the **XLMS-PPI-working-group pipeline** to extract structured metadata and generate Xi search engine configuration files.

**Project Information:**
- **Accession**: PXD042173
- **Title**: Proteome-scale recombinant standard datasets for XL-MS
- **Crosslinker**: DSSO (MS-cleavable)
- **Quencher**: Tris-HCl, 20 mM (pH 8.0)
- **Digestion**: Lys-C, Trypsin
- **Instrument**: Orbitrap Fusion Lumos
- **Source Repository**: [XLMS-PPI-working-group](https://github.com/NCEMS/XLMS-PPI-working-group)

### Quick Dataset Summary

| Property | Value |
|----------|-------|
| **PXD Accession** | PXD042173 |
| **Dataset Type** | Crosslinking Mass Spectrometry (XL-MS) |
| **Title** | Proteome-scale recombinant standard datasets for XL-MS |
| **Organism** | Homo sapiens (Human) - recombinant proteins |
| **Crosslinker** | DSSO (MS-cleavable) |
| **Quencher** | Tris-HCl, 20 mM (pH 8.0) |
| **Digestion** | Lys-C (4h, 37°C) + Trypsin (overnight, 37°C) |
| **Instrument** | Orbitrap Fusion Lumos with FAIMS Pro |
| **Fragmentation** | Stepped HCD (27 ± 6%) |
| **Data Files** | 5 batches, 64 proteins per batch |
| **Interactions** | Up to 224 allowed PPIs per batch |
| **Processing Date** | March 25, 2026 |
| **Xi Configs Available** | ✓ Yes (crosslinking + linear) |
| **Enhanced Metadata** | ✓ Yes (LLM-extracted) |

---

## Table of Contents

- [Overview](#overview)
- [XLMS-PPI Pipeline Components](#xlms-ppi-pipeline-components)
- [Xi Configuration Files](#xi-configuration-files)
- [Enhanced Metadata](#enhanced-metadata)
- [Using This Data](#using-this-data)
- [Supported Crosslinkers & Quenchers](#supported-crosslinkers--quenchers)
- [Scientific Background](#scientific-background)
- [XLMS-PPI Working Group](#xlms-ppi-working-group)
- [References](#references)
- [Quick Reference](#quick-reference)

---

## Overview

This dataset (PXD042173) is part of the crosslinking mass spectrometry standardization effort coordinated by the NCEMS XLMS-PPI Working Group. The data represents a proteome-scale recombinant standard for XL-MS, consisting of systematically mixed and cross-linked recombinant human proteins.

**Key Features of this Dataset:**
- 5 raw datasets (batches 1-5)
- 64 randomly selected human proteins per batch
- Up to 224 allowed protein-protein interactions per dataset
- DSSO crosslinker with Tris-HCl quenching
- MS2-level complexity comparable to typical proteome-wide XL-MS experiments

The data has been enhanced with automated metadata extraction and search engine configuration generation to facilitate reproducible analysis and integration with downstream applications.

---

## XLMS-PPI Pipeline Components

This dataset was processed using the **XLMS-PPI-working-group intelligent metadata compilation pipeline**, which performs:

### 1. Automated Metadata Extraction from PRIDE
- Fetches project metadata directly from PRIDE API
- Extracts sample characteristics, protocols, and instrument information
- Parses publication metadata from associated publications (PubMed/PMC)

### 2. LLM-Enhanced Metadata Processing
- Uses GPT-4o-mini to extract and standardize structured metadata from publications
- Intelligent parsing of crosslinker specifications, digestion enzymes, modifications
- Validation against known parameter databases (15+ crosslinkers, 3+ quenchers)

### 3. Xi Search Engine Configuration Generation
- **Automatically generates Xi search engine configuration files**
- Creates paired configurations: one for crosslinking analysis, one for linear peptide analysis
- Intelligent parameter extraction based on detected experimental conditions

**Processing Stages:**
```
Stage 1: PRIDE Fetch → Retrieve project metadata
Stage 2: Publication Extraction → Find associated publications  
Stage 3: Publication Text Fetch → Download full publication content
Stage 4: LLM Query & Parsing → Extract structured metadata with GPT-4o-mini
Stage 5: Compilation → Combine all metadata sources
Stage 6: Xi Config Generation → Generate search engine configurations
```

For complete pipeline documentation, see the [XLMS-PPI-working-group repository](https://github.com/NCEMS/XLMS-PPI-working-group).

---

## Xi Configuration Files

The `configs/` directory contains automatically generated Xi search engine configuration files optimized for this dataset:

### xi_crosslinking.conf
Configuration for crosslinked peptide detection with DSSO:

**Key Parameters:**
- **Crosslinker**: DSSO (MS-cleavable) on K, nterm, S, T, Y
- **Tolerances**: 10 ppm precursor, 20 ppm fragment
- **Fixed Modifications**: Carbamidomethyl (C, +57.021464)
- **Variable Modifications**:
  - Oxidation (M, +15.99491463)
  - DSSO + Tris mono-links (K, nterm, S, T, Y, +279.077658 Da)
- **Digestion**: Trypsin, Lys-C (3 missed cleavages)
- **Search Mode**: `TOPMATCHESONLY:true` (optimized for crosslinked peptides)

**Mono-Quench Modifications:**
The configuration automatically includes DSSO+Tris-HCl mono-link (dead-end) modifications based on the detected quencher. This accounts for unreacted crosslinker arms that were quenched during sample preparation:

```properties
modification:variable::SYMBOLEXT:dsso_tris;MODIFIED:K;DELTAMASS:279.077658
modification:variable::SYMBOLEXT:dsso_tris;MODIFIED:nterm;DELTAMASS:279.077658
modification:variable::SYMBOLEXT:dsso_tris;MODIFIED:S;DELTAMASS:279.077658
modification:variable::SYMBOLEXT:dsso_tris;MODIFIED:T;DELTAMASS:279.077658
modification:variable::SYMBOLEXT:dsso_tris;MODIFIED:Y;DELTAMASS:279.077658
```

### xi_linear.conf
Configuration for linear (non-crosslinked) peptide detection:

**Key Parameters:**
- **Tolerances**: Same as crosslinking config (10 ppm / 20 ppm)
- **Fixed Modifications**: Carbamidomethyl (C)
- **Variable Modifications**: Oxidation (M) only
- **Digestion**: Same enzymes as crosslinking config
- **Search Mode**: `TOPMATCHESONLY:false` (standard peptide search)

Both configurations were automatically generated based on LLM-extracted metadata from the publication and validated against experimental parameters.

---

## Enhanced Metadata

The `enhanced/` directory contains compiled metadata from multiple sources:

### metadata.json
Comprehensive JSON file containing:
- **PRIDE metadata**: Project description, protocols, instruments, publications
- **LLM-extracted features**: 
  - Crosslinker specifications (name: DSSO, targets: K/nterm/S/T/Y, cleavability: yes)
  - Digestion enzyme parameters (Lys-C, Trypsin with conditions)
  - Quencher information (Tris-HCl, 20 mM, pH 8.0)
  - Sample modifications
  - Instrument configurations
- **Processing metadata**: Stage status, timestamps, data sources

**Directory Structure:**
```
PXD042173/
├── README.md                               # This file
├── configs/                                # Xi search engine configurations
│   ├── xi_crosslinking.conf               # Crosslinked peptide search config
│   └── xi_linear.conf                     # Linear peptide search config
├── enhanced/                               # Compiled metadata
│   └── metadata.json                      # Complete enhanced metadata
├── llm/                                    # LLM extraction results
│   └── responses.json                     # GPT-4o-mini extracted fields
├── pmc/                                    # Publication metadata
│   └── full_text.json                     # PMC publication content
├── pride/                                  # PRIDE API data
│   └── project_details.json               # PRIDE project metadata
└── ncbi/                                   # NCBI data (if applicable)
```

**Key Extracted Fields (from LLM):**
- `comment_cross_linker`: "DSSO"
- `comment_quenching_reagent`: "Tris-HCl, 20 mM (pH 8.0)"
- `comment_cleavage_agent_details`: Lys-C (4h, 37°C), Trypsin (overnight, 37°C)
- `comment_instrument`: "Orbitrap Fusion Lumos with FAIMS Pro device"
- `comment_fragmentation_method`: "Stepped collision energy HCD (27 ± 6%)"

---

## Using This Data

### For Xi Search Engine Analysis

The generated configuration files can be used directly with the Xi search engine:

1. **Download Xi search engine** from [Xi homepage](http://rappsilberlab.org/software/xi/)

2. **Use the crosslinking configuration** for crosslinked peptide identification:
   ```bash
   java -jar Xi.jar --config=configs/xi_crosslinking.conf \
        --fasta=path/to/proteins.fasta \
        --peaks=path/to/spectra.mgf \
        --output=results/
   ```

3. **Use the linear configuration** for linear peptide validation:
   ```bash
   java -jar Xi.jar --config=configs/xi_linear.conf \
        --fasta=path/to/proteins.fasta \
        --peaks=path/to/spectra.mgf \
        --output=results/
   ```

### Accessing Enhanced Metadata

The enhanced metadata can be accessed programmatically:

```python
import json

# Load enhanced metadata
with open('enhanced/metadata.json', 'r') as f:
    metadata = json.load(f)

# Access LLM-extracted features
llm_data = metadata['data']['llm_responses']
crosslinker = llm_data['comment_cross_linker']  # "DSSO"
quencher = llm_data['comment_quenching_reagent']  # "Tris-HCl, 20 mM"
enzymes = llm_data['comment_cleavage_agent_details']

# Access PRIDE metadata
pride_data = metadata['data']['pride_data']
title = pride_data['title']
protocols = pride_data['sampleProcessingProtocol']
```

### Reproducing the Metadata Extraction

To re-run the XLMS-PPI pipeline on this or other datasets:

```bash
# Clone the XLMS-PPI repository
git clone https://github.com/NCEMS/XLMS-PPI-working-group.git
cd XLMS-PPI-working-group

# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="your-openai-key"
export NCBI_API_KEY="your-ncbi-key"  # Optional

# Process PXD042173
python src/main.py --pxd PXD042173 --verbose
```

---

## Supported Crosslinkers & Quenchers

### Crosslinkers (14+ supported in XLMS-PPI pipeline)

**Symmetric crosslinkers:**
- **DSSO** (disuccinimidyl sulfoxide) - MS-cleavable, targets K/nterm/S/T/Y
- **BS³** (bis(sulfosuccinimidyl)suberate) - Non-cleavable, targets K/nterm
- **DSS** (disuccinimidyl suberate) - Non-cleavable, targets K/nterm
- **DSG** (disuccinimidyl glutarate)
- **DSBU** (disuccinimidyl dibutyric urea)
- **EDC** (1-ethyl-3-(3-dimethylaminopropyl)carbodiimide)
- **MBS** (m-maleimidobenzoyl-N-hydroxysuccinimide ester)
- **DMA** (dimethyl adipimidate)
- **Formaldehyde** - Reversible crosslinker
- **Glutaraldehyde**

**Photo-crosslinkers:**
- **Photo-DMAB**
- **AzP** (azide-phenol)
- **AzPC** (azide-phenol-coumarin)

Each crosslinker definition includes full name, short name, Xi format class, monoisotopic mass, linked amino acids, and cleavage stubs (if applicable).

### Quenchers (3 types with 15+ combinations)

| Quencher | Crosslinkers Supported | Example Mono-Link Mass |
|----------|------------------------|------------------------|
| **Tris** | DSSO, BS³, DSS, DSBU | DSSO: 279.08 Da, BS³: 259.14 Da |
| **Ammonium bicarbonate (ABC)** | DSSO, BS³, DSS, DSBU | DSSO: 263.06 Da, BS³: 243.13 Da |
| **Glycine** | Formaldehyde | FA: 75.03 Da |

**For PXD042173:** DSSO + Tris-HCl mono-link modifications are included in the Xi configuration files.

---

## Scientific Background

### Crosslinking Mass Spectrometry (XL-MS)

Crosslinking mass spectrometry (XL-MS) is a powerful structural proteomics method that provides high-resolution structural information about complex mixtures of proteins in their native physiological context.[1],[2],[3] The method works by:

1. **Chemical crosslinking**: Reactive amino acid residues that are close in 3-D space are covalently linked
2. **Enzymatic digestion**: Crosslinked proteins are digested into peptides
3. **MS analysis**: Crosslinked peptides are identified by mass spectrometry
4. **Structural inference**: Distance constraints between crosslinked residues inform protein structure and interactions

**Key advantages:**
- Captures protein-protein interactions (PPIs) in native context
- Provides distance constraints for structural modeling
- Can identify transient or weak interactions
- Enables integrative modeling with AlphaFold3 predictions

This is conceptually similar to Hi-C for chromatin,[4] but applied to protein complexes.

### MS-Cleavable Crosslinkers

**DSSO** (used in PXD042173) is an MS-cleavable crosslinker that fragments during MS/MS analysis:[5]

- **Advantage**: Simplified identification of crosslinked peptides
- **Cleavage**: Generates characteristic fragment patterns in MS/MS spectra
- **Targets**: K (lysine), nterm (N-terminus), S/T/Y (serine/threonine/tyrosine)
- **Mass**: 158.0038 Da (spacer arm)

The Xi search engine is specifically designed to utilize these cleavage patterns for improved crosslink identification.

---

## XLMS-PPI Working Group

This dataset is part of the **Intelligent Metadata Compilation for Crosslinking Mass Spectrometry Data** project aimed at standardizing and integrating publicly available XL-MS datasets from PRIDE.

**Project Goals:**
- Standardize, combine, and integrate existing crosslinking datasets
- Create a meta-dataset cataloging protein-protein interactions (PPIs) in human and model organisms
- Cross-validate with AlphaFold3 structural predictions
- Integrate findings into the EBI Complex Portal

**Working Group Leadership:**
- Lead: Stephen D. Fried, Johns Hopkins University (sdfried@jhu.edu)
- Co-Lead: Yasset Perez-Riverol, EMBL-EBI (yperez@ebi.ac.uk)
- Co-Lead: Henning Hermjakob, EMBL-EBI (hhe@ebi.ac.uk)

**NCEMS Staff:**
- Staff Scientist: Ian Sitarik, Penn State University (ims86@psu.edu)
- Project Coordinator: Maowei Dong, Penn State University (mod5361@psu.edu)

**Communication:**
- GitHub: https://github.com/NCEMS/XLMS-PPI-working-group
- [Zoom Meeting](https://psu.zoom.us/j/2163369137?pwd=K0l5Mmo2ZGpFSitwTVVBOUljaE1Fdz09)
- [Slack Channel](https://friedlab.slack.com/archives/C09L906UPUH)

---

## References

### Crosslinking Mass Spectrometry

[1]: Graziadei, A. & Rappsilber, J. Leveraging crosslinking mass spectrometry in structural and cell biology. *Structure* **30**, 37–54 (2022).

[2]: Sinz, A. Cross-Linking/Mass Spectrometry for Studying Protein Structures and Protein–Protein Interactions: Where Are We Now and Where Should We Go from Here? *Angew. Chem. Int. Ed.* **57**, 6390–6396 (2018).

[3]: Leitner, A., Faini, M., Stengel, F. & Aebersold, R. Crosslinking and Mass Spectrometry: An Integrated Technology to Understand the Structure and Function of Molecular Machines. *Trends Biochem. Sci.* **41**, 20–32 (2016).

[4]: Eagen, K. P. Principles of Chromosome Architecture Revealed by Hi-C. *Trends Biochem. Sci.* **43**, 469–478 (2018).

[5]: Matzinger, M. & Mechtler, K. Cleavable Cross-Linkers and Mass Spectrometry for the Ultimate Task of Profiling Protein–Protein Interaction Networks in Vivo. *J. Proteome Res.* **20**, 78–93 (2021).

### Tools & Workflows

**Xi Search Engine**: Rappsilber Lab - Crosslinking-specific search engine

**XLMS-PPI Pipeline**: NCEMS - Intelligent metadata compilation for crosslinking data

**PRIDE Archive**: ProteomeXchange Consortium - Public proteomics data repository

---

## Credits & Acknowledgments

**XLMS-PPI Working Group**: NCEMS crosslinking standardization initiative
- Stephen D. Fried (Johns Hopkins University)
- Yasset Perez-Riverol, Henning Hermjakob (EMBL-EBI)
- Ian Sitarik, Maowei Dong (Penn State University)

**Key Tools**:
- **Xi Search Engine**: Rappsilber Lab, University of Edinburgh
- **GPT-4o-mini**: OpenAI - LLM for metadata extraction

**Data Sources**:
- **PRIDE Archive**: ProteomeXchange Consortium
- **PubMed Central**: NCBI
- **UniProt**: Universal Protein Resource

---

## License

This project is available under the MIT License.

---

## Quick Reference

```bash
# XLMS-PPI Pipeline - Generate Xi configs and enhanced metadata
git clone https://github.com/NCEMS/XLMS-PPI-working-group.git
cd XLMS-PPI-working-group
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
python src/main.py --pxd PXD042173 --verbose

# Output:
# - configs/xi_crosslinking.conf (DSSO + Tris mono-links)
# - configs/xi_linear.conf
# - enhanced/metadata.json (complete metadata compilation)
```

---

**Last Updated:** March 30, 2026  
**XLMS-PPI Pipeline Version:** 1.1 (Xi Config Generation with Mono-Quench Support)

---

**For Questions or Issues:**
- XLMS-PPI Pipeline: Contact Ian Sitarik (ims86@psu.edu) or open an issue at https://github.com/NCEMS/XLMS-PPI-working-group
