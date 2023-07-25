from hepdata_lib import Submission, Table, Variable, Uncertainty
import numpy as np
import os
from auxiliars import *
import re
import ROOT

# Always at the start
submission = Submission()

## To be filled later
submission.read_abstract("abstract.txt")
#submission.add_link("Webpage with all figures and tables", "https://cms-results.web.cern.ch/cms-results/public-results/publications/SMP-20-014/")
#submission.add_link("arXiv", "http://arxiv.org/abs/arXiv:21XX.XXXXX")
#submission.add_record_id(XXXXXX, "inspire")


common_extras = [["WZ","prompt_WZ"],
                 ["qq$\\rightarrow$ZZ","prompt_ZZ"],
                 ["gg$\\rightarrow$ZZ","prompt_ggZZ"],
                 ["ttX","prompt_TTX"],
                 ["tZq","prompt_TZQ"],
                 ["VH","prompt_VH"],
                 ["VVV","prompt_VVV"],
                 ["Nonprompt","data_fakes"],
                 ["Conversions", "convs"]]
#os.system("sh copyPlots.sh")

def getFigureFrom2DScan(inFile, inTH2D, depUncs = [], pdf = None, qualifiers = [], obs = None, location = "", title = "", xlabels = "", ylabels = [], unitsx="", unitsy="", lims = [-1000,1000,-1000,1000], ttitle=""):
  print "Loading info from TH2D in %s..."%inFile
  inPDF = pdf
  theF = ROOT.TFile(inFile,"READ")
  theH = theF.Get(inTH2D)
  xvals1, xvals2, yvals = [], [], [] 
  for i in range(1, theH.GetNbinsX()+1):
    if i%100 == 0: print "... step %i/%i"%(i, theH.GetNbinsX()+1)
    for j in range(1, theH.GetNbinsY()+1):
      x1 = theH.GetXaxis().GetBinCenter(i)
      x2 = theH.GetYaxis().GetBinCenter(j)
      if x1 >= lims[0] and x1 <= lims[1] and x2 >= lims[2] and x2 <= lims[3]:
        xvals1.append(x1)
        xvals2.append(x2)
        yvals.append(theH.GetBinContent(i,j))

  fig = Table(ttitle)
  fig.description = title
  fig.location    = location
  fig.keywords["observables"] = obs

  ## X axis
  xvar1 = Variable(xlabels[0], is_independent=True, is_binned=False, units=unitsx)
  xvar1.values = xvals1
  xvar2 = Variable(xlabels[1], is_independent=True, is_binned=False, units=unitsx)
  xvar2.values = xvals2
  fig.add_variable(xvar1)
  fig.add_variable(xvar2)

  # Y axis, data
  yvar = Variable(ylabels, is_independent=False, is_binned=False, units=unitsy)
  yvar.values = yvals
  for q in qualifiers:
    yvar.add_qualifier(*q)
  fig.add_variable(yvar)
  fig.add_image(inPDF)
  submission.add_table(fig)



def getFigureFromTuples(inTuple, depTuples, depUncs = [], pdf = None, qualifiers = [], obs = None, location = "", title = "", xlabel = "", ylabels = [], unitsx="", unitsy="", ttitle=""):
  inPDF = pdf 
  fig = Table(ttitle)
  fig.description = title
  fig.location    = location
  fig.keywords["observables"] = obs

  ## X axis
  xvar = Variable(xlabel, is_independent=True, is_binned=False, units=unitsx)
  xvar.values = inTuple
  fig.add_variable(xvar)

  # Y axis, data
  for yv in range(len(depTuples)):
    yvar = Variable(ylabels[yv], is_independent=False, is_binned=False, units=unitsy)
    yvar.values = depTuples[yv]
    uncy = Uncertainty("Total", is_symmetric=False)
    if len(depUncs[yv]) == 2: # Then we need to merge this stuff
      depUncs[yv] = [[depUncs[yv][0][iunc]-depTuples[yv][iunc], depUncs[yv][1][iunc]-depTuples[yv][iunc]] for iunc in range(len(depUncs[yv][0]))]
    uncy.values = depUncs[yv]
    yvar.add_uncertainty(uncy)
    for q in qualifiers:
      yvar.add_qualifier(*q)
    fig.add_variable(yvar)
  fig.add_image(inPDF)
  submission.add_table(fig)


