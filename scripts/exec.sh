#!/bin/bash
# limit memory to half system memory
mem=`cat /proc/meminfo | head -n 1 | awk '{print $2}'`
half_mem_k=$(($mem/2))
ulimit -m $half_mem_k
ulimit -v $half_mem_k
exec nice -n 19 $@


