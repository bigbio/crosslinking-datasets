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

   # Validate against ms-proteomics, crosslinking, and species templates
   parse_sdrf validate-sdrf --sdrf_file datasets/PXD012345/PXD012345.sdrf.tsv \
     -t ms-proteomics -t crosslinking -t human
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
- `comment[modification parameters]` (PTMs in `NT=;AC=;TA=;MT=` format)
- `comment[cleavage agent details]`
- `comment[cross-linker]` (cross-linker reagent using XLMOD ontology)
- `comment[chemical cross-linking coupled with ms]` (XL-MS experiment type)

### Crosslinker Information
Crosslinker information should be specified:
1. In `comment[cross-linker]` using XLMOD ontology terms (e.g., `NT=DSS;AC=XLMOD:02001`)
2. As a modification parameter if it introduces a mass shift (e.g., `NT=DSS crosslink;AC=UNIMOD:1896;TA=K;MT=Variable`)

### Ontology Terms
Use standard ontology terms in `NT=;AC=` format:
- **PSI-MS** (Proteomics Standards Initiative Mass Spectrometry): `MS:` prefix
  - Example: `NT=Trypsin;AC=MS:1001251`
- **UNIMOD**: `UNIMOD:` prefix for modifications
  - Example: `NT=Oxidation;AC=UNIMOD:35;TA=M;MT=Variable`
- **XLMOD**: `XLMOD:` prefix for cross-linkers
  - Example: `NT=DSS;AC=XLMOD:02001`
- **PRIDE**: `PRIDE:` prefix for proteomics-specific terms
- **NCBITaxon**: `NCBITaxon:` prefix for organisms
  - Example: `NT=Homo sapiens;AC=NCBITaxon:9606`
- **EFO**: `EFO:` prefix for experimental factors

Format: `NT=<term name>;AC=<ontology>:<id>[;TA=<target>;MT=<modification type>]`

Example: `NT=Oxidation;AC=UNIMOD:35;TA=M;MT=Variable`

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

**Automated Validation**: All pull requests that modify `*.sdrf.tsv` files will be automatically validated by our GitHub Actions workflow. The workflow:
- Detects all changed SDRF files in the PR
- Validates each file using `sdrf-pipelines`
- Reports any validation errors as PR check failures
- Must pass before the PR can be merged

You can validate locally before pushing using:
```bash
parse_sdrf validate-sdrf --sdrf_file datasets/PXD012345/PXD012345.sdrf.tsv \
  -t ms-proteomics -t crosslinking -t human
```

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
