# Code for the diagnosis of acute cholecystitis from CT images and blood tests

Jupyter notebooks used for the analyses in the manuscript. Each notebook contains the code and the outputs of the run reported in the paper.

## Directory structure

| Directory | Figure | Notebook | Content |
|---|---|---|---|
| `image_model/` | Fig. 2 | `20261024_image_model_revice_with_95ci.ipynb` | Image model (EfficientNetB0) trained on one representative CT slice per patient. Evaluation on the representative slice and on all gallbladder slices of each test patient (hybrid TotalSegmentator masks; a patient is positive if any slice is positive), Grad-CAM, and 95% confidence intervals. |
| `blood_model/` | Fig. 3 | `20261024_fig3_blood_model_revice_with_95ci.ipynb` | Blood-test model (10 blood tests, PyCaret extra trees) with the 7:3 train/test split, and 95% confidence intervals. |
| `hybrid_model/` | Fig. 4 | `20261024_fig4_hybrid_model_revice_with_95ci.ipynb` | Hybrid model (blood tests + image features from the image model, reduced by PCA fitted on the training data only), evaluated on all gallbladder slices of each test patient, and 95% confidence intervals. |
| `supple/` | Supplementary | `20261022_fig4_5fold_cv_hybrid.ipynb` | Five-fold cross-validation of the hybrid model with the algorithm selected and tuned within each training fold (nested). |
| | | `20261022_fig3_5fold_cv_blood.ipynb` | Five-fold cross-validation of the blood-test model: nested algorithm selection, and the algorithm fixed to random forest. |
| | | `20261022_fig3_blood_only_et_5fold_cv.ipynb` | Five-fold cross-validation of the blood-test model with the algorithm fixed to extra trees. |

## Study cohort and evaluation

- 197 patients (100 with acute cholecystitis, 97 controls).
- Main analyses (Fig. 2–4): patient-level 7:3 split into a training set and a test set.
- Supplementary analyses: patient-level five-fold cross-validation stratified by diagnosis (random seed 42). In each fold, the image model, the PCA and the classifier were fitted on the training patients of that fold only.
- 95% confidence intervals: Wilson score interval for accuracy, sensitivity, specificity, PPV and NPV; stratified bootstrap (2,000 resamples) for AUC and F1.

## Environment

- Python 3.10
- Image model: TensorFlow 2.16, scikit-learn, OpenCV, nibabel
- Blood-test and hybrid models: PyCaret 3.3.2 (Python 3.9–3.11)
- Gallbladder segmentation: TotalSegmentator

## Data availability

The CT images, segmentation masks and clinical data are not included in this repository. The paths at the top of each notebook (`root`, `DATA_DIR`, `BASE`) point to the local data directory.
