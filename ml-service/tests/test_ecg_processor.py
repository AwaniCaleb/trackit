"""
Tests for ecg_processor — classification and 12-lead derivation.

Run from the ml-service directory:
    pytest tests/ -v
"""
import numpy as np
import pytest
import neurokit2 as nk

from ecg_processor import analyse, classify, derive_leads, LEAD_LENGTH, MIN_SAMPLES, SAMPLING_RATE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simulate(heart_rate: int, duration: float = 10.0) -> list[float]:
    """Simulate a clean ECG at the given heart rate using the service's sampling rate."""
    return nk.ecg_simulate(
        duration=duration,
        sampling_rate=SAMPLING_RATE,
        heart_rate=heart_rate,
        noise=0,
        random_state=42,
    ).tolist()


# ---------------------------------------------------------------------------
# classify()
# ---------------------------------------------------------------------------

class TestClassify:
    def test_normal_sinus_rhythm(self):
        label, conf = classify(_simulate(70))
        assert label == "Normal"
        assert 0.7 <= conf <= 0.95

    def test_tachycardia(self):
        label, conf = classify(_simulate(120))
        assert label == "Tachycardia"
        assert 0.5 < conf <= 0.95

    def test_bradycardia(self):
        label, conf = classify(_simulate(45))
        assert label == "Bradycardia"
        assert 0.5 < conf <= 0.95

    def test_short_signal_returns_unavailable(self):
        label, conf = classify([0.0] * (MIN_SAMPLES - 1))
        assert label == "Unavailable"
        assert conf == 0.0

    def test_empty_signal_returns_unavailable(self):
        label, conf = classify([])
        assert label == "Unavailable"
        assert conf == 0.0

    def test_confidence_is_float_in_unit_range(self):
        _, conf = classify(_simulate(70))
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

    def test_label_is_always_a_recognised_class(self):
        valid = {"Normal", "Tachycardia", "Bradycardia", "Atrial Fibrillation", "Chaotic", "Unavailable"}
        for hr in [45, 70, 120]:
            label, _ = classify(_simulate(hr))
            assert label in valid


# ---------------------------------------------------------------------------
# derive_leads()
# ---------------------------------------------------------------------------

class TestDeriveLeads:
    ALL_LEADS = {"I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"}

    def setup_method(self):
        self.leads = derive_leads(_simulate(70))

    def test_returns_all_twelve_leads(self):
        assert set(self.leads.keys()) == self.ALL_LEADS

    def test_each_lead_is_exactly_lead_length_samples(self):
        for name, values in self.leads.items():
            assert len(values) == LEAD_LENGTH, (
                f"{name}: expected {LEAD_LENGTH} samples, got {len(values)}"
            )

    def test_einthoven_law_I_plus_III_equals_II(self):
        I   = np.array(self.leads["I"])
        II  = np.array(self.leads["II"])
        III = np.array(self.leads["III"])
        np.testing.assert_allclose(I + III, II, atol=1e-9)

    def test_avr_goldberger_formula(self):
        I   = np.array(self.leads["I"])
        II  = np.array(self.leads["II"])
        aVR = np.array(self.leads["aVR"])
        np.testing.assert_allclose(aVR, -(I + II) / 2.0, atol=1e-9)

    def test_avl_goldberger_formula(self):
        I   = np.array(self.leads["I"])
        II  = np.array(self.leads["II"])
        aVL = np.array(self.leads["aVL"])
        np.testing.assert_allclose(aVL, I - II / 2.0, atol=1e-9)

    def test_avf_goldberger_formula(self):
        I   = np.array(self.leads["I"])
        II  = np.array(self.leads["II"])
        aVF = np.array(self.leads["aVF"])
        np.testing.assert_allclose(aVF, II - I / 2.0, atol=1e-9)

    def test_all_values_are_python_floats(self):
        for name, values in self.leads.items():
            assert all(isinstance(v, float) for v in values), (
                f"{name} contains non-float values"
            )

    def test_short_input_pads_to_lead_length(self):
        leads = derive_leads([0.5] * 100)
        for name, values in leads.items():
            assert len(values) == LEAD_LENGTH

    def test_long_input_truncates_to_lead_length(self):
        leads = derive_leads([0.5] * 2000)
        for name, values in leads.items():
            assert len(values) == LEAD_LENGTH

    def test_precordial_leads_span_negative_to_positive(self):
        # V1 ratio is -0.3 (negative), V6 ratio is 0.9 (positive) — verify polarity
        v1 = np.array(self.leads["V1"])
        v6 = np.array(self.leads["V6"])
        # The signals won't be uniformly negative/positive but their sums should reflect the ratios
        assert np.sum(v1) < np.sum(v6)


# ---------------------------------------------------------------------------
# analyse() — integration
# ---------------------------------------------------------------------------

class TestAnalyse:
    def test_returns_required_top_level_keys(self):
        result = analyse(_simulate(70))
        assert set(result.keys()) == {"classification", "confidence", "leads"}

    def test_classification_is_a_recognised_class(self):
        result = analyse(_simulate(70))
        valid = {"Normal", "Tachycardia", "Bradycardia", "Atrial Fibrillation", "Chaotic", "Unavailable"}
        assert result["classification"] in valid

    def test_leads_dict_has_twelve_entries(self):
        result = analyse(_simulate(70))
        assert len(result["leads"]) == 12

    def test_normal_signal_full_pipeline(self):
        result = analyse(_simulate(70))
        assert result["classification"] == "Normal"
        assert result["confidence"] >= 0.7
        assert len(result["leads"]["II"]) == LEAD_LENGTH

    def test_tachycardia_signal_full_pipeline(self):
        result = analyse(_simulate(120))
        assert result["classification"] == "Tachycardia"

    def test_bradycardia_signal_full_pipeline(self):
        result = analyse(_simulate(45))
        assert result["classification"] == "Bradycardia"
