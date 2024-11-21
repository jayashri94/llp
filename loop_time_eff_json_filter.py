#!/usr/bin/env python
# coding: utf-8

import uproot
import awkward as ak
import numpy as np
import time
import glob


#-------------------------------------------------------------------------------
# Definition of jetTime_hard function
#-------------------------------------------------------------------------------
def jetTime_hard(entry):
    #-------------------------------------------------
    # Retrieve variables and get MET
    #-------------------------------------------------
    # Single number with type uint32
    evtpass    = entry['pass']
    if (evtpass): 

	    evt        = entry['event']
	    run        = entry['run']
	    ls         = entry['ls']
	    
	    # These have same lengths ~ 100
	    jetEta     = ak . to_numpy(entry['JetEta'])
	    jetPhi     = ak . to_numpy(entry['JetPhi'])
	    jetPt      = ak . to_numpy(entry['JetPt'])
	    jetHadFrac = ak . to_numpy(entry['JetHadFrac'])
	
	    # These have same lengths ~ 7,000
	    digiEta    = ak . to_numpy(entry['HBHERecHitEta'])
	    digiPhi    = ak . to_numpy(entry['HBHERecHitPhi'])
	    digiTime   = ak . to_numpy(entry['HBHERecHitTime'])
	    digiEnergy = ak . to_numpy(entry['HBHERecHitEnergy'])
	    NominalMET = ak . to_numpy(entry['NominalMET'])
	
	    # MET
	    met = np . hypot(NominalMET[0], NominalMET[1])
	
	    #-------------------------------------------------
	    # Prepare containers
	    #-------------------------------------------------
	    jTime_hard = []
	    Pt_hard    = []
	    evt_met    = []
	    evt_id     = []
	    HF_hard    = []
	    evt_run    = []
	    evt_ls     = []

	    dgTime     = []

	    #-------------------------------------------------
	    # Apply selection
	    #-------------------------------------------------
	    # Jet selection: length reduces to ~ 5
	    #jetSel = (abs(jetEta) < 2.5) & (jetPt > 30)
	    jetSel = (abs(jetEta) < 1.5) & (jetPt > 30)  # Selecting only barrel jets
	    jEta = jetEta[jetSel]
	    jPhi = jetPhi[jetSel]
	    jPt  = jetPt[jetSel]
	    jHad = jetHadFrac[jetSel]
	    if len(jEta) == 0:
	        print("Warning: No jet survived from selection")
	        return jTime_hard, Pt_hard, HF_hard, evt_met, evt_id, evt_run, evt_ls, dgTime 
	
	    # Time & energy selection: length reduces to ~ 20
	    timeSel   = (digiTime > -1) & (digiTime <= 25) # valid cc time from ntuple
	    energySel = digiEnergy > 10        
	    dEta    = digiEta[timeSel & energySel]
	    dPhi    = digiPhi[timeSel & energySel]
	    dTime   = digiTime[timeSel & energySel]
	    dEnergy = digiEnergy[timeSel & energySel]
	    if len(dEta) == 0:
	        print("Warning: No digi survived from selection")
	        return jTime_hard, Pt_hard, HF_hard, evt_met, evt_id, evt_run, evt_ls, dgTime 
	
	
	    #-------------------------------------------------
	    # Loop over the jets Or Use `np.argmax(jPt)`to find the leading jet
	    #-------------------------------------------------
	    for iJet in range (len(jPt)):
	
		    #-------------------------------------------------
		    # Find Digi selection
		    #-------------------------------------------------
		    delPhi = ((jPhi[iJet] - dPhi) + np.pi ) % (2. * np.pi) - np.pi; # Angle wrapping between (-pi and pi)
		    dR = np . sqrt((jEta[iJet]-dEta)**2 + (delPhi)**2)
		    DigiSel = dR < 0.5
		
		    #-------------------------------------------------
		    # Calculate average and fill containers
		    #-------------------------------------------------
		    #if np . sum(DigiSel) > 7:
		    if (np . sum(DigiSel) <= 7) and (np . sum(DigiSel) > 2):
		        jTime_hard . append(np . average(dTime[DigiSel], weights=dEnergy[DigiSel]))
		        Pt_hard    . append(jPt[iJet])
		        HF_hard    . append(jHad[iJet])
		        evt_met    . append(met)
		        evt_id     . append(evt)
		        evt_run    . append(run)
		        evt_ls     . append(ls)
	
		        dgTime     . append(dTime[DigiSel])
	    return jTime_hard, Pt_hard, HF_hard, evt_met, evt_id, evt_run, evt_ls, dgTime
    
    else:
        return 0

