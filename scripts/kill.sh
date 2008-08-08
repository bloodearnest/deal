#!/bin/bash
for host in `cat ~/.machinelist `; do
  echo "killing on $host"
  (ssh -x $host "kill -9 -1 2>&1 > /dev/null" 2>/dev/null 1>/dev/null &) 2>/dev/null 1>/dev/null
done 
