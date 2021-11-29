class LinearInterpolator:
    def __init__(self):
        pass

    def fit(self, xs, ys):
        self.xs=xs
        self.ys=ys
    
    def interpolate_point(self, y):
        index=len(list(filter(lambda x: x <= y, self.xs)))
        if len(list(filter(lambda x: x == y, self.xs)))==0:
            point=self.ys[index-1]+((self.ys[index]-self.ys[index-1])/(self.xs[index]-self.xs[index-1]))*(y-self.xs[index-1])
        else:
            point=self.ys[index-1]
        return point

    def interpolate_array(self, ys):
        inter_list=[self.interpolate_point(y) for y in ys]
        return inter_list
      
class LinearExtrapolator:
    def __init__(self):
        pass

    def fit(self, xs, ys):
        self.xs=xs
        self.ys=ys
    
    def extrapolate_point(self, y):
        index=len(list(self.xs))-1
        point=self.ys[index-1]+((self.ys[index]-self.ys[index-1])/(self.xs[index]-self.xs[index-1]))*(y-self.xs[index-1])
        return point

    def extrapolate_array(self, ys):
        inter_list=[self.interpolate_point(y) for y in ys]
        return inter_list

class Discountfactor:
    
    def __init__(self):
        pass
    
    def fit(self, filename):
        df1=pd.read_csv(filename)
        a=[df1['Unnamed: 1'].iloc[0]*100]
        a=a+(list((100-df1[1:]['Unnamed: 1']).values))
        b=list(df1['StartDate'].values)
        df1['delta']=pd.to_datetime(df1['StartDate'])-pd.to_datetime(df1['StartDate'].iloc[0])
        df1['delta']=df1['delta'].apply(lambda x: x.days)
        df1['rates']=a
        df1['df']=1/(1+df1['rates']/100*df1['delta']/360)
        self.df=df1
    
    def dis_point(self,date):
        inter=LinearInterpolator()
        inter.fit(self.df.delta.values,self.df.df.values)
        extra=LinearExtrapolator()
        extra.fit(self.df.delta.values,self.df.df.values)
        delta=(pd.to_datetime(date)-pd.to_datetime(self.df.StartDate.iloc[0])).days
        if delta<=df1['delta'].iloc[-1]:
            return inter.interpolate_point(delta)
        else:
            return extra.extrapolate_point(delta)
    
    def dis_array(self,dates):
        itog=pd.DataFrame()
        itog['dates']=dates
        itog['df']=[self.dis_point(date) for date in dates]
        return itog