#-------------------------------------------------------------------------------
# List of files to be processed
#-------------------------------------------------------------------------------
#files = glob.glob('/mnt/data2/users/jayashri/kisti_gen_files/run2022c/*.root')
#files = glob.glob('/mnt/data2/users/jayashri/kisti_gen_files/run2022c/goldenJson/*.root')
files = glob.glob('/mnt/data2/users/jayashri/kisti_gen_files/run2022c/evtfilter/*.root')


#-------------------------------------------------------------------------------
# Result containers
#-------------------------------------------------------------------------------
jTime_hard_qcd = []
JetPt_hard_qcd = []
HF_hard_qcd    = []
evt_met_qcd    = []
evt_id_qcd     = []
run_qcd        = []
ls_qcd         = []

dgTime_qcd     = []
#-------------------------------------------------------------------------------
# Loop over files
#-------------------------------------------------------------------------------
for i in range(len(files)):
    #-------------------------------------------------
    # Measure the time of loop start
    #-------------------------------------------------
    t_loop_start = time . time()

    #-------------------------------------------------
    # Open file
    #-------------------------------------------------
    data = uproot.open(files[i])
    print(files[i], "is going to be processed")

    #-------------------------------------------------
    # Get tree
    #-------------------------------------------------
    caloTree = data['hcalTupleTree/tree']
    branches = caloTree . arrays(['pass','event','run','ls', 'JetEta', 'JetPhi', 'JetPt','JetHadFrac', 'HBHERecHitEta', 'HBHERecHitPhi', 'HBHERecHitTime','HBHERecHitEnergy', 'NominalMET'])

    #-------------------------------------------------
    # Loop over entries
    #-------------------------------------------------
    for entry in branches:
        jetTime_hard_res = jetTime_hard(entry)

        if np.any(jetTime_hard_res != 0):
	        jTime_hard_qcd . extend(jetTime_hard_res[0])
	        JetPt_hard_qcd . extend(jetTime_hard_res[1])
	        HF_hard_qcd    . extend(jetTime_hard_res[2])
	        evt_met_qcd    . extend(jetTime_hard_res[3])
	        evt_id_qcd     . extend(jetTime_hard_res[4])
	        run_qcd        . extend(jetTime_hard_res[5])
	        ls_qcd         . extend(jetTime_hard_res[6])
	
	        dgTime_qcd     . extend(jetTime_hard_res[7]) 
    print(i, "-th loop took", time . time() - t_loop_start, "seconds, having", caloTree . num_entries, "entries")


#-------------------------------------------------------------------------------
# Save
#-------------------------------------------------------------------------------
nRecHit = 7
eRecHit = 10

np . save('npy_files/jTime_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'  . format(nRecHit, eRecHit), jTime_hard_qcd)
np . save('npy_files/JetPt_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'  . format(nRecHit, eRecHit), JetPt_hard_qcd)
np . save('npy_files/HF_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'     . format(nRecHit, eRecHit), HF_hard_qcd   )
np . save('npy_files/evt_met_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'. format(nRecHit, eRecHit), evt_met_qcd   )
np . save('npy_files/evt_id_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets' . format(nRecHit, eRecHit), evt_id_qcd    )

np . save('npy_files/run_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'    . format(nRecHit, eRecHit), np.array(run_qcd,dtype=object))
np . save('npy_files/ls_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'     . format(nRecHit, eRecHit), np.array(ls_qcd, dtype=object))

np . save('npy_files/dgTime_jets_validcc_nhit_above2to{}_ehit{}_data_run2022c_json_filter_barreljets'  . format(nRecHit, eRecHit), np.array(dgTime_qcd, dtype=object))