def get2DFigureFromROOT(rootfile, hist2d, xlims = None, ylims = None, depUncs = [], pdf = None, qualifiers = [], obs = None, location = "", title = "", xlabel = "", ylabel = "", zlabel="", unitsx="", unitsy="", unitsz="", ttitle=""):
  inPDF = pdf
  fig = Table(ttitle)
  fig.description = title
  fig.location    = location
  fig.keywords["observables"] = obs
  rf = ROOT.TFile(rootfile, "READ")
  h2 = rf.Get(hist2d)
  xvals = []
  yvals = []
  zvals = []
  if not(xlims) or not(ylims):
    for i in range(1, h2.GetNbinsX()+1):
      for j in range(1, h2.GetNbinsY()+1):
        xvals.append([h2.GetXaxis().GetBinLowEdge(i), h2.GetXaxis().GetBinLowEdge(i+1)])
        yvals.append([h2.GetYaxis().GetBinLowEdge(j), h2.GetYaxis().GetBinLowEdge(j+1)])
        zvals.append(h2.GetBinContent(i,j))
  else:
    for i in range(1, h2.GetNbinsX()+1):
      for j in range(1, h2.GetNbinsY()+1):
        xvals.append(xlims[i])
        yvals.append(ylims[j])
        zvals.append(h2.GetBinContent(i,j))

  ## X axis
  xvar = Variable(xlabel, is_independent=True, is_binned=True, units=unitsx)
  xvar.values = xvals
  fig.add_variable(xvar)
  yvar = Variable(ylabel, is_independent=True, is_binned=True, units=unitsy)
  yvar.values = yvals
  fig.add_variable(yvar)

  zvar = Variable(zlabel, is_independent=False, is_binned=False, units=unitsz)
  zvar.values = zvals
  for q in qualifiers:
    zvar.add_qualifier(*q)
  fig.add_variable(zvar)

  fig.add_image(inPDF)
  submission.add_table(fig)


def get2DScanFromText(txtfile, depUncs = [], pdf = None, qualifiers = [], obs = None, location = "", title = "", xlabel = "", ylabel = "", zlabel="", unitsx="GeV", unitsy="GeV", unitsz="", ttitle=""):
  print txtfile
  inPDF = pdf
  fig = Table(ttitle)
  fig.description = title
  fig.location    = location
  fig.keywords["observables"] = obs
  theDict = {"Mass1": 0, "Mass2": 1, "Expected, median":4, "Obsserved":7, "Expected, -2$\sigma$": 2, "Expected, -1$\sigma$":3, "Expected, +1$\sigma$": 5, "Expected, +2$\sigma$":6}  
  theVals = {i:[] for i in theDict.keys()}
  xvals = []
  yvals = []
  theFile = open(txtfile,"r")
  for line in theFile.readlines():
     newvals = [float(a.replace(" ", "")) for a in line.split(":")]
     if len(newvals) < 7 or any([nn > 999 for nn in newvals]): continue
     for key in theVals.keys():
        theVals[key].append(newvals[theDict[key]])
     xvals.append(newvals[theDict["Mass1"]])
     yvals.append(newvals[theDict["Mass2"]])

  ## X axis
  xvar = Variable(xlabel, is_independent=True, is_binned=False, units=unitsx)
  xvar.values = xvals
  fig.add_variable(xvar)
  yvar = Variable(ylabel, is_independent=True, is_binned=False, units=unitsy)
  yvar.values = yvals
  fig.add_variable(yvar)  
  zvars = []
  for key in theDict.keys():
       if "Mass" in key: continue 
       zvars.append(Variable(key + zlabel, is_independent=False, is_binned=False, units=unitsz))
       zvars[-1].values = theVals[key]

       for q in qualifiers:
         zvars[-1].add_qualifier(*q)
       fig.add_variable(zvars[-1])

  fig.add_image(inPDF)
  submission.add_table(fig)

def get1DScanFromText(txtfile, depUncs = [], pdf = None, qualifiers = [], obs = None, location = "", title = "", xlabel = "", ylabel = "", zlabel="", unitsx="GeV", unitsy="GeV", unitsz="", ttitle=""):
  print txtfile
  inPDF = pdf
  fig = Table(ttitle)
  fig.description = title
  fig.location    = location
  fig.keywords["observables"] = obs
  theDict = {"Mass1": 0, "Mass2": 1, "Expected, median":4, "Obsserved":7, "Expected, -2$\sigma$": 2, "Expected, -1$\sigma$":3, "Expected, +1$\sigma$": 5, "Expected, +2$\sigma$":6}
  theVals = {i:[] for i in theDict.keys()}
  xvals = []
  yvals = []
  theFile = open(txtfile,"r")
  for line in theFile.readlines():
     newvals = [float(a.replace(" ", "")) for a in line.split(":")]
     if len(newvals) < 7 or any([nn > 999 for nn in newvals]): continue
     for key in theVals.keys():
        theVals[key].append(newvals[theDict[key]])
     xvals.append(newvals[theDict["Mass1"]])

  ## X axis
  xvar = Variable(xlabel, is_independent=True, is_binned=False, units=unitsx)
  xvar.values = xvals
  fig.add_variable(xvar)
  zvars = []
  for key in theDict.keys():
       if "Mass" in key: continue
       zvars.append(Variable(key + zlabel, is_independent=False, is_binned=False, units=unitsz))
       zvars[-1].values = theVals[key]

       for q in qualifiers:
         zvars[-1].add_qualifier(*q)
       fig.add_variable(zvars[-1])

  fig.add_image(inPDF)
  submission.add_table(fig)

 
