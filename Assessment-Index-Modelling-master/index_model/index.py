import datetime as dt
from dateutil.relativedelta import relativedelta
from dateutil import rrule
import pandas as pd

class IndexModel:
    def __init__(self):
        self.data = pd.read_csv("/Users/abc/Desktop/Assessment-Index-Modelling-master/data_sources/stock_prices.csv")
        self.data['Date'] = pd.to_datetime(self.data['Date'], format='%d/%m/%Y').dt.date
        self.timeframe = self.data['Date']
        self.data = self.data.set_index('Date')
        self.idxdf=None


    def calc_index_level(self, start_date: dt.date, end_date: dt.date):
        # setting up a empty index list to store calculated index value
        idxlvl = [100]
        for i in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
            # finding the last business day of the preceding month
            lstbusD = i.date()-dt.timedelta(1)
            while lstbusD.weekday() > 4:
                lstbusD = lstbusD-dt.timedelta(1)
            # selecting last business day data
            lstdata = self.data.loc[lstbusD]
            # finding the three indicator stocks based on market cap of preceding month
            indic = lstdata.nlargest(3) 
            # setting the start time with this month first business day
            startD = i.date()
            # skip the weekend
            while startD.weekday() > 4:
                startD = startD+dt.timedelta(1)
            # setting the end time with next month first business day
            endD = i.date()+relativedelta(months=1)
            # skip the weekend
            while endD.weekday() > 4:
                endD = endD+dt.timedelta(1)
            # select the month data based on previous 3 stocks
            month = self.data.loc[startD:endD, [indic.index[0], indic.index[1], indic.index[2]]]
            # setting the index base for the month
            fst = month.iloc[0,0]
            snd = month.iloc[0,1]
            trd = month.iloc[0,2]
            # calculate the index for the month
            mtnidx = []
            for j in range(1, len(month)):
                idx = (month.iloc[j,0]/fst*0.5 + (month.iloc[j,1]/snd + month.iloc[j,2]/trd)*0.25)
                mtnidx.append(idx) 
            mtnidx = [ x * idxlvl[-1] for x in mtnidx]
            idxlvl = idxlvl + mtnidx
        
        timeframe = self.timeframe[(self.timeframe >= start_date) & (self.timeframe <= end_date)].reset_index()
        idxdf = pd.DataFrame(idxlvl, columns=['index_level'])
        idxdf['Date'] = timeframe['Date']
        idxdf = idxdf.set_index('Date')
        self.idxdf=idxdf

        

    def export_values(self, file_name: str):
        index_value = self.idxdf
        index_value.to_csv(file_name)
        
