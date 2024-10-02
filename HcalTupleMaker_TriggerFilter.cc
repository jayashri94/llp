#include "hcalllp/babymaker/interface/HcalTupleMaker_TriggerFilter.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/PatCandidates/interface/TriggerEvent.h" // Include necessary header for pat::TriggerEvent
#include <iostream>
#include "FWCore/MessageLogger/interface/MessageLogger.h"
HcalTupleMaker_TriggerFilter::HcalTupleMaker_TriggerFilter(const edm::ParameterSet& iConfig)
  : isMC(iConfig.getParameter<bool>("isMC")), // Initialize the isMC flag
//    : triggerResultsToken_(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("metFiltersInputTag"))) {
//initialize triggerResultsToken_ as default-constructed token if isMC is true, and otherwise consumes the TriggerResults
  triggerResultsToken_(isMC ? edm::EDGetToken() : consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("metFiltersInputTag"))) {

   //Conditionally consume filters based on isMC
  if (isMC) {
      globalSuperTightHalo2016FilterToken_ = consumes<bool>(edm::InputTag("globalSuperTightHalo2016Filter"));
      EcalDeadCellTriggerPrimitiveFilterToken_ = consumes<bool>(edm::InputTag("EcalDeadCellTriggerPrimitiveFilter"));
      BadPFMuonFilterToken_ = consumes<bool>(edm::InputTag("BadPFMuonFilter"));
      BadPFMuonDzFilterToken_ = consumes<bool>(edm::InputTag("BadPFMuonDzFilter"));
      hfNoisyHitsFilterToken_ = consumes<bool>(edm::InputTag("hfNoisyHitsFilter"));
      eeBadScFilterToken_ = consumes<bool>(edm::InputTag("eeBadScFilter"));
      //goodVerticesToken_ = consumes<bool>(edm::InputTag("goodVertices"));
      goodVerticesToken_ = consumes<edm::ValueMap<int>>(edm::InputTag("offlinePrimaryVertices", "", "RECO"));
 }

  produces<bool> ( "pass"   );
  // Add produces for the filter flags
  produces<bool>("FlagglobalSuperTightHalo2016Filter");
  produces<bool>("FlagEcalDeadCellTriggerPrimitiveFilter");
  produces<bool>("FlagBadPFMuonFilter");
  produces<bool>("FlagBadPFMuonDzFilter");
  produces<bool>("FlaghfNoisyHitsFilter");
  produces<bool>("FlageeBadScFilter");
  produces<bool>("FlaggoodVertices");
}

void HcalTupleMaker_TriggerFilter::
produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  std::unique_ptr<bool         >  pass  ( new bool        (true) );
  // Define the lambda outside the if-else blocks
