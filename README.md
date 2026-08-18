# CardioScope -- ECG Clinical Decision Support Dashboard

> **Access note.** This is a private academic project developed for the MA7443 / MSc Data
> Science Research Project dissertation ("Analyse Arrhythmia in Heart Beat"), **University of
> Leicester -- Group 2**. This repository is restricted to the project's supervisors/markers and
> the group members listed below. Not for public distribution -- see "Model integration" for
> known limitations before relying on any output from this tool.
>
> **Group 2 -- Contributors:** Pallavi Lingaraju (pl251) · Ansh Gupta (ag728) ·
> Shahmeer Shahzad (ss1792) · Devanshi Vashistha (dv89)
> **Supervisor:** Marco Fasondini · **Marker:** Eleanor Lingham

A Streamlit dashboard for 12-lead ECG review, built for an MSc Data Science dissertation
project. **The real, finalised severity model is integrated and its artefact file is included**
(`models/artifacts/dv_severity_model_improved.joblib`) -- install `lightgbm`/`scikit-learn`
(see requirements.txt) and predictions are real, not placeholder. See "Model integration" below
for the full deployment summary and, importantly, the known gaps in feature extraction that
haven't been verified against the original training code.

**Recently simplified to 2 pages** (per supervisor feedback): everything upload- and
result-related now lives on one **Home** page -- no more routing between separate Upload ECG /
Signal Viewer / Feature Analysis / AI Prediction / Clinical Report / Analytics pages. The second
page, **Project Journey**, is the team's results write-up. If you're looking for those old pages'
code, it's in git history -- they were removed as dead code, not just hidden.

## Quick start

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`). On the **Upload ECG** page,
click **Load Sample ECG** to explore every page immediately without needing a real file.

### Just want to see what it looks like first?

Open `dashboard_preview.html` directly in any browser -- no install required. It's a static
HTML/CSS/SVG mockup (not the real app) using the same colours, typography, and layout, with
working sidebar/tab navigation via plain JavaScript, so you can sanity-check the visual design
before setting up the Python environment. Every chart in it is hand-drawn SVG standing in for
what Plotly renders in the real app -- labelled as a preview at the top of the page.

> **A note on how this was built:** this project was generated and validated in an offline
> sandbox with no access to install `streamlit`, `plotly`, or `wfdb`, so it could not be
> runtime-tested with a live Streamlit server end-to-end. Every file was checked for syntax
> correctness (`python -m py_compile`), and the PDF report generator in
> `utils/report_generator.py` *was* tested for real (a package that happened to be available) and
> confirmed to produce a valid PDF. Please do a "Restart & Run All"-equivalent -- i.e. actually
> run `streamlit run app.py` and click through each page -- as your first real check before
> relying on this for anything, and treat any layout/runtime glitch you hit as expected first-run
> friction rather than something you did wrong.

## Project structure

```
ECG_Dashboard/
├── app.py                     # entry point -- redirects to pages/Home.py
├── config.py                  # paths, constants, clinical taxonomy, shared theme/CSS
├── requirements.txt
├── README.md
├── test_ecg_upload.py         # standalone self-test against real local WFDB data
│
├── assets/
│   ├── logo.png                # generated programmatically (PIL), on-brand placeholder
│   ├── banner.png               # generated programmatically (PIL), on-brand placeholder
│   ├── journey/                  # real figures from each teammate's own notebooks
│   └── icons/                   # empty -- the app uses emoji icons by default
│
├── pages/                     # SIMPLIFIED to exactly 2 pages
│   ├── Home.py                   # the entire functional app: upload, patient info, and
│   │                              # inline results (trace, KPI row, severity badge) -- one
│   │                              # page, no routing. Replaces the old 6-page flow.
│   └── Project_Journey.py        # team results/approach, presentation-ready, real images
│
├── components/                # reusable UI building blocks
│   ├── sidebar.py                # branding, active-record summary, model-status badge
│   ├── cards.py                  # metric cards, status badges, tier badge, info cards
│   └── charts.py                  # generic chart-card wrapper (trimmed -- gauge panels removed)
│
├── utils/                     # framework-agnostic logic
│   ├── ecg_loader.py             # WFDB (.dat or .mat) / CSV / synthetic-sample loading + validation
│   ├── signal_processing.py      # real: bandpass filter, R-peak HR/HRV estimate, quality score
│   ├── model_features.py          # translates this app's feature names to the model's exact
│   │                                expected names -- fixes a real silent-zero bug, see README
│   ├── plotting.py               # trimmed to the 2 figure builders actually in use
│   └── report_generator.py       # PDF (reportlab) with HTML fallback -- currently unused by
│                                   # Home (no Clinical Report page anymore), kept for reuse
│
├── models/                    # see "Model integration" above
│   ├── model_placeholder.py      # fallback when no real model artefact is present
│   ├── trained_model.py           # loads the real severity classifier (artefact-driven,
│   │                                reads feature list/medians/bias from the .joblib itself)
│   ├── predictor.py               # load_model() / predict_model() / return_prediction()
│   └── artifacts/
│       ├── README.md              # which file is here and why
│       └── dv_severity_model_improved.joblib   # INCLUDED -- the real, final model
│
├── GITIGNORE_PATCH.txt        # 3-line fix for a repo bug (see below)
│
└── reports/                   # generated PDF/HTML reports are written here at runtime
```

## Model integration -- status: REAL MODEL ACTIVE

The final trained model is integrated and, assuming `lightgbm`/`scikit-learn` are installed
(see requirements.txt), **produces real predictions** -- not placeholder output.

### Deployment summary

```
MODEL:          LGBM DART reduced (14 feats)
INPUT:          Single 10-second Lead II ECG
FEATURE COUNT:  14
FEATURES:       mean_hr, pnn20, min_hr, pnn50, qt_interval_mean, p_wave_duration_mean,
                pct_valid_beats, t_wave_amplitude_mean, age, qrs_duration_mean,
                signal_quality_mean, st_deviation_mean, r_amplitude_mean, sex_encoded
