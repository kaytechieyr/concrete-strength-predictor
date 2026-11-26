"""Basic tests for the training pipeline."""

import unittest

from train import FEATURE_COLUMNS, TARGET_COLUMN, build_candidates, load_data, split_data


class TrainingPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_data()

    def test_dataset_is_complete(self) -> None:
        self.assertEqual(len(self.data), 1005)
        self.assertFalse(self.data[[*FEATURE_COLUMNS, TARGET_COLUMN]].isna().any().any())

    def test_split_covers_all_records(self) -> None:
        train, validation, test = split_data(self.data)
        self.assertEqual(len(train) + len(validation) + len(test), len(self.data))
        self.assertEqual((len(train), len(validation), len(test)), (703, 151, 151))

    def test_candidate_models_can_predict(self) -> None:
        train, validation, _ = split_data(self.data)
        for model in build_candidates().values():
            model.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMN])
            prediction = model.predict(validation[FEATURE_COLUMNS].head(3))
            self.assertEqual(len(prediction), 3)


if __name__ == "__main__":
    unittest.main()
