import backtrader as bt
import datetime as dt
import csv


class BitcoinFeed(bt.feeds.GenericCSVData):
    params = (('high', 1),('low',1),('close',1),('volume', 2),('openinterest',-1))

    def _loadline(self, linetokens):
        dtfield = linetokens[self.p.datetime]
        dtime = dt.datetime.utcfromtimestamp(int(dtfield))
        linetokens[self.p.datetime] = dtime.strftime(self.p.dtformat)
        return super()._loadline(linetokens)


class BitcoinResampler(bt.Strategy):
    params = (("csv", None),)

    def __init__(self):
        self.BTC = self.datas[0]
        self.csv = self.params.csv

    def next(self):
        self.csv.writerow([self.BTC.datetime.datetime().strftime("%Y-%m-%d %H:%M:%S"), self.BTC.open[0], self.BTC.high[0], self.BTC.low[0], self.BTC.close[0], self.BTC.volume[0]])
        #print("%s %.12f %.12f %.12f %.12f %.12f" % (self.BTC.datetime.datetime(), self.BTC.open[0], self.BTC.high[0], self.BTC.low[0], self.BTC.close[0], self.BTC.volume[0]))


if __name__ == "__main__":

    mins = 15

    cerebro = bt.Cerebro()

    data = BitcoinFeed(
        name="BTC",
        dataname="krakenUSD.csv",
        dtformat='%Y-%m-%dT%H:%M:%S.%f',
        timeframe=bt.TimeFrame.Ticks,
        #fromdate=dt.datetime(2017, 1, 1),
        #todate=dt.datetime(2018, 1, 1),
        nullvalue=0.0
    )

    cerebro.resampledata(
        data,
        timeframe=bt.TimeFrame.Minutes,
        compression=mins,
        bar2edge=True,
        adjbartime=True,
        rightedge=True,
        boundoff=0
    )

    #cerebro.adddata(data)

    with open("krakenUSD_%sm.csv" % mins, "w") as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        cerebro.addstrategy(BitcoinResampler, csv=csvWriter)
        cerebro.run()