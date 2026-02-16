# IDC + TIAToolbox Tutorials

Working examples demonstrating [TIAToolbox](https://github.com/TissueImageAnalytics/tiatoolbox) computational pathology analysis tools applied to slide microscopy data from [NCI Imaging Data Commons (IDC)](https://portal.imaging.datacommons.cancer.gov/).

## Overview

[TIAToolbox](https://tia-toolbox.readthedocs.io/) is a comprehensive Python library for computational pathology providing WSI reading, stain normalization, tissue detection, patch classification, semantic segmentation, nucleus instance segmentation, and more -- all with pretrained deep learning models.

[Imaging Data Commons (IDC)](https://imaging.datacommons.cancer.gov/) hosts thousands of publicly accessible slide microscopy images in DICOM WSI format, along with annotations and segmentations. No authentication is required to access IDC data.

TIAToolbox's `DICOMWSIReader` can directly read IDC's DICOM WSI files, making these two tools naturally complementary. These tutorials show you how to use them together.

## Notebooks

| # | Notebook | TIAToolbox Tools | IDC Data | GPU |
|---|---------|-----------------|----------|-----|
| 01 | [Reading IDC Slides](notebooks/01_reading_idc_slides_with_tiatoolbox.ipynb) | WSIReader, DICOMWSIReader | CPTAC lung | No |
| 02 | [Tissue Masking & Patches](notebooks/02_tissue_masking_and_patch_extraction.ipynb) | OtsuTissueMasker, PatchExtractor | CPTAC/TCGA | No |
| 03 | [Stain Normalization](notebooks/03_stain_normalization.ipynb) | Macenko, Reinhard, Vahadane | Two collections | No |
| 04 | [Patch Classification](notebooks/04_patch_classification.ipynb) | PatchPredictor | TCGA colorectal | Recommended |
| 05 | [Semantic Segmentation](notebooks/05_semantic_segmentation.ipynb) | SemanticSegmentor | TCGA breast | Recommended |
| 06 | [Nucleus Segmentation](notebooks/06_nucleus_instance_segmentation.ipynb) | NucleusInstanceSegmentor | TCGA | Required |
| 07 | [Comparing with IDC Annotations](notebooks/07_comparing_with_idc_annotations.ipynb) | HoVer-Net, SQLiteStore | TCGA + Pan-Cancer ANN | Recommended |

## Quick Start

Click the "Open in Colab" badge at the top of any notebook to run it directly in Google Colab. No local setup required.

To run locally:

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

## Prerequisites

- A Google account (for Colab) or local Python 3.9+ environment
- No authentication needed for IDC data access
- GPU runtime recommended for notebooks 04-07 (free T4 GPU available on Colab)

## Estimated Data Downloads

| Notebook | Download Size |
|----------|--------------|
| 01 | ~300 MB (1 slide) |
| 02 | ~300 MB (1 slide) |
| 03 | ~600 MB (2 slides) |
| 04 | ~300 MB + model weights |
| 05 | ~300 MB + model weights |
| 06 | ~300 MB + model weights |
| 07 | ~500 MB + model weights |

## Resources

- [IDC Portal](https://portal.imaging.datacommons.cancer.gov/) - Interactive data exploration
- [IDC Documentation](https://learn.canceridc.dev/) - IDC learning resources
- [IDC Tutorials](https://github.com/ImagingDataCommons/IDC-Tutorials) - More IDC tutorials
- [IDC Forum](https://discourse.canceridc.dev/) - Community support
- [TIAToolbox Documentation](https://tia-toolbox.readthedocs.io/) - TIAToolbox API reference
- [TIAToolbox Examples](https://github.com/TissueImageAnalytics/tiatoolbox/tree/develop/examples) - Official TIAToolbox examples

## How This Repository Was Created

This repository was generated on **February 16, 2026** using [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's AI coding agent, model: Claude Opus 4.6).

**Process:**
1. Claude Code researched TIAToolbox capabilities (via web search of GitHub, readthedocs, published papers) and IDC slide microscopy data (via the [IDC Claude skill](https://github.com/ImagingDataCommons/idc-claude-skill))
2. A plan was designed matching TIAToolbox tools to appropriate IDC collections (e.g., Kather100K model with TCGA colorectal data, BCSS model with TCGA breast data)
3. All 7 notebooks, README, and supporting files were generated in a single session
4. Existing [IDC-Tutorials](https://github.com/ImagingDataCommons/IDC-Tutorials) pathomics notebooks were used as reference for IDC API conventions

**Colab testing (in progress):** Notebook 01 has been partially tested on Colab. Several dependency and API issues were discovered and fixed (numpy binary incompatibility, missing OpenSlide, zarr/numcodecs version conflict, DICOMWSIReader not populating `objective_power`, `read_rect` coordinate system). Notebooks 02-07 still need end-to-end testing. See [dev/PROCESS.md](dev/PROCESS.md) for the full development log including issues found, fixes applied, and remaining limitations.

## Citations

If you use these tutorials or the underlying tools in your work, please cite:

**IDC:**
> Fedorov, A., et al. "National Cancer Institute Imaging Data Commons: Toward Transparency, Reproducibility, and Scalability in Imaging Artificial Intelligence." *RadioGraphics* 43.12 (2023). https://doi.org/10.1148/rg.230180

**TIAToolbox:**
> Pocock, J., et al. "TIAToolbox as an end-to-end library for advanced tissue image analytics." *Communications Medicine* 2, 120 (2022). https://doi.org/10.1038/s43856-022-00186-5

## License

[Apache 2.0](LICENSE)