//  std::function<std::unique_ptr<bool>(const std::string&)> createFilterPtr;

  if(isMC){
 //        For MC the filters are processed on the fly and we access the results
 //   List of filter names
    std::vector<std::string> filterNames = {
     "globalSuperTightHalo2016Filter",
     "EcalDeadCellTriggerPrimitiveFilter",
     "BadPFMuonFilter",
     "BadPFMuonDzFilter",
     "hfNoisyHitsFilter",
     "eeBadScFilter",
     "goodVertices"
  };
  //   Loop over the filters
    for (const std::string& filterName : filterNames) {
   //      Create a handle for the filter result
 edm::Handle<bool> filterResult;
        edm::Handle<edm::ValueMap<int>> vertexHandle;
     //   Use the correct token for the MC filter
          if (filterName == "globalSuperTightHalo2016Filter") {
            iEvent.getByToken(globalSuperTightHalo2016FilterToken_, filterResult);
        } else if (filterName == "EcalDeadCellTriggerPrimitiveFilter") {
            iEvent.getByToken(EcalDeadCellTriggerPrimitiveFilterToken_, filterResult);
        } else if (filterName == "BadPFMuonFilter") {
            iEvent.getByToken(BadPFMuonFilterToken_, filterResult);
        } else if (filterName == "BadPFMuonDzFilter") {
            iEvent.getByToken(BadPFMuonDzFilterToken_, filterResult);
        } else if (filterName == "hfNoisyHitsFilter") {
            iEvent.getByToken(hfNoisyHitsFilterToken_, filterResult);
        } else if (filterName == "eeBadScFilter") {
            iEvent.getByToken(eeBadScFilterToken_, filterResult);
        } else if (filterName == "goodVertices") {
            iEvent.getByToken(goodVerticesToken_, vertexHandle);
        }

        if (filterName == "goodVertices") {

           if (vertexHandle.isValid()) {
                 for (size_t i = 0; i < vertexHandle->size(); ++i) {
                        int value = (*vertexHandle)[i];
                        std::cout << "Vertex " << i << " flag value: " << value << std::endl;
                }
                 bool passed = false;
                 for (const auto& val : *vertexHandle) {
                        if (val > 0) {
                            passed = true;
                            break;
                        }
                    } 
 std::cout << filterName << " passed: " << passed << std::endl;
                 iEvent.put(std::make_unique<bool>(passed), "Flag" + filterName);
                *pass &= passed;  // Logical AND with the overall pass
           } else {
                std::cerr << filterName << " result not found!" << std::endl;
           }
        } else {

        if (filterResult.isValid()) {
        //     Get the filter acceptance
            bool passed = *filterResult;
            std::cout << filterName << " passed: " << passed << std::endl;
      //      Save the result into the event
                iEvent.put(std::make_unique<bool>(passed), "Flag" + filterName);
          //  Update the overall pass status
                *pass &= passed;  //Logical AND with the overall pass
        } else {
            std::cerr << filterName << " result not found!" << std::endl;
            *pass = false;  //If any filter result is invalid, mark overall as false
        }

     }
  }

}else {
//      for data  Access TriggerResults
  edm::Handle<edm::TriggerResults> triggerResults;
  iEvent.getByToken(triggerResultsToken_, triggerResults);
  const edm::TriggerNames & triggerNames = iEvent.triggerNames(*triggerResults);
// Debug: Print all trigger names
    for (unsigned int i = 0; i < triggerNames.size(); ++i) {
        std::cout << "Trigger name: " << triggerNames.triggerName(i) << std::endl;
     }
 // Debug: Print the size of triggerResults and triggerNames
//  std::cout << "Size of triggerResults: " << triggerResults->size() << std::endl;
//  std::cout << "Size of triggerNames: " << triggerNames.size() << std::endl;
  auto createFilterPtr = [&triggerResults, &triggerNames](const std::string& filterName) -> std::unique_ptr<bool> {
 unsigned int index = triggerNames.triggerIndex(filterName);
        if (index >= triggerResults->size()) {
            std::cerr << "Index out of bounds for filter: " << filterName << " (Index: " << index << ")" << std::endl;
            return std::make_unique<bool>(false); // Default value or handle error
        }
        return std::make_unique<bool>(triggerResults->accept(index));
   // Debug: Print the acceptance of each filter
   //   bool isAccepted = triggerResults->accept(index);
   //   std::cout << "Filter: " << filterName << " is accepted: " << std::boolalpha << isAccepted << std::endl;
   //   return std::make_unique<bool>(isAccepted);
    };
//Fill the filter results to the output tree
  auto goodVertices = createFilterPtr("Flag_goodVertices");
  auto globalSuperTightHalo2016Filter = createFilterPtr("Flag_globalSuperTightHalo2016Filter");
  auto EcalDeadCellTriggerPrimitiveFilter = createFilterPtr("Flag_EcalDeadCellTriggerPrimitiveFilter");
  auto BadPFMuonFilter = createFilterPtr("Flag_BadPFMuonFilter");
  auto BadPFMuonDzFilter = createFilterPtr("Flag_BadPFMuonDzFilter");
  auto hfNoisyHitsFilter = createFilterPtr("Flag_hfNoisyHitsFilter");
  auto eeBadScFilter = createFilterPtr("Flag_eeBadScFilter");


  // Perform the logical AND of all filter results
  *pass = *goodVertices && *globalSuperTightHalo2016Filter && *EcalDeadCellTriggerPrimitiveFilter && *BadPFMuonFilter && *BadPFMuonDzFilter;
  // Put the filter results into the event
  iEvent.put(std::move(goodVertices), "FlaggoodVertices");
  iEvent.put(std::move(globalSuperTightHalo2016Filter), "FlagglobalSuperTightHalo2016Filter");
  iEvent.put(std::move(EcalDeadCellTriggerPrimitiveFilter), "FlagEcalDeadCellTriggerPrimitiveFilter");
  iEvent.put(std::move(BadPFMuonFilter),   "FlagBadPFMuonFilter");
  iEvent.put(std::move(BadPFMuonDzFilter), "FlagBadPFMuonDzFilter");
  iEvent.put(std::move(hfNoisyHitsFilter),     "FlaghfNoisyHitsFilter");
  iEvent.put(std::move(eeBadScFilter),     "FlageeBadScFilter");

 }

  // Put the pass value into the event
  iEvent.put(std::move(pass), "pass");
}
