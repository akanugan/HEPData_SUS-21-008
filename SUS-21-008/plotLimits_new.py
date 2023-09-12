# python produceResults/plotLimits.py --outdir /eos/user/p/pmeiring/www/EWK_SUSY_combination/tmp1/
import os
import re
import glob
import array
import argparse
import sys
from extraTools import *
from lumi_tmp import *

import ROOT
from ROOT import *

parser = argparse.ArgumentParser()
parser.add_argument("--outdir", default="../results/plots/", help="Choose the output directory. Default='%(default)s'")
parser.add_argument("--topology", default="all", choices=["WZ","WH","WHWZ_mix","ZZ", "ZH", "HH", "all", "MLchange_WH", "MLchange_WZ"], help="Choose topology. Default='%(default)s'")

parser.add_argument("--smooth", nargs=2, default = False, help="Apply smoothing X times with kernel Y (Y='k3a','k5a','k5b'). Multiple smoothings are not recommended. Not guaranteed to be compatible with a tag other than 'all'.")
args = parser.parse_args()

chi1pm = "#lower[-0.12]{#tilde{#chi}}#lower[0.2]{#scale[0.85]{^{#pm}}}#kern[-1.3]{#scale[0.85]{_{1}}}"
chi10  = "#lower[-0.12]{#tilde{#chi}}#lower[0.2]{#scale[0.85]{^{0}}}#kern[-1.3]{#scale[0.85]{_{1}}}"
chi20  = "#lower[-0.12]{#tilde{#chi}}#lower[0.2]{#scale[0.85]{^{0}}}#kern[-1]{#scale[0.85]{_{2}}}"


lMargin = 0.14
tMargin = 0.08
rMargin = 0.04
bMargin = 0.14

cmsH = 0.075;
TopMargin = 0.08
legLineH = 0.039;
legTextSize = 0.035;
legY = 1-TopMargin-cmsH-0.025;
legW = 0.14
legH = 0.07;

legX = 1-rMargin-0.045
baselegY = 1-tMargin-cmsH-0.02



maxx = 1200
maxy = 700

if args.topology == "MLchange_WH":
   maxx = 300
   maxy = 150

if args.topology == "MLchange_WZ":
   maxx = 600
   maxy = 400


class TGraphsWrapper():
    def __init__(self,listofTGraphs):
        self.listofTGraphs=listofTGraphs
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            for i in range(self.listofTGraphs.GetSize()):
                getattr(self.listofTGraphs[i],name)(*args, **kwargs)      
        return wrapper

def getLimitGraph(limit_hist):
    c_tmp = TCanvas()
    lim_tmp=limit_hist.Clone()
    lim_tmp.SetContour(1,array.array('d',[1]))
    lim_tmp.Draw("CONT LIST")
    gPad.Update()
    contObjArray = gROOT.GetListOfSpecials().FindObject("contours")
    listofTGraphs=contObjArray.At(0).Clone()
    return TGraphsWrapper(listofTGraphs)


class Analysis:
    def __init__(self, path, color, style, label):
        self.file = args.outdir+"/"+path
        if not os.path.isfile(self.file): raise RuntimeError("Invalid input path: %s"%self.file)
        self.color= color
        self.style = style
        self.label= label
        self.g_exp_0 = TH2D("exp0","exp0",maxx,0,maxx,maxy,0,maxy)
        self.g_obs_0 = TH2D("obs0","obs0",maxx,0,maxx,maxy,0,maxy)        

        self.getLimitGraphs(self.file) 
        #self.g_exp_p1= self.getLimitGraph("1")
        #self.g_exp_m1= self.getLimitGraph("-1")
        #self.g_obs_0 = self.getLimitGraph("self.file)
        
    
    # Function that returns a dict containing the limits (in TH2F format) of all points from a particular analyses 
    def getLimitGraphs(self, file):

        f = ROOT.TFile.Open(file, "READ")
        #g_exp = TH2D("temp","temp",maxx,0,maxx,maxy,0,maxy)
        #g_obs = TH2D("temp1","temp1",maxx,0,maxx,maxy,0,maxy)

        if f:
            g_exp = f.Get("lim_exp")
            g_obs = f.Get("lim_obs")

        self.g_exp_0 = g_exp.Clone("exp0")
        self.g_exp_0.SetDirectory(0)

        self.g_obs_0 = g_obs.Clone("obs0")
        self.g_obs_0.SetDirectory(0)

        f.Close()