def getFigureFromROOT( preroot, postroot, pdf, location, title, extras=common_extras, proc=None, obs=None, nbins=-1, limits=None, alt_data="data", alt_background="total_background", qualifiers= [("Process", "p p --> WZ --> l l l nu"), ("SQRT(S)", 13, "TeV")], ttitle=""):
  print "Including figure %s..."%title
  #### Reading stuff ####
  inPDF = pdf
  vals, dump, borders = readrootasnp(postroot, extras, alt_data, alt_background,nbins)
  dump, uncs, borders = readrootasnp(preroot, extras, alt_data, alt_background,nbins)
  nbins = len(borders)-1
  #### Create figure ####
  fig = Table(ttitle)
  fig.description = title
  fig.location    = "Data and expectations from %s"%location
  fig.keywords["observables"] = ["N"] if not obs else ["N", obs]
  fig.keywords["reactions"] = []
  if proc: fig.keywords["reactions"].append(proc)

  ## X axis
  xvar = Variable(obs, is_independent=True, is_binned=True, units="")
  xvar.values = [(borders[i],borders[i+1]) for i in range(nbins)]
  if limits: xvar.values = [[limits[i],limits[i+1]] for i in range(len(limits)-1)]
  print "...the binning is ", xvar.values
  # Y axis, data
  data = Variable("Observed data", is_independent=False, is_binned=False, units="Events per bin")
  data.values = vals["DATA"]
  uncdata = Uncertainty("Statistic")
  uncdata.values = uncs["DATA"]
  data.add_uncertainty(uncdata)
  for q in qualifiers:
    data.add_qualifier(*q)
  # Y axis, SM
  exp = Variable("Expected SM", is_independent=False, is_binned=False, units="Events per bin")
  exp.values = vals["Total"]
  uncexp = Uncertainty("Total")
  uncexp.values = uncs["Total"]
  exp.add_uncertainty(uncexp)
  for q in qualifiers:
    exp.add_qualifier(*q)
  fig.add_variable(xvar)
  fig.add_variable(data)
  fig.add_variable(exp)
  fig.add_image(inPDF)
  # Y axis extras
  more_yax = []
  more_uncs = []
  for e in extras:
    more_yax.append(Variable(e[0], is_independent=False, is_binned=False, units="Events per bin"))
    more_yax[-1].values = vals[e[0]]
    more_uncs.append(Uncertainty("Total"))
    more_uncs[-1].values = uncs[e[0]]
    more_yax[-1].add_uncertainty(more_uncs[-1])
    for q in qualifiers:
      more_yax[-1].add_qualifier(*q)
    fig.add_variable(more_yax[-1])
  submission.add_table(fig)

def getSRFigureFromROOT( preroot, postroot, pdf, location, title, extras=common_extras, proc=None, obs=None, nbins=-1, alt_data="data", alt_background="total_background", qualifiers= [("SQRT(S)", 13, "TeV")], ttitle="", prefix=""):
  print "Including figure %s..."%title
  #### Reading stuff ####
  inPDF = pdf
  vals, dump, borders = readrootasnp(postroot, extras, alt_data, alt_background,nbins,prefix=prefix)
  dump, uncs, borders = readrootasnp(preroot, extras, alt_data, alt_background,nbins,prefix=prefix)
  nbins = len(borders)-1
  #### Create figure ####
  fig = Table(ttitle)
  fig.description = title
  fig.location    = "Data and expectations from %s"%location
  fig.keywords["observables"] = ["N"] if not obs else ["N", obs]
  fig.keywords["reactions"] = []
  if proc: fig.keywords["reactions"].append(proc)

  ## X axis
  xvar = Variable(obs, is_independent=True, is_binned=False, units="")
  xvar.values = range(1,nbins+1) #[(borders[i],borders[i+1]) for i in range(nbins)]
  print "...the binning is ", xvar.values
  # Y axis, data
  data = Variable("Observed data", is_independent=False, is_binned=False, units="Events per bin")
  data.values = vals["DATA"]
  uncdata = Uncertainty("Statistic")
  uncdata.values = uncs["DATA"]
  data.add_uncertainty(uncdata)
  for q in qualifiers:
    data.add_qualifier(*q)
  # Y axis, SM
  exp = Variable("Expected SM", is_independent=False, is_binned=False, units="Events per bin")
  exp.values = vals["BACKGROUND"]
  uncexp = Uncertainty("Total")
  uncexp.values = uncs["BACKGROUND"]
  exp.add_uncertainty(uncexp)
  for q in qualifiers:
    exp.add_qualifier(*q)
  fig.add_variable(xvar)
  fig.add_variable(data)
  fig.add_variable(exp)
  fig.add_image(inPDF)
  # Y axis extras
  more_yax = []
  more_uncs = []
  for e in extras:
    if all([ term == 0 for term in vals[e[0]]]): continue
    more_yax.append(Variable(e[0], is_independent=False, is_binned=False, units="Events per bin"))
    more_yax[-1].values = vals[e[0]]
    more_uncs.append(Uncertainty("Total"))
    more_uncs[-1].values = uncs[e[0]]
    more_yax[-1].add_uncertainty(more_uncs[-1])
    for q in qualifiers:
      more_yax[-1].add_qualifier(*q)
    fig.add_variable(more_yax[-1])
  submission.add_table(fig)

