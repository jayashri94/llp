#ifndef HcalTupleMaker_TriggerFilter_h
#define HcalTupleMaker_TriggerFilter_h

#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "DataFormats/Common/interface/TriggerResults.h"

class HcalTupleMaker_TriggerFilter : public edm::stream::EDProducer<> {
 public:
  explicit HcalTupleMaker_TriggerFilter(const edm::ParameterSet&);

 private:
  void produce( edm::Event &, const edm::EventSetup & );

 private:
    bool isMC; // Member variable to hold the isMC flag
    edm::EDGetToken triggerResultsToken_;
    // Declare tokens for filters
    edm::EDGetTokenT<bool> globalSuperTightHalo2016FilterToken_;
    edm::EDGetTokenT<bool> EcalDeadCellTriggerPrimitiveFilterToken_;
    edm::EDGetTokenT<bool> BadPFMuonFilterToken_;
    edm::EDGetTokenT<bool> BadPFMuonDzFilterToken_;
    edm::EDGetTokenT<bool> hfNoisyHitsFilterToken_;
    edm::EDGetTokenT<bool> eeBadScFilterToken_;
    //edm::EDGetTokenT<bool> goodVerticesToken_;
    edm::EDGetTokenT<edm::ValueMap<int>> goodVerticesToken_;
};

#endif
