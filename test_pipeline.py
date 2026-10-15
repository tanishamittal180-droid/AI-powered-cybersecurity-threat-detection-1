import unittest
import pandas as pd
from src.data_generator import generate_dataset
from src.ml_pipeline import prepare_frame, train_models, predict_rows
from src.config import FEATURES

class PipelineTests(unittest.TestCase):
    def test_generator_has_expected_schema(self):
        df = generate_dataset(40)
        self.assertTrue(set(FEATURES + ["label"]).issubset(df.columns))
        self.assertEqual(len(df), 40)

    def test_prepare_frame_drops_non_numeric_rows(self):
        df = generate_dataset(40)
        df.loc[0, "packet_size"] = "invalid"
        clean = prepare_frame(df)
        self.assertEqual(len(clean), 39)

    def test_train_and_predict(self):
        df = generate_dataset(160)
        metrics = train_models(df)
        self.assertIn("f1", metrics)
        scored = predict_rows(df[FEATURES].head(5))
        self.assertEqual(len(scored), 5)
        self.assertIn("threat_probability", scored.columns)

if __name__ == "__main__": unittest.main()