def getDiffDistribution(root, pdf, location, title, theVars, theUncs, xtitle="", proc=None, obs=None, nbins=-1, limits=None, qualifiers= [("Process", "p p --> WZ --> l l l nu"), ("SQRT(S)", 13, "TeV")], units ="", xunits="", ttitle=""):
  print "Including figure %s..."%title
  #### Reading stuff ####
  inPDF = pdf
  nbins = nbins
  #### Create figure ####
  fig = Table(ttitle)
  fig.description = title
  fig.location    = "Data and expectations from %s"%location
  fig.keywords["observables"] = obs

  ## X axis
  xvar = Variable(xtitle, is_independent=True, is_binned=True, units=xunits)
  xvar.values = [[limits[i],limits[i+1]] for i in range(len(limits)-1)]
  print "...the binning is ", xvar.values
  fig.add_variable(xvar)
  theFile = ROOT.TFile(root,"READ")


  vals = {}
  uncs = {}
  for v in theVars:
    print root, v[1]
    th = theFile.Get(v[1])
    uh = [ theFile.Get(u[1]) for u in theUncs[v[0]] ] if len(theUncs[v[0]][0]) > 0 else []
    vvals = []
    uuncs = {u[0]:[] for u in theUncs[v[0]]} if len(uh) > 0 else {}
    isTH1 = type(th) == type(ROOT.TH1D())
    nbins = th.GetNbinsX() if isTH1 else th.GetN()-1
    for i in range(1, nbins+1):
      if isTH1:
        vvals.append(th.GetBinContent(i))
      else:
        x, y = ROOT.Double(), ROOT.Double()
        th.GetPoint(i, x, y)
        vvals.append(y)
      for j, u in enumerate(theUncs[v[0]]):
        if u == []: continue
        try:
          uuncs[u[0]].append(uh[j].GetBinError(i))
        except:
          uuncs[u[0]].append([uh[j].GetErrorYlow(i), uh[j].GetErrorYhigh(i)])
    vals[v[0]] = vvals
    uncs[v[0]] = uuncs

  # Y axis extras
  more_yax = []
  more_uncs = []
  for e in theVars:
    more_yax.append(Variable(e[0], is_independent=False, is_binned=False, units=units))
    more_yax[-1].values = vals[e[0]]
    for u in uncs[e[0]]:
      more_uncs.append(Uncertainty(u,is_symmetric=type(uncs[e[0]][u][0])!=type([1,2])))
      more_uncs[-1].values = uncs[e[0]][u]
      more_yax[-1].add_uncertainty(more_uncs[-1])
    for q in qualifiers:
      more_yax[-1].add_qualifier(*q)
    fig.add_variable(more_yax[-1])

  fig.add_image(inPDF)
  submission.add_table(fig)


