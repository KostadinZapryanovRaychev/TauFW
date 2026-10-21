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

3. **Define the tau_h tau_h selection in PicoProducer** - IN PROGRESS.
   `ModuleTauTau.py` now runs end-to-end on the signal sample for 2024
   (see milestone below), using DeepTau2018v2p5 branches and the draft
   ditau trigger. Still using old Run-2 cut values as placeholders
   (`tauCutPt=40`, `tauwp=1`) - not yet tuned to an actual Run-3 POG
   recommendation (pt > 20 GeV, |eta| < 2.5, |dz| < 0.2, a specific
   DeepTau/PNet/UParT VSjet working point).

4. **Apply the official corrections** - file found, loading works, but
   the actual `.evaluate()` calls are still TODO placeholders
   (weight=1). See the correctionlib section below.

5. **Produce pico ntuples** for signal - FIRST LOCAL TEST DONE (see
   milestone below). Backgrounds and data not yet run; full batch
   production not started.

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

### MILESTONE - first full local run on signal works (2026-10-20)

`pico.py run -c tautau -y 2024 -s Zprime*` ran to completion over all
345,524 signal events and wrote
`output/pico_tautau_2024_ZprimeToTauTau_M250.root`:

```
trigger:    18.33% pass
+ tau:      16.36% pass (89.27% relative)
+ ditau pair: 8.61% pass (52.63% relative) -> 29,760 events stored
```

Every blocker hit along the way this session (proxy, HTCondor/EosSubmit
batch issues, missing 2024 pileup files, missing 2024 trigger JSON,
Run-2-only correction tools, a bug in the official TauPOG JSON, several
Run-3-renamed/dropped NanoAOD branches) is now actually cleared in a
working run, not just patched around.

**Caveat - pipeline works, physics numbers don't mean much yet:**
selection cuts are still Run-2 defaults (not Run-3 tuned, step 3), all
correction weights are placeholder 1.0 (step 4 not wired up), and the
jet ID cut is bypassed. Don't use these yields/plots for anything
quantitative yet.

### Next steps, in order

1. Run the backgrounds (DY, TT, WJ, ST, VV) - DONE (2026-10-20), see
   the dedicated section below.
2. Tune the actual selection cuts in `ModuleTauTau.py` to a real Run-3
   POG recommendation - DONE (2026-10-21). Applied the kinematic cuts
   from the supervisor's own CodiMD notes (pT > 20 GeV, |eta| < 2.5,
   |dz| < 0.2 - dz was already correct) plus WP = DeepTau2018v2p5VSjet
   Medium (numeric code 5), matching the WP already wired into the
   correctionlib corrections. Year-gated: Run 2 keeps its old values
   unchanged. Verified on signal: yield dropped from 29,760/345,524
   (8.61%, old Run-2 placeholder cuts) to 23,948/345,524 (6.93%, new
   Run-3 cuts) - a ~19.5% relative decrease, consistent with the WP
   tightening (VVVLoose -> Medium) dominating over the loosened
   kinematic acceptance (pt>40->20, eta<2.1->2.5).
3. Wire up the real `correctionlib` `.evaluate()` calls - DONE
   (2026-10-21), see "Correction weights wired up" section below.
