# Description: Common configuration file for creating pico sample set plotting scripts
import re
from TauFW.Plotter.sample.utils import LOG, STYLE, ensuredir, repkey, joincuts, joinweights, ensurelist,\
                                       setera, getyear, loadmacro, Sel, Var
from TauFW.Plotter.sample.utils import getsampleset as _getsampleset

def getsampleset(channel,era,**kwargs):
  verbosity = LOG.getverbosity(kwargs)
  year     = getyear(era) # get integer year
  fname    = kwargs.get('fname', "$PICODIR/$SAMPLE_$CHANNEL$TAG.root" ) # file name pattern of pico files
  split    = kwargs.get('split',    ['DY'] if 'tau' in channel else [ ] ) # split samples (e.g. DY) into genmatch components
  mergeMC  = kwargs.get('mergeMC',  False        ) # merge all MC samples, useful for jet-to-tau FR measurements
  join     = kwargs.get('join',     ['VV','TT','ST'] ) # ['VV','Top'] ) # join samples (e.g. VV, top)
  rmsfs    = ensurelist(kwargs.get('rmsf', [ ]  )) # remove the tau ID SF, e.g. rmsf=['idweight_2','ltfweight_2']
  addsfs   = ensurelist(kwargs.get('addsf', [ ] )) # add extra weight to all samples
  weight   = kwargs.get('weight',   None         ) # weight for all MC samples
  dyweight = kwargs.get('dyweight', 'zptweight'  ) # weight for DY samples
  ttweight = kwargs.get('ttweight', 'ttptweight' ) # weight for ttbar samples
  filters  = kwargs.get('filter',   None         ) # only include these MC samples
  vetoes   = kwargs.get('vetoes',   None         ) # veto these MC samples
  #tag      = kwargs.get('tag',      ""           ) # extra tag for sample file names
  table    = kwargs.get('table',    True         ) # print sample set table
  setera(era) # set era for plot style and lumi-xsec normalization
  if split and 'TT' in split and 'Top' in join: # don't join TT & ST
    join.remove('Top')
    join += ['TT','ST']
  
  # SM BACKGROUND MC SAMPLES
  if 'UL' in era: # UltraLegacy
    expsamples = [ # table of MC samples to be converted to Sample objects
      # GROUP NAME                     TITLE                 XSEC      EXTRA OPTIONS
      ( 'WJ', "WJetsToLNu",            "W + jets",           52940.0  ),
      ( 'WJ', "W1JetsToLNu",           "W + 1J",              8104.0  ),
      ( 'WJ', "W2JetsToLNu",           "W + 2J",              2793.0  ),
      ( 'WJ', "W3JetsToLNu",           "W + 3J",               992.5  ),
      ( 'WJ', "W4JetsToLNu",           "W + 4J",               544.3  ),
      ( 'DY', "DYJetsToLL_M-10to50",   "Drell-Yan 10-50",    18610.0  ),
      ( 'DY', "DYJetsToLL_M-50",       "Drell-Yan 50",        5343.0, {'extraweight': dyweight} ), # apply k-factor in stitching
      ( 'DY', "DY1JetsToLL_M-50",      "Drell-Yan 1J 50",      877.8, {'extraweight': dyweight} ),
      ( 'DY', "DY2JetsToLL_M-50",      "Drell-Yan 2J 50",      304.4, {'extraweight': dyweight} ),
      ( 'DY', "DY3JetsToLL_M-50",      "Drell-Yan 3J 50",      111.5, {'extraweight': dyweight} ),
      ( 'DY', "DY4JetsToLL_M-50",      "Drell-Yan 4J 50",      44.05, {'extraweight': dyweight} ),
      ( 'VV', "WW",                    "WW",                    75.88 ),
      ( 'VV', "WZ",                    "WZ",                    27.6  ),
      ( 'VV', "ZZ",                    "ZZ",                    12.14 ),
      ( 'TT', "TTTo2L2Nu",             "ttbar 2l2#nu",          88.29, {'extraweight': ttweight} ),
      ( 'TT', "TTToHadronic",          "ttbar hadronic",       377.96, {'extraweight': ttweight} ),
      ( 'TT', "TTToSemiLeptonic",      "ttbar semileptonic",   365.35, {'extraweight': ttweight} ),
      ( 'ST', "ST_t-channel_top",      "ST t-channel t",       136.02 ),
      ( 'ST', "ST_t-channel_antitop",  "ST t-channel at",       80.95 ),
      ( 'ST', "ST_tW_top",             "ST tW",                 35.85 ),
      ( 'ST', "ST_tW_antitop",         "ST atW",                35.85 )
    ]
    #if 'mutau' in channel:
    #  expsamples.append(('DY',"DYJetsToMuTauh_M-50","DYJetsToMuTauh_M-50",5343.0,{'extraweight': dyweight})) # apply correct normalization in stitching
  elif era=='2016': # pre-UL
    expsamples = [ # table of MC samples to be converted to Sample objects
      # GROUP NAME                     TITLE                 XSEC      EXTRA OPTIONS
      ( 'DY', "DYJetsToLL_M-10to50",   "Drell-Yan 10-50",    18610.0, {'extraweight': dyweight} ),
      ( 'DY', "DYJetsToLL_M-50",       "Drell-Yan 50",        4963.0, {'extraweight': dyweight} ), # apply k-factor in stitching
      ( 'DY', "DY1JetsToLL_M-50",      "Drell-Yan 1J 50",     1012.0, {'extraweight': dyweight} ),
      ( 'DY', "DY2JetsToLL_M-50",      "Drell-Yan 2J 50",      334.7, {'extraweight': dyweight} ),
      ( 'DY', "DY3JetsToLL_M-50",      "Drell-Yan 3J 50",      102.3, {'extraweight': dyweight} ),
      ( 'DY', "DY4JetsToLL_M-50",      "Drell-Yan 4J 50",      54.52, {'extraweight': dyweight} ),
      ( 'WJ', "WJetsToLNu",            "W + jets",           50260.0  ),
      ( 'WJ', "W1JetsToLNu",           "W + 1J",              9625.0  ),
      ( 'WJ', "W2JetsToLNu",           "W + 2J",              3161.0  ),
      ( 'WJ', "W3JetsToLNu",           "W + 3J",               954.8  ),
      ( 'WJ', "W4JetsToLNu",           "W + 4J",               494.6  ),
      ( 'VV', "WW",                    "WW",                    75.88 ),
      ( 'VV', "WZ",                    "WZ",                    27.6  ),
      ( 'VV', "ZZ",                    "ZZ",                    12.14 ),
      ( 'TT', "TT",                    "ttbar",                831.76, {'extraweight': ttweight} ),
      ( 'ST', "ST_t-channel_top",      "ST t-channel t",       136.02 ),
      ( 'ST', "ST_t-channel_antitop",  "ST t-channel at",       80.95 ),
      ( 'ST', "ST_tW_top",             "ST tW",                 35.85 ),
      ( 'ST', "ST_tW_antitop",         "ST atW",                35.85 ),
    ]
  elif era=='2017': # pre-UL
    expsamples = [ # table of MC samples to be converted to Sample objects
      # GROUP NAME                     TITLE                 XSEC      EXTRA OPTIONS
      ( 'DY', "DYJetsToLL_M-10to50",   "Drell-Yan 10-50",    18610.0, {'extraweight': dyweight} ), # apply k-factor in stitching
      ( 'DY', "DYJetsToLL_M-50",       "Drell-Yan 50",        5343.0, {'extraweight': dyweight} ),
      ( 'DY', "DY1JetsToLL_M-50",      "Drell-Yan 1J 50",      877.8, {'extraweight': dyweight} ),
      ( 'DY', "DY2JetsToLL_M-50",      "Drell-Yan 2J 50",      304.4, {'extraweight': dyweight} ),
      ( 'DY', "DY3JetsToLL_M-50",      "Drell-Yan 3J 50",      111.5, {'extraweight': dyweight} ),
      ( 'DY', "DY4JetsToLL_M-50",      "Drell-Yan 4J 50",      44.05, {'extraweight': dyweight} ),
      ( 'WJ', "WJetsToLNu",            "W + jets",           52940.0  ),
      ( 'WJ', "W1JetsToLNu",           "W + 1J",              8104.0  ),
      ( 'WJ', "W2JetsToLNu",           "W + 2J",              2793.0  ),
      ( 'WJ', "W3JetsToLNu",           "W + 3J",               992.5  ),
      ( 'WJ', "W4JetsToLNu",           "W + 4J",               544.3  ),
      ( 'VV', "WW",                    "WW",                    75.88 ),
      ( 'VV', "WZ",                    "WZ",                    27.6  ),
      ( 'VV', "ZZ",                    "ZZ",                    12.14 ),
      ( 'TT', "TTTo2L2Nu",             "ttbar 2l2#nu",          88.29, {'extraweight': ttweight} ),
      ( 'TT', "TTToHadronic",          "ttbar hadronic",       377.96, {'extraweight': ttweight} ),
      ( 'TT', "TTToSemiLeptonic",      "ttbar semileptonic",   365.35, {'extraweight': ttweight} ),
      ( 'ST', "ST_t-channel_top",      "ST t-channel t",       136.02 ),
      ( 'ST', "ST_t-channel_antitop",  "ST t-channel at",       80.95 ),
      ( 'ST', "ST_tW_top",             "ST tW",                 35.85 ),
      ( 'ST', "ST_tW_antitop",         "ST atW",                35.85 ),
    ]
  elif era=='2018': # pre-UL
    expsamples = [ # table of MC samples to be converted to Sample objects
      # GROUP NAME                     TITLE                 XSEC      EXTRA OPTIONS
      #( 'DY', "DYJetsToLL_M-10to50",   "Drell-Yan 10-50",    18610.0, {'extraweight': dyweight} ),
      ( 'DY', "DYJetsToLL_M-50",       "Drell-Yan 50",        5343.0, {'extraweight': dyweight} ), # apply k-factor while stitching
      ( 'DY', "DY1JetsToLL_M-50",      "Drell-Yan 1J 50",      877.8, {'extraweight': dyweight} ),
      ( 'DY', "DY2JetsToLL_M-50",      "Drell-Yan 2J 50",      304.4, {'extraweight': dyweight} ),
      ( 'DY', "DY3JetsToLL_M-50",      "Drell-Yan 3J 50",      111.5, {'extraweight': dyweight} ),
      ( 'DY', "DY4JetsToLL_M-50",      "Drell-Yan 4J 50",      44.05, {'extraweight': dyweight} ),
      ( 'WJ', "WJetsToLNu",            "W + jets",           52940.0  ),
      ( 'WJ', "W1JetsToLNu",           "W + 1J",              8104.0  ),
      ( 'WJ', "W2JetsToLNu",           "W + 2J",              2793.0  ),
      ( 'WJ', "W3JetsToLNu",           "W + 3J",               992.5  ),
      ( 'WJ', "W4JetsToLNu",           "W + 4J",               544.3  ),
      ( 'VV', "WW",                    "WW",                    75.88 ),
      ( 'VV', "WZ",                    "WZ",                    27.6  ),
      ( 'VV', "ZZ",                    "ZZ",                    12.14 ),
      ( 'TT', "TTTo2L2Nu",             "ttbar 2l2#nu",          88.29, {'extraweight': ttweight} ),
      ( 'TT', "TTToHadronic",          "ttbar hadronic",       377.96, {'extraweight': ttweight} ),
      ( 'TT', "TTToSemiLeptonic",      "ttbar semileptonic",   365.35, {'extraweight': ttweight} ),
      ( 'ST', "ST_t-channel_top",      "ST t-channel t",       136.02 ),
      ( 'ST', "ST_t-channel_antitop",  "ST t-channel at",       80.95 ),
      ( 'ST', "ST_tW_top",             "ST tW",                 35.85 ),
      ( 'ST', "ST_tW_antitop",         "ST atW",                35.85 ),
    ]
  elif era=='2024': # Run 3, 2024 data-taking
    # XSEC: computed on lxplus via GenXsecAnalyzer over MiniAODSIM (5 files/sample), 2026-10-29.
    # See PicoProducer/data/xsec/ (genxsec_cfg.py, run_genxsec.sh, logs/) and README.md
    # "References & sources" section for the full method and raw logs.
    # TT and ST (tW) samples are decay-mode-split at the Pythia8 level, not at the LHE
    # generator-filter level, so GenXsecAnalyzer reports the same *inclusive* cross section
    # for every decay-mode sample from the same gridpack. These were rescaled by the
    # standard PDG W branching fractions (BR(W->lnu)=0.3259, BR(W->had)=0.6741):
    #   BR(2l2nu) = 0.3259^2        = 0.1062
    #   BR(lnu2q) = 2*0.3259*0.6741 = 0.4392
    expsamples = [ # table of MC samples to be converted to Sample objects
      # GROUP NAME                          TITLE                 XSEC      EXTRA OPTIONS
      ( 'DY', "DYto2L-4Jets_MLL-50",        "Drell-Yan 50",       5435.0, {'extraweight': dyweight} ), # apply k-factor in stitching
      ( 'DY', "DYto2L-4Jets_MLL-50_1J",     "Drell-Yan 1J 50",     975.4, {'extraweight': dyweight} ),
      ( 'DY', "DYto2L-4Jets_MLL-50_2J",     "Drell-Yan 2J 50",     312.7, {'extraweight': dyweight} ),
      ( 'DY', "DYto2L-4Jets_MLL-50_3J",     "Drell-Yan 3J 50",      92.77, {'extraweight': dyweight} ),
      ( 'DY', "DYto2L-4Jets_MLL-50_4J",     "Drell-Yan 4J 50",      45.56, {'extraweight': dyweight} ),
      ( 'WJ', "WtoLNu-4Jets",               "W + jets",          55370.0  ),
      ( 'WJ', "WtoLNu-4Jets_1J",            "W + 1J",              9170.0  ),
      ( 'WJ', "WtoLNu-4Jets_2J",            "W + 2J",              2933.0  ),
      ( 'WJ', "WtoLNu-4Jets_3J",            "W + 3J",                866.5 ),
      ( 'WJ', "WtoLNu-4Jets_4J",            "W + 4J",                417.2 ),
      ( 'VV', "WW",                         "WW",                    79.92 ),
      ( 'VV', "WZ",                         "WZ",                    29.16 ),
      ( 'VV', "ZZ",                         "ZZ",                    12.86 ),
      ( 'TT', "TTto2L2Nu",                  "ttbar 2l2#nu",          80.9, {'extraweight': ttweight} ), # 762.1*0.1062
      ( 'TT', "TTtoLNu2Q",                  "ttbar semileptonic",   334.8, {'extraweight': ttweight} ), # 762.1*0.4392
      ( 'ST', "TWminustoLNu2Q",             "ST tW semileptonic",    15.80 ), # 35.99*0.4392
      ( 'ST', "TWminusto2L2Nu",             "ST tW 2l2#nu",           3.82 ), # 35.99*0.1062
      ( 'ST', "TbarWplustoLNu2Q",           "ST atW semileptonic",   15.84 ), # 36.05*0.4392
      ( 'ST', "TbarWplusto2L2Nu",           "ST atW 2l2#nu",          3.83 ), # 36.05*0.1062
    ]
  else:
    LOG.throw(IOError,"Did not recognize era %r!"%(era))

  # OBSERVED DATA SAMPLES
  if   'tautau'   in channel: dataset = "Tau_Run%d?"%year
  elif 'mutau'    in channel: dataset = "SingleMuon_Run%d?"%year
  elif 'etau'     in channel: dataset = "EGamma_Run%d?"%year if year==2018 else "SingleElectron_Run%d?"%year
  elif 'mumu'     in channel: dataset = "SingleMuon_Run%d?"%year
  elif 'emu'      in channel: dataset = "SingleMuon_Run%d?"%year
  elif 'ee'       in channel: dataset = "EGamma_Run%d?"%year if year==2018 else "SingleElectron_Run%d?"%year
  elif 'mumutau'  in channel: dataset = "SingleMuon_Run%d?"%year
  elif 'eetau'    in channel: dataset = "EGamma_Run%d?"%year if year==2018 else "SingleElectron_Run%d?"%year  
  elif 'mumettau' in channel: dataset = "SingleMuon_Run%d?"%year
  else: LOG.throw(IOError,"Did not recognize channel %r!"%(channel))
  datasample = ('Data',dataset) # GROUP, NAME
  
  # FILTER
  if filters:
    expsamples = [s for s in expsamples if any(f in s[0] for f in filters)]
  if vetoes:
    expsamples = [s for s in expsamples if not any(v in s[0] for v in vetoes)]
  
  # SAMPLE SET
  if weight!=None:
    weight = ""
  elif channel in ['munu']:
    weight = "genweight*trigweight*puweight*idisoweight_1*kfactor_mu"
  elif channel in ['mutau','etau']:
    weight = "genweight*trigweight*puweight*idisoweight_1*idweight_2*ltfweight_2"
  elif channel in ['tautau','ditau']:
    weight = "genweight*trigweight*puweight*idweight_1*idweight_2*ltfweight_1*ltfweight_2"
  elif channel in ['mumutau','eetau']:
    weight = "genweight*trigweight*puweight*idisoweight_1*idisoweight_2" #genweight*trigweight*puweight*idisoweight_1*idisoweight_2*ltfweight_tau 
  elif channel in ['mumettau','emettau']:
    weight = "genweight*trigweight*puweight*idisoweight_1" # ltfweight_tau 
  else: # mumu, emu, ...
    weight = "genweight*trigweight*puweight*idisoweight_1*idisoweight_2"
  for sf in rmsfs: # remove (old) SFs, e.g. for SF measurement
    weight = weight.replace(sf,"").replace("**","*").strip('*')
  for sf in addsfs:  # add extra SFs, e.g. for SF measurement
    weight = joinweights(weight,sf)
  kwargs.setdefault('weight',weight) # common weight for MC
  kwargs.setdefault('fname', fname)  # default filename pattern
  sampleset = _getsampleset(datasample,expsamples,channel=channel,era=era,**kwargs)
  LOG.verb("weight = %r"%(weight),verbosity,1)
  
  # STITCH
  # Note: titles are set via STYLE.sample_titles
  if era=='2024':
    # NOTE: for 2022/2023/2024 eras, stitch() matches the inclusive sample by exact
    # sample name (not group name) -- see Plotter/python/sample/utils.py:414-417,
    # and the working example in Plotter/config/samples_v12.py.
    sampleset.stitch("WtoLNu-4Jets*",        incl='WtoLNu-4Jets',        name='WJ'     ) # W + jets
    sampleset.stitch("DYto2L-4Jets_MLL-50*", incl='DYto2L-4Jets_MLL-50', name="DY_M50" )
  else:
    sampleset.stitch("W*Jets",    incl='WJ',  name='WJ'     ) # W + jets
    sampleset.stitch("DY*J*M-50", incl='DYJ', name="DY_M50")
    ## The following skimming efficiencies should be removed when running on nTuples with corrected cutflow content!!!!
    #                 eff_nanoAOD_DYll=0.47435726,
    #                 eff_nanoAOD_DYll_0orp4j=0.439206,
    #                 eff_nanoAOD_DYll_1j=0.54153996,
    #                 eff_nanoAOD_DYll_2j=0.59700258,
    #                 eff_nanoAOD_DYll_3j=0.65562099,
    #                 eff_nanoAOD_DYll_4j=0.74383978,
    #                 eff_nanoAOD_mutau=0.82747870,
    #                 eff_nanoAOD_mutau_0orp4j=0.814466,
    #                 eff_nanoAOD_mutau_1j=0.847658,
    #                 eff_nanoAOD_mutau_2j=0.867779,
    #                 eff_nanoAOD_mutau_3j=0.889908,
    #                 eff_nanoAOD_mutau_4j=0.922111) # Drell-Yan, M > 50 GeV
  #sampleset.stitch("DY*J*M-10to50", incl='DYJ', name="DY_M10to50" )
  
  # JOIN
  sampleset.join('DY', name='DY' ) # Drell-Yan, M < 50 GeV + M > 50 GeV
  if 'VV' in join:
    sampleset.join('VV','WZ','WW','ZZ', name='VV' ) # Diboson
  if 'TT' in join and era!='year':
    sampleset.join('TT', name='TT' ) # ttbar
  if 'ST' in join:
    sampleset.join('ST', name='ST' ) # single top
  if 'Top' in join:
    sampleset.join('TT','ST', name='Top' ) # ttbar + single top
  if mergeMC:
    sampleset.join('VV','TT','ST','DY','WJ', name='Simulation')
  
  # SPLIT
  # Note: titles are set via STYLE.sample_titles
  if split and channel.count('tau')==1:
    ZTT = STYLE.sample_titles.get('ZTT',"Z -> %s"%channel) # title
    if channel.count('tau')==1:
      ZTT = ZTT.replace("{l}","{mu}" if "mu" in channel else "{e}")
      GMR = "genmatch_2==5"
      GML = "genmatch_2>0 && genmatch_2<5"
      GMJ = "genmatch_2==0"
      GMF = "genmatch_2<5"
    elif channel.count('tau')==2:
      ZTT = ZTT.replace("{l}","{h}")
      GMR = "genmatch_1==5 && genmatch_2==5"
      GML = "(genmatch_1<5 || genmatch_2<5) && genmatch_1>0 && genmatch_2>0"
      GMJ = "(genmatch_1==0 || genmatch_2==0)"
      GMF = "(genmatch_1<5 || genmatch_2<5)"
    else:
      LOG.throw(IOError,"Did not recognize channel %r!"%(channel))
    if 'DM' in split: # split DY by decay modes
      samples.split('DY', [('ZTTDM0', ZTT+", h^{#pm}",                   GMR+" && dm_2==0"),
                           ('ZTTDM1', ZTT+", h^{#pm}h^{0}",              GMR+" && dm_2==1"),
                           ('ZTTDM10',ZTT+", h^{#pm}h^{#mp}h^{#pm}",     GMR+" && dm_2==10"),
                           ('ZTTDM11',ZTT+", h^{#pm}h^{#mp}h^{#pm}h^{0}",GMR+" && dm_2==11"),
                           ('ZL',GML),('ZJ',GMJ),])
    elif 'DY' in split:
      sampleset.split('DY',[('ZTT',ZTT,GMR),('ZL',GML),('ZJ',GMJ),])
    if 'TT' in split:
      sampleset.split('TT',[('TTT',GMR),('TTJ',GMF),])
  
  if table:
    sampleset.printtable(merged=True,split=True)
  print(">>> common weight: %r"%(weight))
  return sampleset
  
