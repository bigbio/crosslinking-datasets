# Crosslinking Datasets

This directory contains SDRF files for crosslinking-annotated datasets from ProteomeXchange.

## Structure

Each dataset has its own subdirectory named after its ProteomeXchange accession ID (PXD number):

```
datasets/
├── PXD000001/
│   └── PXD000001.sdrf.tsv
├── PXD000002/
│   └── PXD000002.sdrf.tsv
└── ...
```

## Dataset Organization

Each dataset directory should contain:
- **[Accession].sdrf.tsv**: The SDRF file describing the dataset
- **README.md** (optional): Additional information about the dataset, such as publication references, special notes, or dataset-specific details

## Adding a New Dataset

To add a new crosslinking dataset:

1. Create a new directory with the ProteomeXchange accession ID:
   ```bash
   mkdir -p datasets/PXD012345
   ```

2. Create the SDRF file in that directory:
   ```bash
   cp templates/sdrf-template.tsv datasets/PXD012345/PXD012345.sdrf.tsv
   ```

3. Edit the SDRF file with your dataset information

4. Validate the SDRF file:
   ```bash
   parse_sdrf validate-sdrf --sdrf_file datasets/PXD012345/PXD012345.sdrf.tsv
   ```

5. Commit and push your changes

## Dataset List

Currently available datasets will be listed here as they are added to the repository.

<!-- 
Template for adding dataset entries:
### PXD000001
- **Title**: [Dataset title]
- **Publication**: [DOI or reference]
- **Organism**: [Species]
- **Crosslinker**: [Type of crosslinker used]
- **Description**: [Brief description of the experiment]
-->

## Validation

All SDRF files in this directory should:
- Follow the MAGE-TAB SDRF format
- Include all required columns for crosslinking experiments
- Use appropriate ontology terms
- Pass validation with sdrf-pipelines tools

## Resources

- [ProteomeXchange](http://www.proteomexchange.org/)
- [PRIDE Archive](https://www.ebi.ac.uk/pride/)
- [sdrf-pipelines](https://github.com/bigbio/sdrf-pipelines)