SCALING:        Supplied StandardScaler from the .joblib artefact
SERIOUS BIAS:   3.95 (multiplies the Serious-class probability before the final
                argmax -- a deliberate clinical-safety decision rule, not a
                recalibration; see models/trained_model.py's _biased_predict())
OUTPUT:         Normal / Doctor review / Serious
ARTEFACT:       models/artifacts/dv_severity_model_improved.joblib
TEST PERFORMANCE (from the model card, per the supplied notebook):
                Serious recall 0.8844 [95% CI 0.872, 0.897]
                Serious precision 0.7072 · macro F1 0.8485 · accuracy 0.8683
                trained on 26,869 records, one hospital cohort (Chapman-Shaoxing-Ningbo)
```

### The inference pipeline, exactly as implemented

```
uploaded ECG (WFDB .hea+.dat/.mat, or CSV)
    -> validate (leads present, no NaN, sane sampling rate)
    -> require Lead II specifically (the model's only trained input; prediction is
       disabled with a clear message if Lead II isn't in the record)
    -> utils/signal_processing.extract_basic_features()   [this app's own naming]
    -> utils/model_features.build_model_features()        [renames to the model's
                                                             exact expected feature names --
                                                             see "A bug this fixes" below]
    -> models/trained_model.py: DataFrame in exact feature order
    -> missing features filled from the artefact's own train_medians
    -> the artefact's own StandardScaler
    -> the artefact's own LightGBM model . predict_proba()
    -> Serious-class probability x 3.95, then argmax (biased_predict, reproduced exactly
       from the supplied notebook's own function)
    -> Normal / Doctor review / Serious, displayed with confidence + full transparency
       on which of the 14 features were measured / imputed / approximated
```

### A real bug this integration caught and fixed

This app's `extract_basic_features()` returns keys like `heart_rate_bpm` for readability on
the Home page. The model's artefact expects `mean_hr`. An earlier integration passed the raw
dict straight to the model without renaming -- meaning heart rate, `min_hr`, `pnn50`, and
`pnn20` (all genuinely computed) were silently falling through to a "no median available,
fallback to 0" branch, feeding the model **zero** for four real, measurable features. Fixed
in `utils/model_features.py`, which is now the single, explicit place that translation
happens -- see its module docstring for the full explanation and the exact mapping.

### Known gaps -- read this before trusting a prediction

The supplied notebook (`supervised_modelling_analysis_final_2.ipynb`) does **not** contain
the raw-ECG-to-14-feature extraction code -- it starts from an already-extracted CSV
(`outputs/lead_ii_features_dv.csv`). Per the brief's own instruction not to guess, here is
the honest breakdown of how each of the 14 features is actually obtained by this dashboard:

| Category | Features | Source |
|---|---|---|
| **Measured** (real, matches training definition) | `mean_hr`, `min_hr`, `pnn50`, `pnn20`, `age`, `sex_encoded` | Computed directly from R-peak intervals, or from the patient info form |
| **Imputed** (the artefact's own designed fallback) | `qt_interval_mean`, `p_wave_duration_mean`, `t_wave_amplitude_mean`, `qrs_duration_mean`, `st_deviation_mean`, `r_amplitude_mean` | This dashboard doesn't implement P/QRS/T-wave delineation, so the artefact's own `train_medians` are used -- exactly the mechanism the artefact ships those medians for |
| **Approximated** (⚠ formula not confirmed) | `pct_valid_beats`, `signal_quality_mean` | No median fallback exists for these in the artefact (meaning training always had real values), and no extraction code for them was supplied. Implemented with defensible standard definitions (see docstrings in `utils/signal_processing.py`), confirmed to be on the right *scale* by cross-checking the shipped scaler's own fitted mean/std, but **not confirmed to match Devanshi's exact original formula** |

**To close this gap fully:** the exact `pct_valid_beats` / `signal_quality_mean` extraction
code, or the feature-extraction notebook that produced `lead_ii_features_dv.csv` in the
first place. Every prediction currently shown flags in its "Which features were measured?"
panel exactly which of the 14 inputs are approximated, so this isn't hidden -- but a
prediction resting on 2 unconfirmed features out of 14 should be treated with more caution
than the model's own reported test performance implies.

### Testing this yourself: dashboard vs. direct model comparison

The brief's own most important test -- run one ECG through the notebook/model directly, run
the same ECG through the dashboard, confirm they match -- **could not be completed in the
sandbox this was built in**, because `lightgbm` isn't installable there (no package-index
access). Everything up to the actual tree prediction was verified for real against your
`JS00001.hea`/`.mat` file (feature extraction, name translation, DataFrame construction,
scaling, bias logic all confirmed correct via a stub model class) -- only the literal LightGBM
inference itself is unverified. **This is the first thing to check once you have `lightgbm`
installed locally**: run the same record through both the notebook and the dashboard, and
confirm the predicted tier matches.

## What's real vs. placeholder right now

| Area | Status |
|---|---|
| WFDB (.hea+.dat or .hea+.mat) / CSV / sample loading, validation | Real |
| Bandpass filtering, R-peak detection, HR/RR/HRV features | Real (lightweight heuristics, not clinical-grade) |
| Signal quality scoring | Real (heuristic, not a trained/validated classifier) |
| Severity **classification** | **Real** -- LGBM DART reduced (14 feats), assuming `lightgbm`/`scikit-learn` are installed |
| 6 of 14 model features (rate/HRV + demographics) | **Real**, matches training definitions |
| 6 of 14 model features (morphology) | Imputed from the artefact's own training medians |
| 2 of 14 model features (`pct_valid_beats`, `signal_quality_mean`) | **Approximated** -- see "Known gaps" above |
| Cluster assignment / typicality | Not applicable -- this model is a classifier only |
| Team results / approach (Project Journey page) | **Real** -- pulled directly from each teammate's own notebooks |

## Known limitations to be aware of

- Not runtime-tested against a live Streamlit server, or against real `lightgbm`, in the
  environment this was built in (see "Testing this yourself" above -- this is the most
  important thing to verify first).
- `pct_valid_beats` and `signal_quality_mean` are approximated, not confirmed to match the
  original training-time formula (see "Known gaps" above).
- The R-peak detector in `utils/signal_processing.py` is a simple amplitude-threshold detector
  for demo purposes, not a validated QRS detector (e.g. Pan-Tompkins, NeuroKit2).
- The model's own documented limitations (from its model card, surfaced nowhere in the UI
  currently except this README -- consider adding a model-card expander if useful): Serious
  recall varies materially across age bands (patients under 40 least well served); single
  10-second Lead II window only, no frequency-domain HRV or episode-level features; severity
  tier collapses multi-diagnosis records to their single most critical code;
  `qrs_duration_mean` is affected by DWT delineation and should not be read as a clinically
  exact QRS duration; trained on one hospital cohort, external validity unproven; research/
  decision-support use only, not a medical device or diagnosis.
- `st.switch_page` / `st.page_link` require Streamlit ≥1.27 / ≥1.31 respectively; both call sites
  fall back gracefully on older versions, but upgrading is recommended.

