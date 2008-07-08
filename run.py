#import psyco
#psyco.full()
import sys
import trace
import record
import report
from stats import dists
from path import path

from sealedbid.model import SBModel
#from cda.model import CDAModel

models = dict(
        #cda=CDAModel,
        sb=SBModel
        )

args = {}
model = SBModel
output = path("results")
trace.enabled = False
fname = path("raw.dat")

for arg in sys.argv[1:]:
    k,v = arg.split('=')
    if k == "model":
        the_model = models[v]
    elif k == "trace":
        trace.enabled = eval(v)
    elif k == "dir":
        output = path(v)
    elif k == "file":
        fname = path(v)
    else:
        args[k] = eval(v)


m = model(**args)
m.run()

r = record.calc_results(m)

#print results
report.printr(r)
report.write(r, output, fname)


                  
