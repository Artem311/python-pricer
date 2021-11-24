
from src.discount_factors import DiscountFactorsEstimator
import pandas as pd

def test_correct_work(data_path):
  DFE = DiscountFactorsEstimator(data_path)
  assert DFE.get_discount_factor_for_date(pd.Timestamp('10-28-2021')) == 1.0
  assert DFE.get_discount_factor_for_date(pd.Timestamp('10-29-2021')) == 0.9999859331183882