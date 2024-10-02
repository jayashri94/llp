#------------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------------
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
import FWCore.ParameterSet.VarParsing as VarParsing
import FWCore.PythonUtilities.LumiList as LumiList

from RecoMET.METFilters.metFilters_cff import globalSuperTightHalo2016Filter,EcalDeadCellTriggerPrimitiveFilter,BadPFMuonFilter,BadPFMuonDzFilter,hfNoisyHitsFilter,eeBadScFilter,goodVertices #--
#------------------------------------------------------------------------------------
# Declare the process and input variables
#------------------------------------------------------------------------------------

from Configuration.StandardSequences.Eras import eras
process                 = cms.Process('NOISE',
        eras.Run3
        )

options = VarParsing.VarParsing ('analysis')
options.register ('skipEvents', 0, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "no of skipped events")
options.outputFile = 'trial_mc.root'
options.maxEvents = 1 #-1 # means all events
# INPUT files
options.inputFiles ="root://cms-xrdr.private.lo:2094//xrd/store/mc/Run3Winter24Reco/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RECO/FlatPU0to80_133X_mcRun3_2024_realistic_v8-v3/80000/ff8de18a-c0f3-44a8-9a09-55de91da763f.root"
options.register('isMC', True, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.bool, "Is this MC data?")
options.isMC = 0 # 0 for DATA and 1 for MC

#------------------------------------------------------------------------------------
# Get and parse the command line arguments
#------------------------------------------------------------------------------------
options.parseArguments()
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.source = cms.Source("PoolSource",
        fileNames  = cms.untracked.vstring(options.inputFiles),
        skipEvents = cms.untracked.uint32(options.skipEvents) # default is 0.
        )
process.TFileService = cms.Service("TFileService",
        fileName = cms.string(options.outputFile)
        )

# import of standard configurations
#------------------------------------------------------------------------------------
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.RecoSim_cff')
process.load('CommonTools.ParticleFlow.EITopPAG_cff')
process.load('PhysicsTools.PatAlgos.slimming.metFilterPaths_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')

# Set up our analyzer
#------------------------------------------------------------------------------------
process.load("hcalllp.babymaker.HcalTupleMaker_Tree_cfi")
process.load("hcalllp.babymaker.HcalTupleMaker_Event_cfi")
#process.load("hcalllp.babymaker.HcalTupleMaker_QIE11Digis_cfi")   # Required members are now merged to HBHERecHits branch
process.load("hcalllp.babymaker.HcalTupleMaker_HBHERecHits_cfi")
process.load("hcalllp.babymaker.HcalTupleMaker_Trigger_cfi")
process.load("hcalllp.babymaker.HcalTupleMaker_GenParticles_cfi")  # Not needed in general
process.load("hcalllp.babymaker.HcalTupleMaker_TriggerFilter_cfi")

process.load("hcalllp.babymaker.HcalTupleMaker_CaloJetMet_cfi")
process.hcalTupleTriggerFilter.isMC = cms.bool(options.isMC) # Use the flag from VarParsing

process.hcalTupleTriggerFilter.metFiltersInputTag = cms.InputTag("TriggerResults", "", "RECO") 
from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '133X_mcRun3_2024_realistic_v8', '')
process.GlobalTag = GlobalTag(process.GlobalTag, '133X_mcRun3_2024_realistic_v10', '')
process.tuple_step = cms.Sequence(
        # Make HCAL tuples: Event, run, ls number
        process.hcalTupleEvent*
        process.hcalTupleHBHERecHits*
        process.hcalTupleCaloJetMet # *
        )
process.preparation = cms.Path(
         process.tuple_step
        )

process.triggerFilterPathsTask = cms.Task(
    process.goodVertices,
    process.globalSuperTightHalo2016Filter,
    process.EcalDeadCellTriggerPrimitiveFilter,
    process.BadPFMuonFilter,
    process.BadPFMuonDzFilter,
    process.hfNoisyHitsFilter,
    process.eeBadScFilter
)

process.triggerFilters = cms.Path(process.triggerFilterPathsTask)
process.eventTuplePath = cms.Path(
    process.hcalTupleTriggerFilter*  # Ensure this runs after patTrigger
    process.hcalTupleTree
)
process.endjob_step = cms.EndPath(process.endOfProcess) # --

process.schedule = cms.Schedule( # --
    process.preparation, # Run the preparation path
    process.triggerFilters,
    process.eventTuplePath,  # Then run the event tuple path
    process.endjob_step
)




