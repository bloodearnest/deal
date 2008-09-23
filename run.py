#import psyco
#psyco.full()
import sys
import trace
import report
from path import path

from sealedbid.model import SBModel
#from cda.model import CDAModel
from mds.mdsmodel import MdsModel

models = dict(
        #cda=CDAModel,
        sb=SBModel,
        mds=MdsModel
        )

args = {}
model = SBModel
output = path("results")
trace.enabled = False
res_fname = path("raw.dat")
series_fname = path("series.dat")

for arg in sys.argv[1:]:
    try:
        k,v = arg.split('=')
        if k == "model":
            model = models[v]
        elif k == "trace":
            trace.enabled = eval(v)
        elif k == "dir":
            output = path(v)
        elif k == "file":
            res_fname = path(v)
        elif k == "series":
            series_fname = path(v)
        else:
            args[k] = eval(v)
    except:
        pass # none = arg


m = model(**args)
m.run()

r = m.calc_results()

#print results
report.printr(r)
report.write(r, output/res_fname)
report.write_series(m, output/series_fname)

#from guppy import hpy
#h = hpy()
#print h.heap()


                  
