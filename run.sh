#!/bin/bash

x=$1
mkdir -p $x
shift
cd $HOME/sim
. bin/activate
cd deal
python $@ 2>&1 > $x/out.log