class getTEX(object):
  def __init__(self,texfile,replacements=[]):
    print "Reading file %s..."%texfile
    self.texfile = texfile
    self.readfile()

  def readfile(self):
    theTexFile = open(self.texfile, "r")
    self.tables = []
    reading = False
    temp = []
    for line in theTexFile.readlines():
      for r in replacements: line = line.replace(r[0], r[1])
      if "begin{table}" in line:
        reading = True
      elif reading:
        if "caption" in line: continue
        if "end{table}" in line:
          reading=False
          self.tables.append(temp)
          temp = []
        elif ("end" in line or "begin" in line or "cmsTable" in line): continue
        else:
          temp.append(line.replace("\n",""))
    self.convertTables()

  def printTables(self, toPrint=None):
    for it, tab in enumerate(self.cleantables):
      if toPrint and not(it == toPrint): continue
      print "."
      print "."
      print "========>Table %i"%it
      for l in tab: print l


  def convertTables(self):
    self.cleantables = []
    for t in self.tables:
      entriesperline = []
      for l in t:
        entriesperline.append(len(l.split("&")))
      cleantable = []
      for i in range(len(t)):
        if entriesperline[i] == max(entriesperline):
          cleantable.append(t[i].split("&"))
      self.cleantables.append(cleantable)

  def parseXSecTable(self, iTable, utypes):
     print "Parsing as cross-section the following table..."
     self.printTables(iTable)
     print
     print
     toParse = self.cleantables[iTable]
     vals = {}
     uncs = {}
     keys = []
     #In cross sections, first column is channel, second is measurement
     for lines in toParse:
       key = lines[0].replace("  "," ")
       for i in range(100):
         if key[-1] == " " and len(key) > 1: key = key[:-1]
       words = lines[1].replace("\\\\","").replace("\\hline","").replace("\\\textrm{ }","\\pm").split("\\pm")
       val   = words[0].replace(" ","")
       unc   = words[1:]
       #print key, val, uncs
       # If we fail to convert we are at a header
       try: val = float(val)
       except: continue
       keys.append(key)
       vals[key] = val
       uncs[key] = {}
       for u in unc:
         for t in utypes.keys():
           if t in u:
             test = u.replace(" ","").replace(t,"")
             try:
               test = float(test)
               uncs[key][utypes[t]] = test
             except:
               udouble = test.replace("{","").replace("}","").replace("^","").split("_")
               uncs[key][utypes[t]] = [float(d) for d in udouble]

     return keys, vals, uncs

  def submitXSecTable(self, iTable, utypes, location="Test", title="", obs = [], xlabel="", ylabel="", units="", xvars = [], yvars = [], ytitles = [], qualifiers = [], pdf = None, ttitle=""):
    keys, vals, uncs = self.parseXSecTable(iTable, utypes)
    keystoint = {k:i for i,k in enumerate(keys)}
    tab = Table(ttitle)
    tab.description = title
    tab.location = location
    tab.keywords["observables"] = obs

    # Category ~ X axis
    cats = Variable(xlabel, is_independent=True, is_binned=False, units="")
    cats.values = xvars

    tab.add_variable(cats)

    # Results ~ Y axis
    allerrors = {}
    ik = 0
    for k in keys:
      for er in uncs[k].keys():
        if not er in allerrors.keys():
          if type(uncs[k][er]) == type([1,2]):
            allerrors[er] = ik*[[0,0]]+[uncs[k][er]]
          else:
            allerrors[er] = ik*[0]+[uncs[k][er]]
        else:
          allerrors[er].append(uncs[k][er])
      for ae in allerrors.keys():
        if len(allerrors[ae]) < ik+1 :
          allerrors[ae].append([0,0] if (type(allerrors[ae][-1]) == type([1,2])) else 0)
      ik += 1

    for ix, xv in enumerate(yvars.keys()):
      measurements = Variable(ytitles[xv], is_independent=False, is_binned=False, units=units)
      measurements.values = [vals[k] for k in yvars[xv]]
      for er in allerrors.keys():
        if type(allerrors[er][-1]) == type([1,2]):
          unc = Uncertainty(er, is_symmetric = False)
          tosave = [allerrors[er][keystoint[k]] for k in yvars[xv]]
          if max([tosave[tt][0] for tt in range(len(tosave))]) < 0.0001: continue
          unc.values = tosave
        else:
          unc = Uncertainty(er)
          unc.values = [allerrors[er][keystoint[k]] for k in yvars[xv]]
        measurements.add_uncertainty(unc)
      for q in qualifiers:
        measurements.add_qualifier(*q)

      tab.add_variable(measurements)
    if pdf:  tab.add_image(pdf)
    submission.add_table(tab)


  def parseMultyEntryTable(self, iTable, utypes, flipit=False):
     print "Parsing as multi-entry the following table..."
     self.printTables(iTable)
     print
     print
     toParse = self.cleantables[iTable]
     if flipit:
       tempParse = [[0. for k in range(len(toParse))] for j in range(len(toParse[0]))]
       for i in range(len(tempParse)):
         for j in range(len(tempParse[0])):
           tempParse[i][j] = toParse[j][i]
       toParse = tempParse

     vals = {}
     uncs = {}
     quants = []
     #In multienties, first column is channel, second and onwards is measurement
     for lines in toParse:
       key = lines[0].replace("  "," ").replace("\\\\","").replace("\\hline","")
       for i in range(100):
         if key[-1] == " " and len(key) > 1: key = key[:-1]
       vals[key] = []
       uncs[key] = []
       for i in range(1, len(lines)):
         words = lines[i].replace("\\\\","").replace("\\hline","").replace("\\\textrm{ }","\\pm").split("\\pm")
         val   = words[0].replace(" ","")
         try:
           try: # Just a single value
             val = float(val)
           except: # A range
             val = [float(v) for v in val.replace("[","").replace("]","").replace(" ","").split(",")]
         except: # If we are here maybe the uncertainties are asymmetric?
           try:
             words = val.replace("_","").replace("^","").replace("}","").split("{")
             val = float(words[0])
           except: #Ok, then I don't know what it is
             continue
         if type(val) ==  type([1,2]) or len(words) < 2:
           pass
         else:
           if len(words) < 3:
             uncs[key].append(float(words[1]))
           else:
             uncs[key].append([float(words[1]), float(words[2])])
         vals[key].append(val)
       if len(vals[key]) > 0: quants.append(key)
     print quants, vals, uncs
     return quants, vals, uncs

  def submitMultyEntryTable(self, iTable, utypes, flipit=False,  location="Test", title="", obs = [], xlabel="", ylabel="", units="", xvars = [], ytitles = [], qualifiers = [], pdf = None, unctitles = None, ttitle=""):
    quants, vals, uncs = self.parseMultyEntryTable(iTable, utypes, flipit)
    tab = Table(ttitle)
    tab.description = title
    tab.location = location
    tab.keywords["observables"] = obs

    # Category ~ X axis
    cats = Variable(xlabel, is_independent=True, is_binned=False, units="")
    cats.values = xvars
    tab.add_variable(cats)

    for meas in quants:
      print "These", meas, ytitles.keys()
      if not(meas in ytitles.keys()): continue
      isInterval = type(vals[meas][0]) == type([1,2])
      measurements = Variable(ytitles[meas], is_independent=False, is_binned=False, units=units)
      measurements.values = ["("+",".join([str(kk) for kk in k])+")" for k in vals[meas]] if isInterval else vals[meas]
      if len(uncs[meas]) == len(vals[meas]):
        unc = Uncertainty("Total" if not unctitles else unctitles[meas], is_symmetric = (type(uncs[meas][0]) != type([1,2])))
        unc.values = uncs[meas]
        measurements.add_uncertainty(unc)
      for q in qualifiers:
        measurements.add_qualifier(*q)
      tab.add_variable(measurements)
    if pdf:  tab.add_image(pdf)
    submission.add_table(tab)


