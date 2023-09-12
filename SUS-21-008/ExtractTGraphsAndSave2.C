#include <TFile.h>
#include <TCanvas.h>
#include <TList.h>
#include <TGraph.h>

void ExtractTGraphsAndSave2(const char* inputFile, const char* outputFile, const char* canvasName) {
    TFile* file = new TFile(inputFile, "READ"); // Open the root file
    if (!file || file->IsZombie()) {
        std::cerr << "Error: Cannot open the input file: " << inputFile << std::endl;
        return;
    }

    TCanvas* canvas = (TCanvas*)file->Get(canvasName); // Get the TCanvas object
    if (!canvas) {
        std::cerr << "Error: Cannot find the TCanvas '" << canvasName << "' in the input file." << std::endl;
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
    int graphCounter = 1;
    while ((obj = next())) { // Loop through the list of objects
        if (obj->InheritsFrom(TGraph::Class())) { // Check if the object is a TGraph
            TGraph* graph = (TGraph*)obj;
            TString graphName = Form("TGraph%d", graphCounter++); // Generate a unique name
            graph->Write(graphName); // Write the TGraph to the output file with its unique name as the key
            std::cout << "Saved TGraph '" << graphName << "' to the output file." << std::endl;
        }
    }

    outputFilePtr->Close(); // Close the output file
    file->Close(); // Close the input file
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <inputFile> <outputFile> <canvasName>" << std::endl;
        return 1;
    }

    const char* inputFile = argv[1];
    const char* outputFile = argv[2];
    const char* canvasName = argv[3];

    ExtractTGraphsAndSave2(inputFile, outputFile, canvasName);

    return 0;
}
