# SDRF Template for Crosslinking Experiments

This directory contains template SDRF files that can be used as a starting point for creating SDRF files for new crosslinking datasets.

## Template File

**sdrf-template.tsv** - A basic template for crosslinking proteomics experiments

### How to Use the Template

1. Copy the template file to your dataset directory
2. Rename it to match your ProteomeXchange accession (e.g., `PXD012345.sdrf.tsv`)
3. Fill in the appropriate values for your experiment:
   - Replace sample names with your actual sample identifiers
   - Update organism, cell type, and disease information
   - Add rows for all samples in your experiment
   - Update modification parameters with your specific crosslinker
   - List all raw data files
   - Add file URIs pointing to the actual data location

### Column Descriptions

#### Required Sample Information
- **source name**: Unique identifier for each biological sample
- **characteristics[organism]**: Species name (use scientific name, e.g., "Homo sapiens")
- **characteristics[organism part]**: Tissue or sample type
- **characteristics[cell type]**: Specific cell line or cell type
- **characteristics[disease]**: Disease state or "normal" for healthy samples
- **characteristics[biological replicate]**: Biological replicate number

#### Technical Metadata
- **comment[technical replicate]**: Technical replicate number
- **comment[fraction identifier]**: Fraction number if fractionation was performed
- **comment[label]**: Labeling strategy (e.g., "label free sample", "TMT10plex")

#### Instrument and Analysis Parameters
- **comment[instrument]**: Mass spectrometry instrument model
- **comment[modification parameters]**: Variable modifications (oxidation, deamidation, etc.)
  - Format: `NT:<id>; NT:<modification name>; TA:<mass>`
- **comment[modification parameters]** (crosslinker): Crosslinker modification
  - Format: `NT:<id>; NT:<crosslinker name>; TA:<mass>`
- **comment[cleavage agent details]**: Protease used for digestion
  - Format: `NT:<id>; NT:<protease name>`

#### Data Files
- **comment[data file]**: Raw data file name
- **comment[file uri]**: Full URI/URL to access the data file

#### Experimental Factors
- **factor value[crosslinker]**: Type of crosslinker used (e.g., DSS, BS3, EDC)

### Common Crosslinkers

- **DSS** (Disuccinimidyl suberate): Mass delta 138.06808 Da
- **BS3** (Bis(sulfosuccinimidyl)suberate): Mass delta 138.06808 Da
- **EDC** (1-Ethyl-3-(3-dimethylaminopropyl)carbodiimide): Zero-length crosslinker
- **DSSO** (Disuccinimidyl sulfoxide): Mass delta 158.0038 Da (before fragmentation)
- **DSBU** (Disuccinimidyl dibutyric urea): Mass delta 196.0848 Da

### Ontology Terms

Use appropriate ontology terms where possible:
- **MS ontology (MS)** for mass spectrometry instruments and methods
- **PRIDE ontology (PRIDE)** for proteomics-specific terms
- **UNIMOD** for modifications
- **EFO** (Experimental Factor Ontology) for biological characteristics

### Validation

Before submitting, validate your SDRF file using:
```bash
pip install sdrf-pipelines
parse_sdrf validate-sdrf --sdrf_file your_file.sdrf.tsv
```

### Example Datasets

Check the `datasets/` directory for real-world examples of SDRF files for crosslinking experiments.
