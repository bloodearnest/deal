#!/bin/bash

# parse run args
cd $HOME/deal
run_n=$1; shift
outdir=$1; shift
logfile=$outdir/log.$run_n

#set env
source ~/bin/virtualenv_tools
ver=`python -c "import sys; print sys.version_info[:3]"`
if [ "$ver" == "(2, 5, 1)" ]; then
    workon sim2.5.1-cslin
    echo "using sim2.5.1-cslin" > $logfile
elif [ "$ver" == "(2, 5, 0)" ]; then
    workon sim2.5.0-gps
    echo "using sim2.5.0-gps" > $logfile
else
    echo "no suitable env found: $ver" > $logfile
    exit 1
fi

mkdir -p $outdir # ensure results dir
echo `which python` >> $logfile
opts="trace=False -dAgg" # disable trace and set matplot not to use gtk
exec python -O run.py $@ dir=$outdir $opts 2>&1 >> $logfile


