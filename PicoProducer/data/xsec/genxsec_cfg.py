import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

options = VarParsing.VarParsing('analysis')
options.register('dataset', '', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string,
                  "DAS dataset name, only used for the printed label")
options.parseArguments()

process = cms.Process("GenXSec")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles)
)
process.dummy = cms.EDAnalyzer("GenXSecAnalyzer")
process.p = cms.Path(process.dummy)

print(">>> Running GenXsecAnalyzer for dataset: %s" % options.dataset)
print(">>> Number of input files: %d" % len(options.inputFiles))
