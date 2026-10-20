## tau_2024_patched.json.gz

Patched copy of the official TauPOG Run-3 2024 `correctionlib` file:
```
/cvmfs/cms-griddata.cern.ch/cat/metadata/TAU/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/2026-01-14/tau.json.gz
```
(see https://cms-analysis-corrections.docs.cern.ch/corrections/TAU/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/)

### Bug and patch

The official file fails to load with `correctionlib` (2.5.0 and 2.7.0
both tested), raising `RuntimeError: Invalid edges array type`. Cause:
the upper pt-binning edge for the `tau_trigger` correction's many
category combinations is serialized as the **string** `"+inf"` instead
of a proper JSON number (270 occurrences, all the same bug). This is a
file bug on TauPOG's side, not a correctionlib version issue - a
patched local copy loads and evaluates correctly.

Patch applied: every `"+inf"` string replaced with the number `1e20`
(a safe, effectively-unbounded upper bound for tau pt, matching the
column's intended "catch-all top bin" behavior).

Verified to load and evaluate (e.g.
`tau_trigger.evaluate(40.0, 0, 'ditau', 'Medium', 'sf', 'nom') = 0.916`).

### Status

Reported upstream to TauPOG (not yet confirmed fixed as of this
commit) - this local patch should be dropped once the official CVMFS
file is corrected; `ModuleTauTau.py` points here as a temporary
workaround only.
