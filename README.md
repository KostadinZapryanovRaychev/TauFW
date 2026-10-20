### TauFW

cd $CMSSW_BASE/src/
cmsenv
scram b -j8
voms-proxy-init --voms cms --valid 192:00:00 --rfc

### PicoProducer

(https://github.com/cms-nanoAOD/nanoAOD-tools):

### Combine

If you want to use the `combine` tools in `Fitter`, install combine following the
[latest instructions](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#setting-up-the-environment-and-installation),
for example

```
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.1.0 # for CMSSW_10_X
git checkout v9.1.0 # for CMSSW_11_X
```

and then [`CombineHarvester`](https://github.com/cms-analysis/CombineHarvester),

```
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scramv1 b clean; scramv1 b
git checkout v2.0.0 # for CMSSW_11_X only
```

## Analysis plan: Z' &rarr; tau tau (Run 3, hadronic channel)

Simple steps:

2. **Register the samples.** DONE.
   - Signal: Z'(250) NanoAODSim registered in `PicoProducer/samples/samples_2024.py`
     as `Zprime/ZprimeToTauTau_M250`, pointing to
     `/eos/cms/store/user/mileva/bsm3g/RunIII2024Summer24/M250/NANOAODSIM/`
     (cross section 232.0 pb). Verified with `pico.py get files -y 2024 -s Zprime*`.
   - Backgrounds (DY, ttbar, W+jets, single-top, diboson) were already
     present in `samples_2024.py`, resolving via official DAS. Verified
     with `pico.py get files -y 2024 -s DY*` (and similar).
   - Still missing: Run 3 data samples (same file, same way, once needed).

3. **Define the tau_h tau_h selection in PicoProducer**, using the TauPOG
   Run-3 recommendation as the starting point: tau pt > 20 GeV, |eta| < 2.5,
   |dz| < 0.2, a DeepTau/PNet/UParT VSjet working point, opposite-sign pair,
   well-separated in DeltaR (as checked already in the Coffea prototype).
   Pick the trigger(s) appropriate for a 250 GeV resonance.

4. **Apply the official corrections** once available: tau ID SFs, tau energy
   scale, lepton-to-tau fake rate, and trigger SFs from the TauPOG
   `correctionlib` JSONs, wired into the PicoProducer processing step.

5. **Produce pico ntuples** for signal, backgrounds, and data with
   PicoProducer, run locally on a small signal file first to validate the
   output before submitting full batch jobs.

6. **Analyze and plot with Plotter**: build the visible/di-tau mass
   distribution, validate background modeling in control regions (DY,
   ttbar), and define the Z'(250) signal region.

7. **Cross-check against the Coffea prototype** at key steps (branch
   content, selection yields, mass shape) to catch bugs early before
   investing in the full TauFW chain.

8. **Fit with Fitter/combine** once the signal region and background
   estimates are stable, following the EXO-21-016 approach for the
   statistical treatment.

Open items before steps 3-4 can be finalized: TauPOG's exact Run 3
`correctionlib` recommendations (ID/ES/trigger SFs) and the trigger choice
for a light-mass resonance.

### Verify a sample is registered correctly

```bash
pico.py get samples -y 2024 -s Zprime*
pico.py get files   -y 2024 -s Zprime*
```

The first confirms the sample entry is parsed; the second lists the actual
`.root` files found at its `store=` path, confirming it can be read.

pico.py channel tautau ModuleTauTau
pico.py run -c tautau -y 2024 -s Zprime\*

### 2024 pileup profiles - DONE

TauFW needs to know how busy real 2024 collisions were ("pileup") so it
can make simulated MC events match it. Two reference files were missing
and are now both in `PicoProducer/data/pileup/`:

- `Data_PileUp_2024_69p2.root` - copied directly from the official Lumi
  POG file (`dataPileupHistogram-2024BCDEFGHI_Golden-69200ub.root`).
- `MC_PileUp_2024.root` - built by running a small "pileup" job over all
  registered 2024 background MC samples (DY, TT, WJ, ST, VV; signal
  excluded on purpose) and summing their `Pileup_nTrueInt` histograms.

With both in place, `pico.py run -c tautau -y 2024 -s Zprime*` no longer
crashes on a missing-file error.

### BLOCKED: 2024 ditau trigger definitions missing

Next crash in the same command: `data/trigger/tau_triggers_2024.json`
does not exist. Only 2016/2017/2018 (Run 2) trigger JSONs exist in this
TauFW checkout - nothing for Run 3 yet.

This file is not a simple reference copy like the pileup files - it
lists the actual HLT ditau trigger path names for that year plus the
NanoAOD `TrigObj` filter-bit mapping needed to match offline taus to
the trigger object that fired. Getting this wrong silently breaks (or
wrongly passes) the trigger requirement, so it needs the real official
Run-3 2024 ditau trigger recommendation, not a guess.

**DRAFT created** (`data/trigger/tau_triggers_2024.json`), built from the
real 2024 NanoAODv15 MC branch list, not guessed from scratch:

- Trigger path: `HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1` - found by
  listing `HLT_*` branches in the actual signal file's NanoAOD content;
  it's the direct Run-3 successor of the Run-2 path already used in
  `tau_triggers_2018.json` (same 35 GeV threshold, "Medium" WP, same
  eta2p1 acceptance, old ChargedIso tau ID swapped for the newer DeepTau).
- Filter bit: `TrigObj_filterBits` bit 11 = "di-tau" for the Tau object,
  read directly from the NanoAODv15 autoDoc page.

Still unverified (flagged in the file's own `_DRAFT_NOTE`): the offline
`ptmin` cut (guessed as threshold+5 GeV, following the Run-2 pattern)
and the cosmetic HLT filter name string (not used by the matching logic
itself). Cross-check this draft against the official TauPOG Run-3
trigger recommendation before trusting any resulting numbers.

The draft trigger JSON loads fine - `pico.py run -c tautau -y 2024 -s
Zprime*` got past it with no crash.

### BLOCKED (real step-4 blocker): tau trigger/ID SF tools are Run-2 only

Next crash in the same command: `TauTriggerSFs.py` hard-codes
`years = [2016,2017,2018]` and explicitly refuses 2024. This is not a
missing file - it's a Run-2-only tool (reads old-style ROOT histograms
like `tauTriggerEfficiencies2018.root`). `ModuleTauTau.py` would hit the
same wall right after for `TauIDSFTool` (tau ID SFs), for the same
reason.

TauPOG's Run-3 corrections use a different format entirely:
`correctionlib` JSON files (per the supervisor's notes: "The
correctionlib JSON files are available at CAT webpage" - tau ID SFs,
tau momentum SFs, lepton->tau fake rate SFs, lepton+tau and di-tau
trigger SFs).

**UPDATE - correctionlib file found and reachable.** Found via
https://cms-analysis-corrections.docs.cern.ch/corrections/TAU/, era
`Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15` (matches the
signal campaign and registered data eras). File `tau.json.gz` lives on
CVMFS, confirmed reachable:

```
/cvmfs/cms-griddata.cern.ch/cat/metadata/TAU/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/2026-01-14/tau.json.gz
```

It's built for `DeepTau2018v2p5`, not `DeepTau2017v2p1`. Confirmed via
`root -l <signal file>` + `Events->Print("Tau_idDeepTau*")` /
`"Tau_rawDeepTau*"` that the signal NanoAODv15 file **only** has
`DeepTau2018v2p5` branches (no `2017v2p1` at all) - so switching the
selection to match was mandatory, not optional.

`ModuleTauTau.py` updated:

- Selection now reads `idDeepTau2018v2p5*`/`rawDeepTau2018v2p5*`
  branches for year >= 2022 (2017v2p1 for Run 2, unchanged).
- `correctionlib.CorrectionSet` loaded from the file above for 2024.
- Output tree branches still use their old `*2017v2p1*` names for now
  (not renamed - shared file, bigger change, deferred) but for
  year >= 2022 they hold `DeepTau2018v2p5` values.
- **Not yet wired up:** the actual `.evaluate()` calls for the 4
  scale-factor corrections (ID, VSe/VSmu fake rate, trigger) and the
  tau energy scale - their exact `genmatch`/working-point argument
  convention needs confirming against an official TauPOG usage example
  first (the CAT docs describe `genmatch` as grouped categories, not
  simply the raw NanoAOD value). Left as neutral weight=1 placeholders
  with clear TODO comments rather than guessed.

Next: confirm the correction input conventions, then fill in the
`.evaluate()` calls.

### Shared-code (ModuleTauPair.py) Run-3 fixes along the way

Running `pico.py run -c tautau -y 2024 -s Zprime*` surfaced more issues
in the shared base module (used by all channels, not just tautau):

- `getlepvetoes()` was missing the `era` argument in the two
  `ModuleTauTau.py` call sites - the function itself already had
  era-aware branch names (2022/2023+ variants), it just wasn't being
  passed through. Fixed.
- Several legacy Tau ID branches don't exist in Run-3 NanoAOD:
  `Tau_idAntiEle` (dropped, role covered by DeepTau VSe, no
  substitute), `Tau_idDecayMode` (renamed to `idDecayModeOldDMs`, same
  meaning), `Tau_idMVAoldDM2017v2`/`idMVAnewDM2017v2` (old MVA iso ID
  fully retired, no substitute). Confirmed via
  `Events->Print("Tau_id*")`. Defaulted the no-substitute ones to -1
  for year>=2022, remapped idDecayMode to its renamed equivalent.
- `Jet_jetId` is missing entirely from this private NanoAOD production
  (confirmed via `Events->Print("Jet_*")` - all the raw energy-fraction
  ingredients to compute it manually are present, just not the
  precomputed flag). Decision: bypassed the Tight jet ID cut for now
  (try/except around the one crash site in `fillJetBranches`), flagged
  with a TODO to compute it properly from the official JME formula
  before trusting jet/b-tag-based quantities.
- Side finding, not yet fixed: `jetveto()` (Run-3 jet veto maps) only
  activates for `'2022'`/`'2023'` eras, not `'2024'`, even though the
  jet veto map ROOT file for 2024
  (`data/jetveto/Winter24Prompt24_2024BCDEFGHI.root`) is already
  present in the repo. Not blocking the current test run (the function
  just returns 0 early for 2024), but should be wired in before trusting
  results that depend on jet veto maps.

### BUG in the official TauPOG file - found, patched locally, reported

Loading the official CVMFS file crashed `correctionlib` with
`RuntimeError: Invalid edges array type`. Downloaded a local copy and
inspected it directly: the `tau_trigger` correction's upper pt-binning
edge is serialized as the **string** `"+inf"` in 270 places, instead of
a proper JSON number - a bug in the file itself (reproduced identically
with both correctionlib 2.5.0 on lxplus and 2.7.0 locally), not a
version mismatch.

Fix: patched a local copy (`"+inf"` -> `1e20`, an effectively-unbounded
upper pt edge), verified it loads and evaluates correctly
(`tau_trigger.evaluate(40.0, 0, 'ditau', 'Medium', 'sf', 'nom') =
0.916`). Saved as `PicoProducer/data/tau/tau_2024_patched.json.gz`
(see `data/tau/README.md` for the full bug writeup), and
`ModuleTauTau.py` now points there instead of the CVMFS path, until
TauPOG fixes the official file (should be reported upstream via the
GitLab MR `!2` mentioned on the docs page).

## References & sources - how each step was built, and why

**Signal sample.** Path and cross section (232.0 pb for M=250) came
from the supervisor's own production notes (CodiMD page), where the
private Z'(250) Run-3 NanoAODSim was generated and placed on eos.
Motivation: this is the actual signal we're searching for, so it has to
come from the specific private production, not a central dataset.

**Background samples.** Already present in `samples/samples_2024.py`
from earlier TauFW work, resolving via official central DAS (Run3
Winter24NanoAOD campaign). Motivation: standard SM backgrounds (DY,
ttbar, W+jets, single-top, diboson) that mimic the ditau signature and
need to be subtracted/modeled, following the same approach as the
Run-2 Z'->2tau analysis (CADI EXO-21-016).

**2024 data pileup profile** (`Data_PileUp_2024_69p2.root`). Copied
directly from the official CMS Luminosity POG certification area:
`/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/PileUp/
dataPileupHistogram-2024BCDEFGHI_Golden-69200ub.root`. This is the
standard, POG-maintained source for "how busy was 2024 data" - using
the full-run ("BCDEFGHI") Golden JSON version with the standard 69.2 mb
minbias cross section, matching the eras covered by the registered
`Tau_Run2024*` data samples. Motivation: required to reweight MC to
match real collision conditions (see the longer pileup explanation
above).

**2024 MC pileup profile** (`MC_PileUp_2024.root`). Built in-house (no
official equivalent exists for a private sample mix): ran the
`pileup` channel over every registered 2024 background MC sample and
summed their simulated `Pileup_nTrueInt` distributions, following the
exact recipe documented inside TauFW itself
(`PicoProducer/python/analysis/PileUp.py` header comment and
`data/pileup/getPileupProfiles.py`). Signal was deliberately excluded,
since the MC profile should represent the background mix being
reweighted to match data, not the resonance being searched for.

**2024 ditau trigger JSON** (`data/trigger/tau_triggers_2024.json`,
still DRAFT). Built from:

- The official NanoAOD "autoDoc" branch documentation
  (`https://cms-xpog.docs.cern.ch/autoDoc/`), NanoAODv15, 2024 MC -
  this is where `TrigObj_filterBits` bit 11 ("di-tau" for the Tau
  object) came from, and where the full list of `HLT_*` branches was
  read to find `HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1`.
- Comparison against TauFW's own existing Run-2 file
  (`tau_triggers_2018.json`) to infer the expected JSON structure and
  the pattern for the still-unconfirmed `ptmin` (offline cut =
  online threshold + 5 GeV).

Motivation: without trigger information, `ModuleTauTau` cannot check
whether an event was actually recorded by a ditau trigger, or confirm
a reconstructed tau pair matches the object that caused the trigger to
fire - this is a required, not optional, part of the per-event
selection (see `ModuleTauTau.py`, the `self.trigger.fired(event)`
check right after the "no cut" stage).

**Still pending, needs the official TauPOG source** (per your
supervisor's CodiMD notes, under "Tau analysis - run 3 data and
documentation" / "Tau ID recommendations for Run-3: 2022-2024"):

- Confirmation (or correction) of the draft ditau trigger choice above.
- The `correctionlib` JSON files for tau ID SFs, tau momentum scale,
  lepton->tau fake rate, and trigger SFs (step 4 of the plan).
- The exact tau ID working point recommendation (DeepTau vs PNet vs
  UParT) to use for the selection (step 3).
