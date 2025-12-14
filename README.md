# Crosslinking Datasets Repository

This repository contains SDRF (Sample and Data Relationship Format) files for crosslinking-annotated datasets in ProteomeXchange.

## Purpose

The goal of this repository is to provide standardized metadata annotations for crosslinking proteomics datasets submitted to ProteomeXchange. Each dataset has its own SDRF file that describes the experimental design, samples, and data relationships according to the MAGE-TAB SDRF format.

## Repository Structure

```
crosslinking-datasets/
├── datasets/
│   ├── PXD000001/
│   │   └── PXD000001.sdrf.tsv
│   ├── PXD000002/
│   │   └── PXD000002.sdrf.tsv
│   └── ...
├── templates/
│   └── sdrf-template.tsv
└── README.md
```

## SDRF Format

SDRF (Sample and Data Relationship Format) is a tab-delimited format that describes:
- Sample characteristics and experimental variables
- Protocols and protocol parameters
- Raw and processed data files
- Relationships between samples and data files

### Required Columns

Common SDRF columns for crosslinking experiments include:
- `source name`: Biological source identifier
- `characteristics[organism]`: Species/organism
- `characteristics[cell type]`: Cell type (if applicable)
- `characteristics[disease]`: Disease state (if applicable)
- `comment[data file]`: Raw data file names
- `comment[fraction identifier]`: Fraction information
- `comment[technical replicate]`: Technical replicate number
- `comment[biological replicate]`: Biological replicate number
- `comment[label]`: Labeling information
- `comment[instrument]`: Mass spectrometry instrument
- `comment[modification parameters]`: PTMs and crosslinker information
- `comment[cleavage agent details]`: Protease used

## Adding a New Dataset

1. Create a new directory under `datasets/` with the ProteomeXchange accession ID (e.g., `PXD012345`)
2. Create an SDRF file named `<accession>.sdrf.tsv` in that directory
3. Follow the SDRF format guidelines and use the template as reference
4. Ensure all required columns are present and properly formatted
5. Validate the SDRF file using appropriate validation tools

## SDRF Validation

SDRF files should be validated before submission. You can use tools like:
- [sdrf-pipelines](https://github.com/bigbio/sdrf-pipelines) for validation
- ProteomeXchange submission validation tools

**Automated Validation**: All pull requests that modify `*.sdrf.tsv` files are automatically validated using the sdrf-pipelines tool before they can be merged into the main branch. The validation checks:
- File format and structure
- Required columns presence
- Ontology term correctness
- Data consistency

## Contributing

To contribute a new SDRF file:
1. Fork this repository
2. Add your SDRF file following the structure above
3. Submit a pull request with a description of the dataset
4. Ensure your SDRF file passes automated validation

## Resources

- [MAGE-TAB SDRF Specification](http://fged.org/projects/mage-tab/)
- [ProteomeXchange](http://www.proteomexchange.org/)
- [PRIDE Database](https://www.ebi.ac.uk/pride/)
- [sdrf-pipelines Documentation](https://github.com/bigbio/sdrf-pipelines)

## Contact

For questions or issues, please open an issue in this repository.
