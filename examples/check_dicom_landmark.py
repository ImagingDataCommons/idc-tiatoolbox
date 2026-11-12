"""Check the notebook reader on the public C3L-03262 DICOM pyramid (CPU only).

Pass the directory of DICOM instances, or --download-dir to fetch the series.
The reference is assembled directly from the encoded reduced-level JPEG frames.
"""
import argparse
import io
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image
from pydicom.encaps import generate_frames
from tiatoolbox.wsicore.wsireader import DICOMWSIReader

SERIES = "1.3.6.1.4.1.5962.99.1.260401516.1165064422.1640937941356.2.0"
BOUNDS = (3843, 3951, 5891, 5999)  # x0, y0, x1, y1 in the baseline matrix
SIZE = 512


def reference_crop(directory):
    levels = {}
    for path in directory.glob("*.dcm"):
        header = pydicom.dcmread(path, stop_before_pixels=True)
        if header.SeriesInstanceUID != SERIES or header.PatientID != "C3L-03262":
            raise ValueError(f"Unexpected series or patient in {path.name}")
        if header.ImageType[2] == "VOLUME":
            levels[header.TotalPixelMatrixColumns] = (path, header)
    _, native = levels[9959]
    path, reduced = levels[2489]
    if (native.TotalPixelMatrixRows, reduced.TotalPixelMatrixRows) != (9023, 2255):
        raise ValueError("Unexpected pyramid geometry")
    if (native.TotalPixelMatrixOriginSequence != reduced.TotalPixelMatrixOriginSequence
            or native.ImageOrientationSlide != reduced.ImageOrientationSlide):
        raise ValueError("Pyramid levels disagree on origin or orientation")

    def spacing(header):
        measures = header.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0]
        return np.asarray(measures.PixelSpacing, dtype=float)[::-1]  # x, y in mm

    box = np.rint(BOUNDS * np.tile(spacing(native) / spacing(reduced), 2)).astype(int)
    x, y, right, bottom = box
    if tuple(box) != (960, 987, 1472, 1499):
        raise ValueError(f"Unexpected physical footprint {box}")
    ds = pydicom.dcmread(path)
    if ds.DimensionOrganizationType != "TILED_FULL" or ds.NumberOfOpticalPaths != 1:
        raise ValueError("Reference requires this single-plane, row-major tiled level")
    width, height = ds.Columns, ds.Rows
    across = (ds.TotalPixelMatrixColumns + width - 1) // width
    down = (ds.TotalPixelMatrixRows + height - 1) // height
    if ds.NumberOfFrames != across * down:
        raise ValueError("Unexpected frame count for a single focal plane")
    reference = np.empty((SIZE, SIZE, 3), dtype=np.uint8)
    covered = np.zeros((SIZE, SIZE), dtype=bool)
    for i, frame in enumerate(generate_frames(ds.PixelData, number_of_frames=ds.NumberOfFrames)):
        left, top = (i % across) * width, (i // across) * height
        x0, y0 = max(left, x), max(top, y)
        x1, y1 = min(left + width, right), min(top + height, bottom)
        if x0 < x1 and y0 < y1:
            with Image.open(io.BytesIO(frame)) as im:
                patch = im.convert("RGB").crop((x0-left, y0-top, x1-left, y1-top))
            reference[y0-y:y1-y, x0-x:x1-x] = np.asarray(patch)
            covered[y0-y:y1-y, x0-x:x1-x] = True
    if not covered.all():
        raise ValueError("Incomplete JPEG reference")
    return reference


def check(directory):
    reference = reference_crop(directory)
    reader = DICOMWSIReader(directory)
    if reader.info.objective_power is None:
        reader.info.objective_power = 20  # native objective of this series
    actual = reader.read_bounds(BOUNDS, resolution=5, units="power")
    if actual.shape != reference.shape:
        raise AssertionError(f"Expected {reference.shape}, got {actual.shape}")
    error = np.abs(actual.astype(np.int16) - reference.astype(np.int16))
    # Allow small RGB rounding differences between JPEG decoders.
    mean, p99 = error.mean(), np.percentile(error, 99)
    if mean > 2 or p99 > 5:
        raise AssertionError(f"Landmark mismatch: mean RGB error {mean:.3f}, p99 {p99:.1f}")
    print(f"PASS: C3L-03262, 512 × 512 at 5×; mean RGB error {mean:.3f}, p99 {p99:.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--series-dir", type=Path)
    group.add_argument("--download-dir", type=Path)
    args = parser.parse_args()
    if args.download_dir is not None:
        from idc_index import IDCClient

        args.download_dir.mkdir(parents=True, exist_ok=True)
        IDCClient().download_from_selection(downloadDir=str(args.download_dir),
            seriesInstanceUID=[SERIES], dirTemplate="%SeriesInstanceUID")
        directory = args.download_dir / SERIES
    else:
        directory = args.series_dir
    check(directory)