replacements = [["\\eee","eee"],
                ["\\eem","eem"],
                ["\\mme","mme"],
                ["\\mmm","mmm"],
                ["\\POWHEG", "POWHEG"],
                ["\\MATRIX", "MATRIX"],
                ["$", ""],
                ["~", ""],
                ["\\\textrm{ fb}",""],
                ["\\\textrm{ pb}",""],
                ["[\\cmsTabSkip]",""],
                ["^+",""],
                ["(+) ",""],
                ["^-",""],
                [" (--)",""],
]

unctypes  = { "(\\stat)": "stat",
              "(\\syst)": "syst",
              "(\\lum)" : "lumi",
              "(\\\thy)" : "theo",
              "(\\\textrm{PDF})": "PDF",
              "(\\\textrm{scale})": "scale",
              "(\\\text{PDF+scale})":"PDF+scale",
              "(\\\text{scale})":"scale",
}
#tex = getTEX("/nfs/fanae/user/carlosec/WZ/AN_Legacy/SMP-20-014/SMP-20-014.tex", replacements=replacements)




getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/2lss_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/2lss_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_007.pdf",
  location = "Figure 7",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 2lSS category",
  obs      = "SR",
  nbins    = 20,
  ttitle   = "Category 2lss, signal regions",
  alt_data = "SR2lss_data",
  alt_background = "SR2lss_background",
  prefix   = "SR2lss_"
)


getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/SR3lA_RunII.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/SR3lA_RunII.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_008.pdf",
  location = "Figure 8",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 3lA category",
  obs      = "SR",
  nbins    = 64,
  ttitle   = "Category 3lA, signal regions",
  alt_data = "data",
  alt_background = "total_background",
  prefix   = "",
  extras   = [["WZ","WZ"],
                 ["ZZ","ZZH"],
                 ["ttX+tZq","TTX"],
                 ["VVV","Multiboson"],
                 ["Nonprompt","Nonprompt"],
                 ["Conversions", "Xgamma"]]
)


getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lB_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lB_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_009.pdf",
  location = "Figure 9",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 3lB category",
  obs      = "SR",
  nbins    = 3,
  ttitle   = "Category 3lB, signal regions",
  alt_data = "SR_3lB_data",
  alt_background = "SR_3lB_background",
  prefix   = "SR_3lB_"
)



getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lC_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lC_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_010.pdf",
  location = "Figure 10",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 3lC category",
  obs      = "SR",
  nbins    = 9,
  ttitle   = "Category 3lC, signal regions",
  alt_data = "SR_3lC_data",
  alt_background = "SR_3lC_background",
  prefix   = "SR_3lC_"
)



getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lD_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lD_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_011.pdf",
  location = "Figure 11",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 3lD category",
  obs      = "SR",
  nbins    = 16,
  ttitle   = "Category 3lD, signal regions",
  alt_data = "SR_3lD_data",
  alt_background = "SR_3lD_background",
  prefix   = "SR_3lD_"
)



getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lE_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lE_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_012-a.pdf",
  location = "Figure 12, top",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 3lE category",
  obs      = "SR",
  nbins    = 9,
  ttitle   = "Category 3lE, signal regions",
  alt_data = "SR_3lE_data",
  alt_background = "SR_3lE_background",
  prefix   = "SR_3lE_"
)



getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lF_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/3lF_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_012-b.pdf",
  location = "Figure 12, bottom",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 3lF category",
  obs      = "SR",
  nbins    = 12,
  ttitle   = "Category 3lF, signal regions",
  alt_data = "SR_3lF_data",
  alt_background = "SR_3lF_background",
  prefix   = "SR_3lF_"
)


getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lG_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lG_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_013.pdf",
  location = "Figure 13",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 4lG category",
  obs      = "SR",
  nbins    = 5,
  ttitle   = "Category 4lG, signal regions",
  alt_data = "SR4lG_data",
  alt_background = "SR4lG_background",
  prefix   = "SR4lG_"
)


getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lH_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lH_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_014-a.pdf",
  location = "Figure 14, top left",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 4lH category",
  obs      = "SR",
  nbins    = 3,
  ttitle   = "Category 4lH, signal regions",
  alt_data = "SR4lH_data",
  alt_background = "SR4lH_background",
  prefix   = "SR4lH_"
)



getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lI_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lI_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_014-b.pdf",
  location = "Figure 14, top right",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 4lI category",
  obs      = "SR",
  nbins    = 3,
  ttitle   = "Category 4lI, signal regions",
  alt_data = "SR4lI_data",
  alt_background = "SR4lI_background",
  prefix   = "SR4lI_"
)


getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lJ_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lJ_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_014-c.pdf",
  location = "Figure 14, bottom left",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 4lH category",
  obs      = "SR",
  nbins    = 3,
  ttitle   = "Category 4lJ, signal regions",
  alt_data = "SR4lJ_data",
  alt_background = "SR4lJ_background",
  prefix   = "SR4lJ_"
)



getSRFigureFromROOT(
  preroot  = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lK_Legacy.root",
  postroot = "/nfs/fanae/user/carlosec/WZ/CMSSW_8_0_19/src/CMGTools/TTHAnalysis/python/plotter/4lK_Legacy.root",
  pdf      = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_014-d.pdf",
  location = "Figure 14, bottom right",
  title    = "Prefit distribution of observed and expected yields for signal regions in the 4lK category",
  obs      = "SR",
  nbins    = 3,
  ttitle   = "Category 4lK, signal regions",
  alt_data = "SR4lK_data",
  alt_background = "SR4lK_background",
  prefix   = "SR4lK_"
)


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiWH_mergedRegions_combined/TChiWH_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_020.pdf",
 location = "Figure 20",
 title = "Upper limits at the 95 \% CL for the TChiWH model, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in TChiWH")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiWZSR_mergedRegions_combined/TChiWZSR_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_019.pdf",
 location = "Figure 19 (SR approach)",
 title = "Upper limits at the 95 \% CL for the TChiWZ model (SR), normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in TChiWZ (SR)")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiWZNN_mergedRegions_combined/TChiWZNN_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_019.pdf",
 location = "Figure 19 (NN approach)",
 title = "Upper limits at the 95 \% CL for the TChiWZ model (NN), normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in TChiWZ (NN)")

get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiStaux0p05_mergedRegions_combined/TChiStaux0p05_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_018-a.pdf",
 location = "Figure 18 (left)",
 title = "Upper limits at the 95 \% CL for the tau-dominated TChiSlepSneu model, x=0.05, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in tau-dominated TChiSlepSneu, x=0.05")

get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiStaux0p5_mergedRegions_combined/TChiStaux0p5_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_018-b.pdf",
 location = "Figure 18 (right)",
 title = "Upper limits at the 95 \% CL for the tau-dominated TChiSlepSneu model, x=0.5, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in tau-dominated TChiSlepSneu, x=0.5")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiStaux0p95_mergedRegions_combined/TChiStaux0p95_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_018-c.pdf",
 location = "Figure 18 (bottom)",
 title = "Upper limits at the 95 \% CL for the tau-dominated TChiSlepSneu model, x=0.95, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in tau-dominated TChiSlepSneu, x=0.95")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiTESlepx0p05_mergedRegions_combined/TChiTESlepx0p05_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_017-a.pdf",
 location = "Figure 17 (left)",
 title = "Upper limits at the 95 \% CL for the tau-enhanced TChiSlepSneu model, x=0.05, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in tau-enhanced TChiSlepSneu, x=0.05")

