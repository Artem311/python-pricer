
import pandas as pd
import numpy as np
import math

class DiscountFactorsEstimator():
  """
  Class for estimating discount factors based on 3 months LIBOR and Eurodollar futures quotes

  Args
  ----
  data_path: str, required
      Path to 'USD rates.csv' file

  """
  def __init__(self, data_path):

    df = pd.read_csv(data_path)
    df['StartDate'] = pd.to_datetime(df['StartDate'])
    df['EndDate'] = pd.to_datetime(df['EndDate'])

    self.libor3m = df[['Unnamed: 1','StartDate','EndDate']].values[0]
    self.eurodollars = df[['Unnamed: 1','StartDate','EndDate']].values[1:]
    self.implied_rates = df[['Unnamed: 1','StartDate','EndDate']].values[1:]
    self.implied_rates[:,0] = (100-self.implied_rates[:,0])*0.01
    self.all_rates = np.concatenate((self.libor3m.reshape(1,3),self.implied_rates),axis=0)

    self.no_missings_rates = []
    for i in range(len(self.all_rates)-1):
      if (self.all_rates[i][2] >= self.all_rates[i+1][1]):
        self.no_missings_rates.append(self.all_rates[i])
      else:
        days_current = (self.all_rates[i][2] - self.all_rates[i][1]).days
        days_future = (self.all_rates[i+1][1] - self.all_rates[i][2]).days
        total_days = days_current + days_future
        new_rate = self.all_rates[i][0]*total_days/days_current
        self.no_missings_rates.append(np.array([new_rate,self.all_rates[i][1],self.all_rates[i+1][1]]))
    self.no_missings_rates = np.array(self.no_missings_rates)

    self.aligned_rates = [self.no_missings_rates[0]]
    for i in range(1,len(self.no_missings_rates)):
      if self.no_missings_rates[i-1][2] == self.no_missings_rates[i][1]:
        self.aligned_rates.append(self.no_missings_rates[i])
        continue
      else:
        # (1+r1)(1+r2_new) = (1+r2)(1+r1)^(r1_days_before_r2/r1_days)
        #
        r1_days = (self.no_missings_rates[i-1][2] - self.no_missings_rates[i-1][1]).days
        r1_days_before_r2 = (self.no_missings_rates[i][1] - self.no_missings_rates[i-1][1]).days
        r2_new = (1+self.no_missings_rates[i][0])*(1+self.no_missings_rates[i-1][0])**(r1_days_before_r2/r1_days) / (1+self.no_missings_rates[i-1][0]) - 1
        self.aligned_rates.append(np.array([r2_new,self.no_missings_rates[i-1][2],self.no_missings_rates[i][2]]))
    self.aligned_rates = np.array(self.aligned_rates)


  def get_discount_factor_for_date(self, date):
    """
    Function for getting discount factor for one date

    Args
    ----
    date: pd.Timestamp, required
        Date for which discount factor is needed
    
    Returns
    -------
    discount factor: float
        Discount factor value
    
    """
    if date <= self.aligned_rates[0][1]:
      #print("Date should be after",self.aligned_rates[0][1])
      return 1.0
    elif date > self.aligned_rates[-1][2]:
      accumulated_rate = np.prod(self.aligned_rates[:-1,0]+1)
      this_rate_days = (self.aligned_rates[-1][2]-self.aligned_rates[-1][1]).days
      needed_days = (date-self.aligned_rates[-1][1]).days
      rate = accumulated_rate * (1+self.aligned_rates[-1][0])**(needed_days/this_rate_days)
      return 1/rate

    else:
      accumulated_rate = 1.0
      for i in range(len(self.aligned_rates)):
        if date > self.aligned_rates[i][2]:
          accumulated_rate *= (1+self.aligned_rates[i][0])
        else:
          break
      this_rate_days = (self.aligned_rates[i][2]-self.aligned_rates[i][1]).days
      needed_days = (date-self.aligned_rates[i][1]).days
      rate = accumulated_rate * (1+self.aligned_rates[i][0])**(needed_days/this_rate_days)
      return 1/rate

  def get_discount_factors(self,dates):
    """
    Function for getting discount factors for the list of dates

    Args
    ----
    dates: iterable, required
        Array of dates, each date is pd.Timestamp
    
    Returns
    -------
    discount factors: np.array
        np.array of elements [date, discount factor]
    
    """
    return np.array(list(zip(dates,np.array([self.get_discount_factor_for_date(d) for d in dates]))))