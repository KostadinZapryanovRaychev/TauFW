#!/bin/bash
# Usage: ./run_genxsec.sh <MiniAODSIM DAS dataset name> [nfiles]
# Example:
#   ./run_genxsec.sh /TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-...*/MINIAODSIM 5
#
# Requires: cmsenv already set up, valid grid proxy (voms-proxy-init -voms cms), dasgoclient available.

set -e

DATASET="$1"
NFILES="${2:-5}"

if [ -z "$DATASET" ]; then
  echo "Usage: $0 <MiniAODSIM dataset> [nfiles]"
  exit 1
fi

echo ">>> Querying DAS for files in: $DATASET"
FILES=$(dasgoclient -query="file dataset=$DATASET" | head -n "$NFILES")

if [ -z "$FILES" ]; then
  echo "!!! No files found for dataset $DATASET"
  exit 1
fi

INPUTFILES=""
for f in $FILES; do
  INPUTFILES="$INPUTFILES inputFiles=root://cms-xrd-global.cern.ch/$f"
done

echo ">>> Using $NFILES file(s):"
echo "$FILES"
echo ">>> Running cmsRun..."

mkdir -p logs
SAMPLENAME=$(basename "$DATASET" | cut -d/ -f1)
LOGFILE="logs/${SAMPLENAME}_$(date +%Y%m%d_%H%M%S).log"

cmsRun genxsec_cfg.py dataset="$DATASET" $INPUTFILES 2>&1 | tee "$LOGFILE"
echo ">>> Full log saved to: $LOGFILE"