get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiTESlepx0p5_mergedRegions_combined/TChiTESlepx0p5_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_017-b.pdf",
 location = "Figure 17 (right)",
 title = "Upper limits at the 95 \% CL for the tau-enhanced TChiSlepSneu model, x=0.5, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in tau-enhanced TChiSlepSneu, x=0.5")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiTESlepx0p95_mergedRegions_combined/TChiTESlepx0p95_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_017-c.pdf",
 location = "Figure 17 (bottom)",
 title = "Upper limits at the 95 \% CL for the tau-enhanced TChiSlepSneu model, x=0.95, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in tau-enhanced TChiSlepSneu, x=0.95")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiSlepx0p05SR_mergedRegions_combined/TChiSlepx0p05SR_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_016-a.pdf",
 location = "Figure 16 (left)",
 title = "Upper limits at the 95 \% CL for the flavour-democratic TChiSlepSneu model, x=0.05 (SR), normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in flavour-democratic TChiSlepSneu, x=0.05 (SR)")

get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiSlepx0p5SR_mergedRegions_combined/TChiSlepx0p5SR_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_016-b.pdf",
 location = "Figure 16 (right)",
 title = "Upper limits at the 95 \% CL for the flavour-democratic TChiSlepSneu model, x=0.5, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in flavour-democratic TChiSlepSneu, x=0.5 (SR)")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiSlepx0p95SR_mergedRegions_combined/TChiSlepx0p95SR_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_016-c.pdf",
 location = "Figure 16 (bottom)",
 title = "Upper limits at the 95 \% CL for the flavour-democratic TChiSlepSneu model, x=0.95 (SR), normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in flavour-democratic TChiSlepSneu, x=0.95 (SR)")

get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiSlepx0p05NN_mergedRegions_combined/TChiSlepx0p05NN_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_016-a.pdf",
 location = "Figure 16 (left)",
 title = "Upper limits at the 95 \% CL for the flavour-democratic TChiSlepSneu model, x=0.05 (NN), normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in flavour-democratic TChiSlepSneu, x=0.05 (NN)")

get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiSlepx0p5NN_mergedRegions_combined/TChiSlepx0p5NN_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_016-b.pdf",
 location = "Figure 16 (right)",
 title = "Upper limits at the 95 \% CL for the flavour-democratic TChiSlepSneu model, x=0.5, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in flavour-democratic TChiSlepSneu, x=0.5 (NN)")


get2DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiSlepx0p95NN_mergedRegions_combined/TChiSlepx0p95NN_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_016-c.pdf",
 location = "Figure 16 (bottom)",
 title = "Upper limits at the 95 \% CL for the flavour-democratic TChiSlepSneu model, x=0.95 (NN), normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_2^{0}} = m_{\\tilde{\chi}_1^{\pm}} $",
 ylabel = "$m_{\\tilde{\chi}_1^{0}}$",
 zlabel = " Upper limit",
 unitsx = "GeV",
 unitsy = "GeV",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in flavour-democratic TChiSlepSneu, x=0.95 (NN)")


get1DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiZZ_mergedRegions_combined/TChiZZ_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_021-a.pdf",
 location = "Figure 21 (top)",
 title = "Upper limits at the 95 \% CL for the TChiZZ model, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_1^{0}}$",
 ylabel = "",
 zlabel = "Upper limit",
 unitsx = "GeV",
 unitsy = "",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in TChiZZ ")

get1DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiHZ_mergedRegions_combined/TChiHZ_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_021-b.pdf",
 location = "Figure 21 (middle)",
 title = "Upper limits at the 95 \% CL for the TChiHZ model, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_1^{0}}$",
 ylabel = "",
 zlabel = "Upper limit",
 unitsx = "GeV",
 unitsy = "",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in TChiHZ ")


get1DScanFromText("/pool/phedex/userstorage/carlosec/combine/CMSSW_10_2_13/src/lims_Approval/lims_TChiHH_mergedRegions_combined/TChiHH_mergedRegions_UL_SR",
 pdf = "/nfs/fanae/user/carlosec/WZ/HepDataSUSY/Figure_021-c.pdf",
 location = "Figure 21 (bottom)",
 title = "Upper limits at the 95 \% CL for the TChiHH model, normalized to expected cross section",
 xlabel = "$m_{\\tilde{\chi}_1^{0}}$",
 ylabel = "",
 zlabel = "Upper limit",
 unitsx = "GeV",
 unitsy = "",
 unitsz = "",
 obs    = ["UL"],
 ttitle = "Upper limits in TChiHH ")


# This always at the end
for table in submission.tables:
    table.keywords["cmenergies"] = [13000]
print "Prepare submission and tar files"
outdir = "example_output"
submission.create_files(outdir)
