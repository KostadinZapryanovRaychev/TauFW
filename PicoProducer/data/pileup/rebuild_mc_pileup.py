#!/usr/bin/env python3
# Rebuild MC_PileUp_2024.root with each sample's Pileup_nTrueInt histogram scaled by
# xsec/sumweights before summing, so the combined profile matches the actual MC mixture
# used in the analysis (instead of being dominated by whichever sample has the most raw
# stored events, as the unweighted tothist.Add(hist) in getMCProfile did by default).
#
# Run from $CMSSW_BASE/src/TauFW/PicoProducer/data/pileup/
#   python3 rebuild_mc_pileup.py
#
# Needs, per sample: xsec (pb, from Plotter/config/samples.py era=='2024' table) and
# sumweights (sum of genWeight over ALL raw processed events, from the 'weight' bin of
# the 'cutflow' histogram in the merged *_tautau.root file -- NOT the pileup-channel file,
# which only has the raw unweighted 'pileup' histogram).

import os
from ROOT import TFile
from getPileupProfiles import getMCProfile

ANALYSIS_DIR = "/eos/user/k/kraychev/analysis/2024"

# (GROUP, SAMPLE, XSEC_pb) -- from Plotter/config/samples.py, era=='2024'
samples_xsec = [
  ('DY', "DYto2L-4Jets_MLL-50",     5435.0),
  ('DY', "DYto2L-4Jets_MLL-50_1J",   975.4),
  ('DY', "DYto2L-4Jets_MLL-50_2J",   312.7),
  ('DY', "DYto2L-4Jets_MLL-50_3J",    92.77),
  ('DY', "DYto2L-4Jets_MLL-50_4J",    45.56),
  ('WJ', "WtoLNu-4Jets",           55370.0),
  ('WJ', "WtoLNu-4Jets_1J",         9170.0),
  ('WJ', "WtoLNu-4Jets_2J",         2933.0),
  ('WJ', "WtoLNu-4Jets_3J",          866.5),
  ('WJ', "WtoLNu-4Jets_4J",          417.2),
  ('VV', "WW",                        79.92),
  ('VV', "WZ",                        29.16),
  ('VV', "ZZ",                        12.86),
  ('TT', "TTto2L2Nu",                 80.9),
  ('TT', "TTtoLNu2Q",                334.8),
  ('ST', "TWminustoLNu2Q",            15.80),
  ('ST', "TWminusto2L2Nu",             3.82),
  ('ST', "TbarWplustoLNu2Q",          15.84),
  ('ST', "TbarWplusto2L2Nu",           3.83),
]

samples   = []  # (sample, pileup-file path) for getMCProfile
weights   = {}  # sample -> xsec/sumweights

for group, name, xsec in samples_xsec:
  pufile    = os.path.join(ANALYSIS_DIR, group, f"{name}_pileup.root")
  ttfile    = os.path.join(ANALYSIS_DIR, group, f"{name}_tautau.root")
  if not os.path.isfile(pufile):
    print(f">>> WARNING: missing {pufile}, skipping")
    continue
  if not os.path.isfile(ttfile):
    print(f">>> WARNING: missing {ttfile}, skipping")
    continue
  tf = TFile.Open(ttfile)
  cutflow = tf.Get("cutflow")
  assert cutflow, f"No 'cutflow' histogram in {ttfile}!"
  # NOTE: the 'weight' cut's bin LABEL is "no cut, weighted" (the title passed to
  # addcut), not "weight" (that's just the cut's internal dict key) -- and bin labels
  # here are set via SetBinLabel (not Fill(label,...)), so the axis isn't "alphanumeric"
  # and TAxis::FindBin(str) would silently fail anyway. addcut('weight',...,15) hardcodes
  # index 15 -> bin 16 (bin = 1+index), so just read that bin directly.
  sumw = cutflow.GetBinContent(16)
  tf.Close()
  assert sumw > 0, f"sumweights <= 0 for {name} ({sumw})!"
  scale = xsec / sumw
  samples.append((name, pufile))
  weights[name] = scale
  print(f">>> {name:28s} xsec={xsec:10.2f} pb  sumw={sumw:14.1f}  scale={scale:.6e}")

outfname = "MC_PileUp_2024_xsecweighted.root"
hist = getMCProfile(outfname, samples, channel="pileup", era="2024", weights=weights)
print(f">>> Wrote {outfname}: mean={hist.GetMean():.2f}")
print(">>> Compare to the real data profile (Data_PileUp_2024_69p2.root) and to the old")
print(">>> MC_PileUp_2024.root before replacing it.")
