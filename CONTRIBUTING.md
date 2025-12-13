# Contributing to Crosslinking Datasets

Thank you for your interest in contributing SDRF files for crosslinking datasets! This document provides guidelines for contributing to this repository.

## How to Contribute

### Adding a New Dataset

1. **Fork the repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/crosslinking-datasets.git
   cd crosslinking-datasets
   ```

2. **Create a new branch**
   ```bash
   git checkout -b add-pxd012345
   ```

3. **Add your dataset**
   ```bash
   # Create dataset directory
   mkdir -p datasets/PXD012345
   
   # Copy and edit the template
   cp templates/sdrf-template.tsv datasets/PXD012345/PXD012345.sdrf.tsv
   ```

4. **Fill in the SDRF file**
   - Edit `datasets/PXD012345/PXD012345.sdrf.tsv` with your dataset information
   - Include all samples and data files
   - Use appropriate ontology terms
   - Ensure proper formatting (tab-separated)

5. **Validate your SDRF file**
   ```bash
   # Install sdrf-pipelines if needed
   pip install sdrf-pipelines
   
   # Validate
   parse_sdrf validate-sdrf --sdrf_file datasets/PXD012345/PXD012345.sdrf.tsv
   ```

6. **Commit your changes**
   ```bash
   git add datasets/PXD012345/
   git commit -m "Add SDRF for PXD012345"
   ```

7. **Push and create a pull request**
   ```bash
   git push origin add-pxd012345
   # Then create a PR via GitHub UI
   ```

## SDRF File Requirements

### File Naming
- SDRF files must be named: `<PXD_ACCESSION>.sdrf.tsv`
- Example: `PXD012345.sdrf.tsv`

### File Format
- Tab-separated values (TSV)
- UTF-8 encoding
- Unix line endings (LF)

### Required Columns
At minimum, your SDRF file should include:
- `source name`
- `characteristics[organism]`
- `comment[data file]`
- `comment[instrument]`
- `comment[modification parameters]` (including crosslinker)
- `comment[cleavage agent details]`

### Crosslinker Information
Crosslinker information should be specified:
1. As a modification parameter with proper ontology terms
2. As a factor value if it's an experimental variable

### Ontology Terms
Use standard ontology terms when available:
- **PSI-MS** (Proteomics Standards Initiative Mass Spectrometry): `MS:` prefix
  - Example: `MS:1001251; Trypsin`
- **UNIMOD**: `UNIMOD:` prefix for modifications
  - Example: `UNIMOD:1896; DSS crosslink; TA:138.06808`
- **PRIDE**: `PRIDE:` prefix for proteomics-specific terms
- **NCBITaxon**: `NCBITaxon:` prefix for organisms
  - Example: `NCBITaxon:9606; Homo sapiens`
- **EFO**: `EFO:` prefix for experimental factors
  - Example: `EFO:0000001; experimental factor`

Format: `<ontology>:<id>; <term name>; [TA:<value>]`

Example: `MS:1001460; Oxidation; TA:15.99491`

## Quality Guidelines

### Completeness
- Include all samples from the dataset
- List all raw data files
- Provide complete technical metadata

### Accuracy
- Verify organism names (use scientific names)
- Double-check file names match actual data files
- Ensure modification masses are correct
- Confirm instrument names are accurate

### Consistency
- Use consistent naming conventions
- Apply the same format for similar values
- Follow the template structure

## Validation

Before submitting, ensure your SDRF file:
1. ✓ Passes sdrf-pipelines validation
2. ✓ Contains no trailing spaces or tabs
3. ✓ Uses proper ontology terms
4. ✓ Includes all required columns
5. ✓ Has no empty required fields

## Pull Request Guidelines

### PR Title
Use format: `Add SDRF for PXD012345: [Brief dataset description]`

### PR Description
Include:
- ProteomeXchange accession (PXD number)
- Dataset title
- Publication DOI (if available)
- Organism(s)
- Crosslinker type(s)
- Number of samples
- Any special notes or considerations

### Example PR Description
```
Add SDRF for PXD012345: Crosslinking study of human protein complexes

- **Accession**: PXD012345
- **Title**: Systematic analysis of protein complexes using DSS crosslinking
- **Publication**: https://doi.org/10.1234/example
- **Organism**: Homo sapiens
- **Crosslinker**: DSS
- **Samples**: 12 biological replicates
- **Notes**: Includes fractionation data
```

## Getting Help

If you need assistance:
1. Check the [README.md](README.md) for documentation
2. Review the [template README](templates/README.md) for guidance
3. Look at existing datasets in the `datasets/` directory
4. Open an issue for questions or clarification

## Code of Conduct

- Be respectful and professional
- Provide accurate information
- Follow the contribution guidelines
- Help others in the community

## License

By contributing to this repository, you agree that your contributions will be licensed under the same license as the repository.

Thank you for contributing to the crosslinking datasets repository!
