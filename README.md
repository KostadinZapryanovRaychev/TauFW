On a Linux 8 node like `lxplus8`, you can use the `el8_amd64_gcc10` architecture instead of `slc7_*`.

Which CMSSW release should not really matter for post-processing of nanoAOD,
but if you like to use `combine` in the same repository, it is better to use at least the
[recommended release for the latest Combine version](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#setting-up-the-environment-and-installation),
see below.

### TauFW

To install `TauFW`:

### PicoProducer

(https://github.com/cms-nanoAOD/nanoAOD-tools):

```
cd $CMSSW_BASE/src/
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
scram b -j4
```

(https://github.com/cms-tau-pog/TauIDSFs):

```
cd $CMSSW_BASE/src/
git clone https://github.com/cms-tau-pog/TauIDSFs TauPOG/TauIDSFs
cmsenv
scram b -j4
```

If you want to use the lepton SFs from the HTT group, please do

```
cd $CMSSW_BASE/src/TauFW/PicoProducer/data/lepton/
rm -rf HTT
git clone https://github.com/CMS-HTT/LeptonEfficiencies HTT
```

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

### TauPOG corrections

For TauPOG-internal work: To create JSON files with TauPOG corrections for
[`correctionlib`](https://github.com/cms-nanoAOD/correctionlib),
please follow the instructions
[here](https://gitlab.cern.ch/cms-tau-pog/jsonpog-integration/-/blob/TauPOG_v2/POG/TAU/README4UPDATES.md).
From at least `CMSSW_11_3_X`, `correctionlib` should be pre-installed.

To create ROOT files including the measured SFs please install [`TauIDSFs` tool](https://github.com/cms-tau-pog/TauIDSFs).
Modify the `TauIDSFs/utils/createSFFiles.py` script to include your measured SFs into the script.
Finally, run the `TauFW/scripts/tau_createROOT.sh` to generate your ROOT files. They will be created into `TauFW/scripts/data/`
IMPORTANT: please comment and do not delete older SFs

The latest code used to create root files for SF can be taken from [here](https://github.com/saswatinandan/TauFW/blob/master/Fitter/createroot_TES.py)

## Analysis plan: Z' &rarr; tau tau (Run 3, hadronic channel)

Simple steps:

1. **Set up on lxplus.** Install a Run 3 CMSSW release and TauFW as described
   above (`PicoProducer`, `NanoAODTools`, `TauIDSFs`).

2. **Register the samples.** Add the private Z'(250) NanoAODSim signal
   (`/eos/cms/store/user/mileva/bsm3g/RunIII2024Summer24/M250/`), the main
   backgrounds (DY, ttbar, W+jets, QCD, diboson), and Run 3 data to
   PicoProducer's sample list, with the known signal cross sections
   (232.0 pb for M=250).

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