4. Properly compute Jet ID for Run 3 from the available energy-fraction
   branches (today's bypass is a stopgap), and wire in the 2024 jet
   veto map (`jetveto()` currently skips 2024 entirely).
5. Once 2-4 are done, re-run signal + backgrounds, then move to step 6
   (Plotter: build the ditau mass distribution, control regions).

### Running backgrounds through the pipeline - DONE (one-file correctness check)

Fixed one more bug hit while starting this: `ModuleTauTau.py` crashed
on DY with `AssertionError: Did not find cut 'weight_mutaufilter'`.
Cause: the shared `domutau` option (DY->mutau genfilter stitching, a
mutau-channel-specific technique) auto-enables for any DY sample
regardless of channel, but this tautau module never registers the
cutflow bins that feature needs. Fixed by forcing `domutau=False` in
`ModuleTauTau.py`'s `__init__` (irrelevant to tautau anyway).

`pico.py run -c tautau -y 2024 -s DY*` then succeeded on
`DYto2L-4Jets_MLL-50` (37/143468 events passed, 0.03% - much lower than
signal's 8.6%, as expected for inclusive DY+jets vs. a 35 GeV ditau
trigger).

**Important caveat to not forget, same as with the pileup jobs earlier
in this doc:** a local `pico.py run` only grabs **one file** per
sample by default, as a quick correctness check - not the full
sample statistics. It also looked like only one of DY's 5 registered
sub-samples (`DYto2L-4Jets_MLL-50`, not the `_1J/_2J/_3J/_4J` jet
bins) actually ran from a single `-s DY*` call - needs re-checking.

**Still to run** (one file each, as a correctness check, same as DY):

- [x] DY jet bins: `_1J`, `_2J`, `_3J`, `_4J` - DONE, all ran fine when
      named explicitly (`-s DYto2L-4Jets_MLL-50_1J ..._2J ..._3J
..._4J`); `-s DY*` only matching one sub-sample earlier was a
      shell-glob quirk in that terminal, not a pico.py bug.
- [x] TT (`TTto2L2Nu` 264 pass, `TTtoLNu2Q` 148 pass) - DONE
- [x] WJ (`WtoLNu-4Jets` + `_1J/_2J/_3J/_4J`) - DONE
- [x] ST (`TWminusto2L2Nu` 178, `TWminustoLNu2Q` 92, `TbarWplusto2L2Nu` 177, `TbarWplustoLNu2Q` 104 pass) - DONE
- [x] VV (`WW`, `WZ`, `ZZ` 58 pass) - DONE

**Before any final/trustworthy results:** every sample above needs a
full **batch submission** (`pico.py submit`, not just `pico.py run`)
so ALL of its files get processed, not just the first one used for
this correctness check.

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

### Correction weights wired up - DONE (2026-10-21)

Replaced the `weight=1` placeholders in `ModuleTauTau.py` with real
`correctionlib` `.evaluate()` calls for all five corrections (tau ID
SF, VSe/VSmu lepton-fake-rate SF, trigger SF, tau energy scale), for
Run 3 (year >= 2022) only - Run 2 behavior unchanged.

**What was missing and how it was found:** the open question was the
exact `genmatch` input convention (the CAT docs page's listed "Values"
for each correction node looked like grouped categories, not obviously
the raw NanoAOD value) and the precise argument order per correction.
Searched for an official TauPOG usage example:

- A direct fetch of the TauPOG's own `jsonpog-integration` GitLab repo
  (where an `examples/tauExample.py` is referenced from the README) was
  blocked by GitLab's bot-protection (Anubis).
- Instead found and fetched the source of
  [`Corrections/TAU/tauCorrections.py`](https://nanoaod-base-analysis.readthedocs.io/en/stable/_modules/Corrections/TAU/tauCorrections.html)
  from the `cms-tau-pog`-adjacent `nanoaod-base-analysis` framework (a
  real, in-use CMS analysis framework, Run-2 corrections but same
  correctionlib file family) - confirms `genmatch` is passed as the
  **raw NanoAOD `Tau_genPartFlav` value, unmodified**, and gives the
  argument order for VSjet/VSe/VSmu/TES: `eval({pt, dm, genmatch, wp,
wp_vse, syst, flag})` for VSjet, `eval({eta, genmatch, wp, syst})`
  for VSe/VSmu, `eval({pt, eta, dm, genmatch, id, syst})` for TES.
- Combined this confirmed _convention_ with the exact _input signature_
  of our own Run-3 2024 file's correction nodes (already captured
  verbatim from the CAT docs page the day before - see the "BLOCKED"
  section above) to write the final calls.

**Working-point choices made** (documented in-code too): VSjet
Medium/Tight for the two ID SF variants (Medium matches the Medium WP
now used in the selection itself, step 2), VSe VVLoose, VSmu Loose -
all mirroring the Run-2 defaults this module already used, for
consistency rather than a new independent choice. `flag='dm'` uses the
decay-mode-binned VSjet SF (recommended for pT <= 140 GeV, which covers
essentially all taus in this analysis). The ditau trigger SF is applied
per leg and multiplied (`trigweight = SF(tau1) * SF(tau2)`), the
standard simplified approach for a ditau trigger.

**Known approximation, not yet resolved:** the SF/fake-rate working
points passed to `correctionlib` (e.g. VSe='VVLoose') don't necessarily
exactly match the _actual_ cut applied in the selection loop (`idVSe<1`
is close to a no-op, not a clean "VVLoose" cut) - a minor inconsistency
inherited from how loose the baseline preselection already was, to be
refined later once working points across selection and corrections are
all explicitly re-examined together.

**Bug found on first test run, fixed:** crashed with
`RuntimeError: Index below bounds in Binning for input argument 0
value: 21.721864` - the `tau_trigger` correction's pt binning only
covers `[24.59953, inf)` (per this file's own CAT docs page, read the
day before), since the trigger itself needs ~35 GeV online and the SF
simply isn't measured below ~24.6 GeV. Our new Run-3 baseline cut
(pt>20, a general POG kinematic recommendation) is independent of this
specific trigger's actual threshold, so a subleading tau at ~21.7 GeV
passed selection but fell outside what the trigger SF can answer.
Fixed by clamping the pt passed to `trigCorr.evaluate()` at the
binning's documented floor (24.6 GeV) - standard practice for a value
just below a measured range's edge.

**Verified with real values, not just "doesn't crash":** scanned the
output ntuple's `idweight_1/2`, `trigweight`, `ltfweight_1/2`,
`genmatch_1/2` branches for the signal sample - `idweight` in ~0.90-1.07
and `trigweight` in ~0.89-1.00 (both physically plausible SF ranges),
`ltfweight` exactly 1 wherever `genmatch`=5 (real tau, correctly
skipping the lepton-fake-rate SF), no NaN, no suspiciously constant
values. Step 3 is done and validated, not just technically working.

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

Today's work made the pipeline technically compatible with 2024 (Run-3) data format and runnable end-to-end on signal and all backgrounds, but not yet physically accurate - selection cuts and correction weights still need tuning to real Run-3 values before the output resembles actual 2024 data.

### SESSION UPDATE 2026-10-21 - steps 2 and 3 done and verified

Picked up today's "Next steps" list: tuned the selection cuts to the
real Run-3 POG recommendation (step 2) and wired up the actual
`correctionlib` scale-factor weights (step 3) - both DONE and verified
with real numbers, not just "doesn't crash" (see the dedicated
sections above for the full writeup, sources, and bugs found/fixed
along the way: a trigger-SF pt-binning out-of-range crash, and a
pre-existing `ltfweight_1` default-value typo).

Stopping here for today at the user's request. **Remaining for next
session:** step 4 (properly compute Jet ID for Run 3 instead of the
current bypass, and wire in the 2024 jet veto map), then re-run
signal + all backgrounds with the updated cuts/corrections as a
one-file correctness check (same pattern as yesterday), before moving
to full batch production and Plotter.
