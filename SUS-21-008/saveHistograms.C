#include <TFile.h>
#include <TCanvas.h>
#include <TH1.h>
#include <THStack.h>
#include <TGraphAsymmErrors.h>
#include <TKey.h>

void saveHistograms(const char* input_file, const char* output_file) {
    TFile* tf_input = TFile::Open(input_file);
    if (!tf_input || tf_input->IsZombie()) {
        std::cerr << "Error: Could not open the input file." << std::endl;
        return;
    }

    TFile* tf_output = TFile::Open(output_file, "RECREATE");
    if (!tf_output || tf_output->IsZombie()) {
        std::cerr << "Error: Could not create the output file." << std::endl;
        tf_input->Close();
        return;
    }

    TList* canvas_list = tf_input->GetListOfKeys();
    TIter next_canvas(canvas_list);
    TKey* key_canvas;

    while ((key_canvas = static_cast<TKey*>(next_canvas()))) {
        TObject* obj_canvas = key_canvas->ReadObj();
        if (!obj_canvas || !obj_canvas->InheritsFrom("TCanvas")) {
            continue;
        }

        TCanvas* c = static_cast<TCanvas*>(obj_canvas);

        TPad* pad1 = static_cast<TPad*>(c->FindObject("pad1"));
        if (!pad1) {
            std::cerr << "Error: 'pad1' not found in canvas '" << c->GetName() << "'." << std::endl;
            continue;
        }

        TList* pad1List = pad1->GetListOfPrimitives();

        for (int i = 0; i < pad1List->GetSize(); ++i) {
            TObject* obj1 = pad1List->At(i);

            if (obj1->InheritsFrom("THStack")) {
                THStack* stack = static_cast<THStack*>(obj1);
                TList* histograms = stack->GetHists();
                TIter next_hist(histograms);
                TH1* hist;

                while ((hist = static_cast<TH1*>(next_hist()))) {
                    tf_output->cd();
                    hist->Write();
                }
            } else {
                tf_output->cd();
                obj1->Write();
            }
        }
    }

    tf_input->Close();
    tf_output->Close();

    delete tf_input;
    delete tf_output;
}
