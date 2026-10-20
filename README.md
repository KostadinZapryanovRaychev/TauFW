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