class LimitPlot:
    def __init__(self,AN,outname="dummy"):
        self.AN     = AN
        self.legend = TLegend(0.16,0.58,0.65,0.8986)
        self.legendGeneral = TLegend(0.65,0.75,0.85,0.8986)
        if "MLchange" in args.topology:
            nGraph = 2
            self.legend = TLegend(lMargin+0.03, legY-0.08-(legLineH*nGraph), lMargin+0.03+0.4, legY-0.01-(legLineH*nGraph));
            self.legendGeneral = TLegend(lMargin+0.03, legY+0.1-(legLineH*nGraph*0.8), lMargin+0.03+0.4, legY+0.03-(legLineH*nGraph*0.8))


        self.labels = ["dummy", "dummy"]
        self.text   = []
        self.c      = TCanvas(outname,outname,700,700)
        self.out = outname
        self.drawLimits()

    def drawLimits(self):
        # Black magic to enforce correct axes ranges
        self.c.cd()
        self.c.SetLeftMargin(0.12)
        ROOT.gStyle.SetNumberContours(999)
        ROOT.gStyle.SetOptTitle(0)
        h_ghost = TH2D("dummy","dummy",maxx,0,maxx,maxy,0,maxy); h_ghost.SetStats(0)
        h_ghost.GetXaxis().SetRangeUser(100,maxx)
        h_ghost.GetXaxis().SetTitle("m_{%s} = m_{%s} [GeV]"%(chi20,chi1pm))
        h_ghost.GetYaxis().SetRangeUser(0,maxy)
        h_ghost.GetYaxis().SetTitle("m_{%s} [GeV]"%(chi10))
        h_ghost.GetZaxis().SetRangeUser(0,10)


        if args.topology == "MLchange_WH" or args.topology == "MLchange_WZ":
           h_ghost.GetYaxis().SetRangeUser(0,maxy)

        h_ghost.Draw("colz")


        # h_bkgd = self.AN[0].g_exp_0.Clone("h_bkgd")
        # h_bkgd.Draw("colz same")
        # h_bkgd.GetZaxis().SetRangeUser(0,10)

        hObs_Gen = TGraph2D()
        hExp_Gen = TGraph2D()

        hObs_Gen.SetLineColor(kBlack)
        hObs_Gen.SetLineWidth(3)
        hObs_Gen.SetLineStyle(1)
        hExp_Gen.SetLineColor(kBlack)
        hExp_Gen.SetLineWidth(3)
        hExp_Gen.SetLineStyle(2)


        # Draw the contours (where r=1)
        hlims=[]
        glims=[]

        for an in self.AN:

            hlim = an.g_exp_0.Clone()
            hlim_obs = an.g_obs_0.Clone()

            if "WH_WH" in an.file:
                hlim.GetXaxis().SetRangeUser(150, 950)
                hlim_obs.GetXaxis().SetRangeUser(150,950)  


            glim=getLimitGraph(hlim)
            glim.SetLineColor(an.color)
            glim.SetLineWidth(3)
            glim.SetLineStyle(2)

            hlim.SetContour(1,array.array('d',[1]))
            hlim.SetLineColor(an.color)
            hlim.SetLineWidth(3)
            hlim.SetLineStyle(2)

            glim_obs=getLimitGraph(hlim_obs)
            glim_obs.SetLineColor(an.color)
            glim_obs.SetLineWidth(3)
            glim_obs.SetLineStyle(1)

            hlim_obs.SetContour(1,array.array('d',[1]))
            hlim_obs.SetLineColor(an.color)
            hlim_obs.SetLineWidth(3)
            hlim_obs.SetLineStyle(1)

            #if args.smooth:
            #    print(int(args.smooth[0]), args.smooth[1])
            #    hlim.Smooth()
            #    hlim_obs.Smooth()
            #
            #	   self.centHist.Smooth(1,"k5a")
            #hlim.Smooth(1, "k3a")
            #hlim_obs.Smooth(1, "k3a")

            hlims.append(hlim)
            hlims.append(hlim_obs)
            glims.append(glim)
            glims.append(glim_obs)
            glim.Draw("SAME") #("CONT3 LIST same")
            glim_obs.Draw("SAME") #("CONT3 LIST same")

            # glims.append(hlim)
            # glims.append(hlim_obs)
            # glim.Draw("same")
            # glim_obs.Draw("same")


            #f2 = ROOT.TFile.Open("testing_comb_WZ.root", "RECREATE")
            #hlim.Write("h_exp")
            #hlim_obs.Write("h_obs")
            #f2.Close()

            self.legend.AddEntry(hlim_obs,an.label,"l")

        if args.topology == "WHWZ_mix":
           #self.legend.SetHeader("pp#rightarrow%s%s"%(chi1pm,chi20)")
           #self.legend.SetHeader("pp#rightarrow%s%s"%(chi1pm,chi20)"),B(#tilde{#chi}_{1}^{#pm} #rightarrow W#tilde{#chi}_{1}^{0})=1")
           self.legend.SetHeader("pp #rightarrow #tilde{#chi}_{1}^{#pm}#tilde{#chi}_{2}^{0}, B(#tilde{#chi}_{1}^{#pm} #rightarrow W#tilde{#chi}_{1}^{0})=1")
        elif args.topology == "WZ":
           self.legend.SetHeader("pp #rightarrow #tilde{#chi}_{1}^{#pm}#tilde{#chi}_{2}^{0} #rightarrow WZ#tilde{#chi}^{0}_{1}#tilde{#chi}^{0}_{1}")
        elif args.topology == "WH":
       	   self.legend.SetHeader("pp #rightarrow #tilde{#chi}_{1}^{#pm}#tilde{#chi}_{2}^{0} #rightarrow WH#tilde{#chi}^{0}_{1}#tilde{#chi}^{0}_{1}")


        self.legend.SetNColumns(1)
        #self.legend.SetFillStyle(0)
        #self.legend.SetLegendFillColor(0)
        self.legend.SetBorderSize(0)
        self.legend.SetTextSize(legTextSize*0.9);
        self.legend.Draw("same")

        self.legendGeneral.AddEntry(hExp_Gen, "Expected", "l")
        self.legendGeneral.AddEntry(hObs_Gen, "Observed", "l")
        #self.legendGeneral.SetFillStyle(0)
        #self.legendGeneral.SetLegendFillColor(0)
        self.legendGeneral.SetBorderSize(0)
        self.legendGeneral.SetTextSize(0.031)
        self.legendGeneral.Draw("same")

        CMS_lumi.lumi_13TeV = "137 fb^{-1}"
        CMS_lumi(self.c, 0, True, "   Preliminary  ",0.05)

        self.c.RedrawAxis()
        self.c.Update()
        self.c.Modified()
        self.c.SaveAs(args.outdir+"/%s.png"%(self.out))
        self.c.SaveAs(args.outdir+"/%s.pdf"%(self.out))

    def addText(text, font, style, size, color, position):
        return

