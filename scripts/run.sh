#!/bin/bash
run_n=$1; shift
outdir=$1; shift
mkdir -p $outdir # ensure results dir
opts="trace=False -dAgg"
exec python -OO run.py $@ dir=$outdir $opts 2>&1 > $outdir/log.$run_n


