import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import itertools as itl

dataroot = uproot.open('/data3/jayashri/root_files/pythia_generated/tree_rootfiles/tree_llp_2400_tau4.0.root'). # file location
dataroot.keys()

data_tree = dataroot['tree']

alldata = data_tree.arrays()

status,pdg_id,evt,mom1,dvtx_x,dvtx_y = data_tree.arrays(['status','id','evt','mom1','dvtx_x','dvtx_y'],outputtype=tuple)
dvtx = data_tree.arrays(['dvtx_x','dvtx_y','dvtx_z'], outputtype=tuple)

r = np.hypot(dvtx[0], dvtx[1])

#selections
id_sel1 = abs(pdg_id) >= 1000021
id_sel2 = abs(pdg_id) != 1000039    # to include r hadrons in moms list whose pdg id are above 1000021 and to exclude gravitinos as they are never mothers for the gluino.

idsel = id_sel1 & id_sel2
#allmom = mom1[idsel]  #all the moms of gluinos under our consideration
status_sel1 = abs(status) == 106
status_sel2 = abs(status) == 22

r_106 = r[idsel & status_sel1]
r_22  = r[idsel & status_sel2]

#mom_per_evt = []*1000
#mom_order = []

#for i in range (0,1000):
  #evt_sel = evt ==i
  #mom_per_evt.append(i)
  #mom_per_evt[i] = mom1[idsel & evt_sel]
  #num = len(mom_per_evt[i].flatten())
  #n = (num * 0.5) + 2   # random assumption that atleast two more than half of the  moms among 'num' may corresponds to one of two gluinos of status 106.
  #arr =  []
  #for  j in  range (0,int(n)):
    #arr.append(j)
    #if j ==  0:
      #arr[j] = mom1[idsel & evt_sel & status_sel1]
    #else:
      #k = j-1
      #arr[j] = mom1[arr[k]]        # This array contains all the moms order wise in an event
  #print (arr)
  #arr_order = list(itl.chain(*arr))
  #s = list(itl.chain(*arr_order))
  #gluino1 = []
  #gluino2 = []
  #for l in range  (0,int(n)):
     #gluino1.append(l)
     #gluino2.append(l)
     #even  = 2 * l
     #odd = (2 * l) + 1
     #gluino1[l]= s[even]
#gluino2[l]= s[odd]
  #ith_row = []
  #for cols in range (2):
     #ith_row.append(cols)
     #if cols == 0:
       #ith_row[cols] = gluino1 # separaring moms of gluino1 into this array
     #else:
       #ith_row[cols] = gluino2
  #mom_order.append(i)
  #mom_order[i] = ith_row   # this is a list containing 2d arrays. Each array has the list of moms of gluinos, generation wise pertaining to one of the two gluino_status106. 


#save = np.save('momlists_gluino2400_tau4p0.npy', mom_order)
load = np.load('momlists_gluino2400_tau4p0.npy', allow_pickle= True) # since 'for' loop takes longer to run in python once the gnerated array is saved for later use and the correspond lines are commented out.


# rearranging the entries in r_22 array if their order is reversed, which can be examined after the end of the loop below.

r_22new = []
for i in range (0,1000):
   ith_row =[]
   for j in range (0,2):
      ith_row.append(j)
      list_1 = list(itl.chain(*load[i,[j]]))
      #list_2 = list(itl.chain(*list_1))
      if j ==0:
         if 5 in list_1:
            ith_row[j] = r_22[i,[0]]  # always in an event momnumber '5' corresponds to 1st gluino of status22 and 6 to the next gluino_22. [Realised by examinig the root file for various events]
          elif 6 in list_1:           # Thus if the mom_list 1 contains 6 or if mom list 2 contains 5 then we can say that the order is reversed in this event.
            ith_row[j] = r_22[i,[1]]
      else:
         if 6 in list_1:
            ith_row[j] = r_22[i,[1]]
         elif 5 in list_1:
            ith_row[j] = r_22[i,[0]]
   r_22new.append(i)
   r_22new[i] = ith_row

r_22dist = list(itl.chain(*r_22new))
r_106dist = r_106.flatten()

#plotting 2d histogram for decay vertex distribuiton
xbin = np.linspace (0, 10000, num=21)
ybin = np.linspace (0, 10000, num=21)
plt.hist2d(r_106dist, r_22dist,bins= [xbin,ybin], norm= mpl.colors.LogNorm())
cbar = plt.colorbar()

plt.xlim([0,10000])
plt.ylim([0,10000])
plt.title("Decay_vertex_dist_2400_tau4.0_Gluino")

plt.xlabel('Decay vertex for gluino_106 (mm)', fontsize = 12)
plt.ylabel('Decay vertex for gluino_22 (mm)',fontsize = 12)
cbar.ax.set_ylabel('Number of events')
plt.savefig('hist2d_r106_22__dist_gluino_mom_traced_new.png', dpi = 300)
