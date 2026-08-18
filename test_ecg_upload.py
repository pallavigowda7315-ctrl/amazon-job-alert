"""
test_ecg_upload.py
====================
Run this yourself, locally, with real data -- I (Claude) built and hardened
the loading code in utils/ecg_loader.py, but could not install the `wfdb`
package or fetch real PhysioNet files in the sandbox I built this in, so
the WFDB upload path has never actually been run against a real file.
This script is the fastest way to close that gap.

USAGE
-----
1. Point WFDB_HEA / WFDB_DAT below at a real matching .hea/.dat pair from
   your dataset (e.g. from extracted_data/.../WFDBRecords/.../JS00001.hea).
2. From the ECG_Dashboard folder, with your venv activated:
       python test_ecg_upload.py
3. Read the PASS/FAIL summary at the end.

If something fails, the traceback plus the specific record that failed is
exactly what to paste back for a fix -- much faster than debugging through
the Streamlit UI.
"""
import sys
import traceback
from pathlib import Path

# --------------------------------------------------------------------------
# EDIT THESE TWO PATHS to point at one real .hea/.dat pair from your dataset
# --------------------------------------------------------------------------
WFDB_HEA = Path("extracted_data/a-large-scale-12-lead-electrocardiogram-database-for-arrhythmia-study-1.0.0/WFDBRecords/01/010/JS00001.hea")
WFDB_DAT = Path("extracted_data/a-large-scale-12-lead-electrocardiogram-database-for-arrhythmia-study-1.0.0/WFDBRecords/01/010/JS00001.dat")

sys.path.insert(0, str(Path(__file__).parent))

results = []


def check(name, fn):
    print(f"\n{'='*70}\n{name}\n{'='*70}")
    try:
        fn()
        print(f"[PASS] {name}")
        results.append((name, True, None))
    except Exception as exc:  # noqa: BLE001 -- this script's whole job is to surface failures
        print(f"[FAIL] {name}")
        traceback.print_exc()
        results.append((name, False, str(exc)))


def test_wfdb_dependency():
    import wfdb  # noqa: F401
    print("wfdb package is installed.")


def test_wfdb_files_exist():
    assert WFDB_HEA.exists(), f"Header file not found: {WFDB_HEA}\n  -> Edit WFDB_HEA at the top of this script."
    assert WFDB_DAT.exists(), f"Signal file not found: {WFDB_DAT}\n  -> Edit WFDB_DAT at the top of this script."
    print(f"Found: {WFDB_HEA.name} ({WFDB_HEA.stat().st_size:,} bytes)")
    print(f"Found: {WFDB_DAT.name} ({WFDB_DAT.stat().st_size:,} bytes)")


def test_wfdb_load():
    from utils.ecg_loader import load_wfdb_record, validate_record

    hea_bytes = WFDB_HEA.read_bytes()
    dat_bytes = WFDB_DAT.read_bytes()
    record = load_wfdb_record(hea_bytes, dat_bytes, record_name=WFDB_HEA.stem)

    print(f"Record name : {record['record_name']}")
    print(f"Leads       : {list(record['signals'].keys())}")
    print(f"Sampling    : {record['fs']} Hz")
    print(f"Duration    : {record['duration_s']:.1f} s")
    print(f"Patient     : {record['patient']}")
    if record["warnings"]:
        print("Warnings:")
        for w in record["warnings"]:
            print(f"  - {w}")

    issues = validate_record(record)
    if issues:
        print("Validation issues found:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("No structural validation issues.")

    assert len(record["signals"]) > 0, "No leads were parsed."
    assert record["fs"] > 0, "Invalid sampling rate."


def test_signal_processing_on_real_data():
    from utils.ecg_loader import load_wfdb_record
    from utils.signal_processing import extract_basic_features, compute_signal_quality

    hea_bytes = WFDB_HEA.read_bytes()
    dat_bytes = WFDB_DAT.read_bytes()
    record = load_wfdb_record(hea_bytes, dat_bytes, record_name=WFDB_HEA.stem)

    lead = "II" if "II" in record["signals"] else next(iter(record["signals"]))
    features = extract_basic_features(record, lead=lead)
    print(f"Features on lead {lead}:")
    for k, v in features.items():
        print(f"  {k}: {v}")

    quality = compute_signal_quality(record["signals"][lead], record["fs"])
    print(f"\nSignal quality: {quality}")

    assert features["extracted"], (
        "R-peak detection found fewer than 2 beats on this real record -- either this "
        "specific record is genuinely low quality, or the detector needs tuning against "
        "real data (it was only validated against a synthetic signal until now)."
    )


def test_prediction_pipeline_end_to_end():
    from utils.ecg_loader import load_wfdb_record
    from utils.signal_processing import extract_basic_features
    from models.predictor import run_full_prediction

    hea_bytes = WFDB_HEA.read_bytes()
    dat_bytes = WFDB_DAT.read_bytes()
    record = load_wfdb_record(hea_bytes, dat_bytes, record_name=WFDB_HEA.stem)
    lead = "II" if "II" in record["signals"] else next(iter(record["signals"]))
    features = extract_basic_features(record, lead=lead)
    features["age"] = 55  # stand-in patient info for this smoke test
    features["sex_encoded"] = 1

    prediction = run_full_prediction(features)
    print(f"Predicted class : {prediction['predicted_class']}")
    print(f"Confidence      : {prediction['confidence']}")
    print(f"Is placeholder  : {prediction['is_placeholder']}")
    if not prediction["is_placeholder"]:
        print(f"Feature sources : {prediction['feature_sources']}")

    assert prediction["predicted_class"] in [
        "Normal / usually benign", "Doctor review / possible procedure", "Serious / urgent review"
    ]


if __name__ == "__main__":
    check("1. wfdb package installed", test_wfdb_dependency)
    check("2. Real .hea/.dat files found", test_wfdb_files_exist)
    check("3. Loading the real WFDB record", test_wfdb_load)
    check("4. Signal processing on the real record", test_signal_processing_on_real_data)
    check("5. Full prediction pipeline, end to end", test_prediction_pipeline_end_to_end)

    print(f"\n\n{'='*70}\nSUMMARY\n{'='*70}")
    for name, passed, err in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}" + (f"  -- {err}" if err else ""))
    n_pass = sum(1 for _, p, _ in results if p)
    print(f"\n{n_pass}/{len(results)} checks passed.")
    if n_pass < len(results):
        print("\nPaste the FAIL output above back for a fix.")
