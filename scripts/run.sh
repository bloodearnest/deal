#!/bin/bash
run_n=$1; shift
outdir=$1; shift
mkdir -p $outdir # ensure results dir
exec python run.py $@ dir=$outdir trace=False 2>&1 > $outdir/log.$run_n


