#include <TFile.h>
#include <TCanvas.h>
#include <TList.h>
#include <TGraph.h>

void ExtractTGraphsAndSave(const char* inputFile, const char* outputFile) {
    TFile* file = new TFile(inputFile, "READ"); // Open the root file
    if (!file || file->IsZombie()) {
        std::cerr << "Error: Cannot open the input file: " << inputFile << std::endl;
        return;
    }

    TCanvas* canvas = (TCanvas*)file->Get("summary_comb_DM_sosOnly"); // Get the TCanvas object
    if (!canvas) {
        std::cerr << "Error: Cannot find the TCanvas 'summary_comb_DM_sosOnly' in the input file." << std::endl;
        file->Close();
        return;
    }

    TList* graphList = canvas->GetListOfPrimitives(); // Get the list of primitives (TGraphs and other objects) from the canvas
    if (!graphList) {
        std::cerr << "Error: No primitives found in the TCanvas." << std::endl;
        file->Close();
        return;
    }

    TFile* outputFilePtr = new TFile(outputFile, "RECREATE"); // Create the output file
    TIter next(graphList); // Create an iterator to loop through the list
    TObject* obj;
    while ((obj = next())) { // Loop through the list of objects
        if (obj->InheritsFrom(TGraph::Class())) { // Check if the object is a TGraph
            TGraph* graph = (TGraph*)obj;
            TString graphName = graph->GetName();
            graph->Write(graphName); // Write the TGraph to the output file with its name as the key
            std::cout << "Saved TGraph '" << graphName << "' to the output file." << std::endl;
        }
    }

    outputFilePtr->Close(); // Close the output file
    file->Close(); // Close the input file
}

void extractTGraphs() {
    const char* inputFile = "/Users/ankush/Downloads/summary_comb_DM_sosOnly.root";
    const char* outputFile = "/Users/ankush/lim_graphs.root";
    ExtractTGraphsAndSave(inputFile, outputFile);
}
