# Early Warning for Critical Events

An experimental deep-learning project for predicting sepsis from longitudinal
patient vital signs and laboratory measurements before clinical onset. The
repository contains preprocessing and training notebooks, trained PyTorch
models, scalers, evaluation plots, and SHAP explainability outputs.

> **Warning:** This is a research and educational project, not a medical
> device. Its predictions must not be used for diagnosis, treatment, or
> clinical decision-making.

## What is included

- Data preprocessing with missing-value imputation, scaling, and categorical
  feature encoding.
- LSTM-based sepsis prediction using up to the most recent 48 hourly
  observations.
- Model evaluation with ROC, precision-recall, and confusion-matrix plots.
- SHAP-based feature importance and temporal explainability.
- Saved PyTorch checkpoints and fitted preprocessing scalers.

## Repository layout

```text
.
├── data_preprocessing_pipeline.ipynb
├── data_precessing_pipeline_updated.ipynb
├── models/
│   ├── latm_v4.ipynb              # LSTM v4 training and evaluation
│   ├── inference.ipynb            # Inference on new .psv files
│   ├── saved_models/              # PyTorch checkpoints and scalers
│   └── results/                   # Metrics, plots, and SHAP outputs
├── processed_training_Ay/         # Processed patient .psv files
├── processed_training_setB/       # Additional processed patient .psv files
└── sepsis_prediction_model.keras  # Keras model artifact
```

## Requirements

Use Python 3.10 or newer and install the notebook dependencies:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install numpy pandas scikit-learn matplotlib joblib torch shap jupyter
```

## Running the workflow

1. Place the input patient files in the expected processed-data folders. The
   files should be pipe-separated `.psv` files containing the `SepsisLabel`
   target column for training.
2. Open `data_preprocessing_pipeline.ipynb` or
   `data_precessing_pipeline_updated.ipynb` and run the preprocessing cells.
3. Open `models/latm_v4.ipynb`. Run it from the `models/` directory, check the
   configuration paths, and run the training and evaluation cells.
4. Review the generated files in `models/results/` and the checkpoints in
   `models/saved_models/`.
5. For inference, open `models/inference.ipynb`, update `NEW_DATA_DIR` to a
   folder of new `.psv` files, verify the model and scaler paths, and run the
   notebook. Predictions are written to the configured output CSV.

The training and inference notebooks must use compatible feature ordering,
model architecture, scaler, and sequence length. The inference notebook
currently uses the v4 checkpoint, a 48-timestep window, and a threshold of
`0.35`; adjust these only when they match the training configuration.

## Results and explainability

The `models/results/` directory includes:

- ROC, precision-recall, and confusion-matrix plots.
- Training-history and SHAP feature-importance plots.
- Ranked SHAP feature values in CSV and NumPy formats.

Run the SHAP section in `models/latm_v4.ipynb` after training to regenerate
the explainability outputs.

## License

This project is distributed under the license in [LICENSE](LICENSE).
