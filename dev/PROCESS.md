# Development Process

This document records how this repository was created, the tools and methods used, what was learned about TIAToolbox in the context of IDC, and known limitations.

## How This Repository Was Created

### Date

Initial creation: **February 16, 2026**

### Tools Used

- **Claude Code** (Anthropic's CLI agent, model: Claude Opus 4.6) — used to research both TIAToolbox and IDC, design the project structure, and generate all notebooks and supporting files
- **IDC imaging-data-commons skill** — a Claude Code skill (from [idc-claude-skill](https://github.com/ImagingDataCommons/idc-claude-skill)) that provides structured knowledge about IDC's data model, `idc-index` API, index tables (`sm_index`, `ann_index`, `ann_group_index`, `seg_index`, etc.), SQL query patterns, download workflows, and digital pathology guide
- **`idc-index` 0.11.9** (IDC data version v23) — installed locally; used for verifying API patterns and table schemas

### Process

1. **Research phase**: Claude Code explored TIAToolbox capabilities via web search (GitHub, PyPI, readthedocs, published papers) and IDC slide microscopy data via the imaging-data-commons skill. Three parallel exploration agents researched:
   - TIAToolbox analysis tools inventory (all modules, classes, pretrained models)
   - TIAToolbox data format support (WSI readers, DICOM support, dependencies)
   - IDC slide microscopy collections, annotation tables, and digital pathology workflows

2. **Design phase**: A planning agent synthesized the research into a detailed notebook-by-notebook plan, including:
   - Which TIAToolbox tool to pair with which IDC collection (matching model training domains)
   - Data size budgets per notebook
   - Colab compatibility constraints
   - Code patterns validated against existing IDC-Tutorials conventions

3. **Implementation phase**: Notebooks were written sequentially (01-07), each building on patterns established in earlier ones. The existing [IDC-Tutorials](https://github.com/ImagingDataCommons/IDC-Tutorials) pathomics notebooks were used as reference for IDC API conventions (download patterns, `dirTemplate`, DICOM ANN parsing with highdicom).

### Prompting

The initial prompt was:

> "we are starting a new project that will explore the various analysis tools available in TIAToolbox, evaluate their applicability for processing slide microscopy data available in Imaging Data Commons, and will create working examples helping users get started with applying that open source tool for IDC data analysis. Use /imaging-data-commons skill for everything related to IDC."

Follow-up decisions made interactively:
- GitHub hosting: `github.com/fedorov/idc-tiatoolbox`
- Scope: All 7 notebooks (not incremental)
- Environment: Colab-first design
- License: Apache 2.0

## Understanding of TIAToolbox in the IDC Context

### Key Integration Point: DICOMWSIReader

The critical connector between TIAToolbox and IDC is `DICOMWSIReader`:

- TIAToolbox's `WSIReader.open()` auto-detects DICOM WSI directories (checks for `.dcm` files) and returns a `DICOMWSIReader`
- Under the hood, `DICOMWSIReader` uses the [`wsidicom`](https://github.com/imi-bigpicture/wsidicom) library
- IDC's DICOM WSI files (downloaded as `<SeriesInstanceUID>/<crdc_instance_uuid>.dcm`) are directly compatible
- The download pattern `dirTemplate='%SeriesInstanceUID'` creates the per-series folders that `WSIReader.open()` expects

### TIAToolbox Analysis Tools Applicable to IDC Data

| Tool | Class | Pretrained Models | Best IDC Collections | Notes |
|------|-------|-------------------|---------------------|-------|
| WSI Reading | `WSIReader` / `DICOMWSIReader` | N/A | All SM collections | Foundation for everything else |
| Tissue Masking | `OtsuTissueMasker` | N/A | All | Essential preprocessing; Otsu works well on H&E |
| Patch Extraction | `SlidingWindowPatchExtractor` | N/A | All | Pairs with masking; configurable resolution/stride |
| Stain Normalization | `MacenkoNormalizer`, `ReinhardNormalizer`, `VahadaneNormalizer` | N/A | Multi-collection studies | Important when combining data from different scanners/sites |
| Patch Classification | `PatchPredictor` | `resnet18-kather100k` (9-class CRC), various PCam models | `tcga_coad`, `tcga_read` (for Kather100K); any for PCam | Model-data domain match matters |
| Semantic Segmentation | `SemanticSegmentor` | `fcn_resnet50_unet-bcss` (5-class breast) | `tcga_brca`, `cptac_brca` | BCSS model trained on breast cancer; using on other tissue types will produce poor results |
| Nucleus Segmentation | `NucleusInstanceSegmentor` | `hovernet_fast-pannuke` (6 nuclei types), `hovernet_original-kumar` | All H&E collections | PanNuke is multi-organ; works broadly |
| Feature Extraction | `DeepFeatureExtractor` | ImageNet ResNets | All | For downstream graph/clustering analysis |
| Foundation Models | via `DeepFeatureExtractor` + `timm` | UNI, Prov-GigaPath, H-optimus-0 | All | Requires model access (gated HuggingFace models) |
| Graph Analysis | `SlideGraphConstructor` | SlideGraph+ | All | Requires feature extraction first |

### IDC Slide Microscopy Data Profile

Based on queries via `sm_index`:
- Multiple TCGA collections have hundreds of H&E slides (BRCA, LUAD, LUSC, COAD, etc.)
- CPTAC collections also have pathology slides with different scanners than TCGA
- `ObjectiveLensPower` varies (20x and 40x are common); 20x slides are ~2-4x smaller in file size
- Pan-Cancer-Nuclei-Seg-DICOM provides nucleus centroid annotations across many TCGA collections (DICOM ANN format)
- Annotation parsing requires `highdicom`; coordinates may be in mm (SCOORD3D) requiring pixel spacing conversion

### Collection-to-Model Domain Matching

This is a key design consideration: pretrained models perform best on tissue types matching their training data.

| Model | Training Data | Best IDC Collections |
|-------|--------------|---------------------|
| `resnet18-kather100k` | NCT-CRC-HE-100K (colorectal) | `tcga_coad`, `tcga_read` |
| `fcn_resnet50_unet-bcss` | BCSS (breast cancer) | `tcga_brca`, `cptac_brca` |
| `hovernet_fast-pannuke` | PanNuke (19 organs) | Broad applicability |
| PCam models | Patch Camelyon (lymph node) | `camelyon16`, `camelyon17` (if available) |

## Known Limitations

### Notebooks Have Not Been Executed

**This is the most important limitation.** All 7 notebooks were generated by Claude Code without being run end-to-end. They need to be tested on Google Colab to verify:

1. **TIAToolbox DICOMWSIReader compatibility**: The `WSIReader.open()` auto-detection of DICOM directories needs to be confirmed with actual IDC downloads. Potential issues:
   - `wsidicom` dependency may not be installed by default with `pip install tiatoolbox`
   - Some DICOM WSI tile encodings (JPEG2000 with specific transfer syntaxes) may not be supported
   - The directory structure from `idc-index` downloads may not match what `DICOMWSIReader` expects

2. **API surface accuracy**: TIAToolbox API was researched via web search, not by inspecting installed source code. Specific concerns:
   - `PatchPredictor.predict()` parameter names and return format may differ between versions
   - `SemanticSegmentor` output file naming (`.raw.0.npy`) may vary
   - `NucleusInstanceSegmentor` output format (`.dat` via joblib) may have changed
   - The `predictor.labels` attribute for class names may not exist on all model wrappers

3. **Coordinate systems**: The tile extraction and annotation coordinate conversion code involves multiple coordinate transforms (baseline ↔ thumbnail, baseline ↔ mpp-scaled, mm ↔ pixel). Off-by-one errors or incorrect scaling are likely until verified.

4. **Data availability**: The specific IDC collections and slides selected by the SQL queries depend on the current IDC data version (v23). Collections, slide counts, and metadata may change in future IDC releases.

### TIAToolbox Version Sensitivity

- The notebooks require `tiatoolbox>=1.5.0` for `DICOMWSIReader` support
- TIAToolbox is under active development; API changes between versions are possible
- The `pretrained_model` string identifiers (e.g., `"hovernet_fast-pannuke"`, `"resnet18-kather100k"`) need to match exactly what the installed version supports
- Foundation model support (UNI, Prov-GigaPath) was not included in the notebooks because these models require gated HuggingFace access

### Scope Limitations

- **No custom model training**: All notebooks use pretrained models only. No fine-tuning or training workflows are demonstrated.
- **No full WSI processing**: Notebooks 04-07 process tiles/regions, not entire slides, to keep Colab runtime manageable. Users wanting full-slide analysis need to adapt the code.
- **No DICOM output**: TIAToolbox results are saved in native formats (numpy, joblib). Converting results back to DICOM (e.g., using `highdicom` to create DICOM SEG or ANN objects) is not demonstrated.
- **No multiplexed/immunofluorescence**: Only H&E-stained slides are covered. IDC also has multiplexed immunofluorescence data that TIAToolbox can potentially process.
- **No clinical data integration**: IDC's `clinical_index` is not used. Correlating analysis results with clinical outcomes would be a natural extension.
- **Single-slide workflows**: Each notebook processes one slide. Batch processing across many slides (cohort analysis) is not demonstrated.

### IDC-Specific Limitations

- **Download sizes**: Even "small" slides are ~200-600 MB. On slow connections, downloads may timeout.
- **Colab disk space**: The total across all notebooks is ~2-4 GB, well within Colab's ~100 GB, but users running multiple notebooks in one session should watch disk usage.
- **IDC data versioning**: Queries use the current IDC index. When `idc-index` is upgraded, query results may change (different slides, different sizes).

### Comparison Notebook (07) Limitations

- The Pan-Cancer-Nuclei-Seg-DICOM annotations contain centroids (POINT graphic type), while HoVer-Net produces full contours. The comparison is therefore centroid-to-centroid, not contour-to-contour.
- No formal detection matching (e.g., Hungarian matching with distance threshold) is implemented; only spatial density correlation is computed.
- The comparison is on a single tile from a single slide; it's illustrative, not a rigorous benchmark.

## Recommendations for Next Steps

1. **Run all notebooks on Colab** and fix any issues (this is the highest priority)
2. **Verify TIAToolbox DICOM compatibility** by testing `WSIReader.open()` on several IDC collections
3. **Add error handling** for common failure modes (download failures, missing wsidicom, GPU not available)
4. **Consider adding a notebook** for feature extraction with foundation models (requires addressing HuggingFace model access)
5. **Consider DICOM output** — using `highdicom` to convert TIAToolbox results back to DICOM SEG/ANN for re-upload or SLIM visualization
6. **Consider batch processing** — a notebook showing analysis across an entire collection (e.g., all TCGA-BRCA slides)
