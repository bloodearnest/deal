#!/bin/bash
cd $HOME/sim/deal
source ../bin/activate
exec nice -n 19 $@