if __name__ == '__main__':


    if args.topology == "WZ":
        SOS_WZ =   Analysis(color=kGreen+2, style=1, label="2/3l soft", path="SOS_WZ_contour.root")
        ML_WZ =    Analysis(color=kRed, style=1, label="#geq3l", path="MLNN_WZ_contour.root")
        zedge_WZ = Analysis(color=kBlue+2, style=1, label="2l on-Z", path="zedge_WZ_contour.root")
        WX_WZ =    Analysis(color=kOrange+2, style=1, label="Hadr. WX", path="WX_WZ_contour.root")
        Comb_WZ =  Analysis(color=kBlack, style=1, label="Combined",   path="comb_WZ_contour.root")

        LPlot = LimitPlot([SOS_WZ, ML_WZ, zedge_WZ, WX_WZ, Comb_WZ], outname = "Individual_WZ")

    elif args.topology == "WH":
        ML_WH =    Analysis(color=kRed, style=1, label="#geq3l", path="ML_WH_contour.root")
        WH_WH =    Analysis(color=kMagenta+2, style=1, label="1l 2b", path="WH_WH_contour.root")
        WX_WH =    Analysis(color=kOrange+2, style=1, label="Hadr. WX", path="WX_WH_contour.root")
        Comb_WH =  Analysis(color=kBlack, style=1, label="Combined",   path="comb_WH_contour.root")

        LPlot = LimitPlot([ML_WH, WH_WH, WX_WH, Comb_WH], outname = "Individual_WH")

    elif args.topology == "MLchange_WH":
        ML_WH =    Analysis(color=kOrange, style=1, label="ML (WH)", path="ML_WH_contour_25.root")
        ML_WH_new =    Analysis(color=kBlack, style=1, label="ML with leading leg pT>30 GeV (WH)", path="ML_WH_contour.root")

        LPlot = LimitPlot([ML_WH, ML_WH_new], outname = "Individual_WH_MLchange")

    elif args.topology == "MLchange_WZ":
        ML_WZ =    Analysis(color=kOrange, style=1, label="ML (WZ)", path="MLNN_WZ_contour_25.root")
        ML_WZ_new =    Analysis(color=kBlack, style=1, label="ML with leading leg pT>30 GeV (WZ)", path="MLNN_WZ_contour.root")

        LPlot = LimitPlot([ML_WZ, ML_WZ_new], outname = "Individual_WZ_MLchange")

    elif args.topology == "WZ_comb":
        Comb_WZ =  Analysis(color=kGreen+2, style=1, label="B(#tilde{#chi}_{2}^{0} #rightarrow Z#tilde{#chi}_{1}^{0})=1 (WZ)",   path="comb_WZ_contour.root")
        LPlot = LimitPlot([Comb_WZ], outname = "Individual_WZ_comb")

    elif args.topology == "WHWZ_mix":
        Comb_WZ       =  Analysis(color=kMagenta+2, style=1, label="B(#tilde{#chi}_{2}^{0} #rightarrow Z#tilde{#chi}_{1}^{0})=1 (comb.)",   path="comb_WZ_contour.root")
        Comb_WH       =  Analysis(color=kGreen+2, style=1, label="B(#tilde{#chi}_{2}^{0} #rightarrow H#tilde{#chi}_{1}^{0})=1 (comb.)",   path="comb_WH_contour.root")
        Comb_WHWZ5050 =  Analysis(color=kOrange+4, style=1, label="B(#tilde{#chi}_{2}^{0} #rightarrow Z#tilde{#chi}_{1}^{0})=B(#tilde{#chi}_{2}^{0} #rightarrow H#tilde{#chi}_{1}^{0})=0.5 (comb.)",   path="comb_WHWZ0p50_contour.root")

        LPlot = LimitPlot([Comb_WZ,Comb_WH,Comb_WHWZ5050], outname = "Mixed_WHWZ_5050")

    else:
        SOS_WZ =   Analysis(color=kBlack, style=1, label="2/3l soft (WZ)", path="SOS_WZ_contour.root")
        ML_WZ =    Analysis(color=kRed, style=1, label="3l (WZ)", path="ML_WZ_contour.root")
        zedge_WZ = Analysis(color=kBlue+2, style=1, label="2l on-Z (WZ)", path="zedge_WZ_contour.root")
        WX_WZ =    Analysis(color=kOrange+2, style=1, label="Hadr. WX (WZ)", path="WX_WZ_contour.root")
        Comb_WZ =  Analysis(color=kRed, style=1, label="B(#tilde{#chi}_{2}^{0} #rightarrow Z#tilde{#chi}_{1}^{0})=1 (WZ)",   path="comb_WZ_contour.root")

       	LPlot = LimitPlot([SOS_WZ, ML_WZ, zedge_WZ, WX_WZ, Comb_WZ], outname = "Individual_WZ")

        ML_WH =    Analysis(color=kMagenta+2, style=1, label=">3l (WH)", path="ML_WH_contour.root")
        WH_WH =    Analysis(color=kGreen+2, style=1, label="1l 2b (WH)", path="WH_WH_contour.root")
        WX_WH =    Analysis(color=kOrange+4, style=1, label="Hadr. WX (WH)", path="WX_WH_contour.root")
        Comb_WH =  Analysis(color=kGreen+2, style=1, label="B(#tilde{#chi}_{2}^{0} #rightarrow H#tilde{#chi}_{1}^{0})=1 (WH)",   path="comb_WH_contour.root")

        LPlot = LimitPlot([ML_WH, WH_WH, WX_WH, Comb_WH], outname = "Individual_WH")

        LPlot = LimitPlot([Comb_WZ, Comb_WH], outname = "Comb_WZ_WH")

   # LPlot = LimitPlot([SOS_WZ_obs], outname = "TChiWZ")

