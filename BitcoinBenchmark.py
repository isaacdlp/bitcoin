import backtrader as bt
import datetime as dt

leverUp = True


''' Buy & Hold Bitcoin '''


class BitcoinFeed(bt.feeds.GenericCSVData):
    params = (('openinterest',-1),)


class BitcoinStrategy(bt.Strategy):

    def __init__(self):
        self.BTC = self.datas[0]
        self.last_id = 0
        super().__init__()

    def get_id(self):
        self.last_id += 1
        return self.last_id

    def log(self, txt, dt=None):
        dt = dt or self.BTC.datetime.datetime()
        print('%s %s' % (dt.isoformat(), txt))

    def do_exit(self, asset, short=False):
        if self.getposition(asset).size != 0.0:
            trade_id = self.get_id()
            if short:
                self.buy(asset, tradeid=trade_id, exectype=bt.Order.Market)
            else:
                self.sell(asset, tradeid=trade_id, exectype=bt.Order.Market)
            self.log("Order %s Exit %s %s" % (trade_id, "Short" if short else "Long", asset._name))

    def do_enter(self, asset, short=False):
        if self.getposition(asset).size == 0.0:
            trade_id = self.get_id()
            if short:
                self.sell(asset, tradeid=trade_id, exectype=bt.Order.Market)
            else:
                self.buy(asset, tradeid=trade_id, exectype=bt.Order.Market)
            self.log("Order %s Enter %s %s" % (trade_id, "Short" if short else "Long", asset._name))

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        self.log("Order %s %s Size %i Price: %.2f, Cost: %.2f, Comm %.2f" % (
        order.tradeid, order.Status[order.status], order.size, order.executed.price, order.executed.value,
        order.executed.comm))

    def next(self):
        if len(self.broker.get_orders_open()) == 0.0 and self.getposition(self.BTC).size == 0.0:
            self.do_enter(self.BTC)


if __name__ == "__main__":

    leverage = 2 if leverUp else 1
    percents = 195 if leverUp else 95

    cerebro = bt.Cerebro()

    data = BitcoinFeed(
        name="BTC",
        dataname="krakenUSD_15m.csv",
        timeframe=bt.TimeFrame.Minutes,
        fromdate=dt.datetime(2017, 1, 1),
        todate=dt.datetime(2018, 1, 1),
        nullvalue=0.0
    )

    cerebro.adddata(data)

    cerebro.addstrategy(BitcoinStrategy)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=percents) # taking leverage

    broker = cerebro.getbroker()
    broker.setcash(1000)

    broker.setcommission(commission=0.003, leverage=leverage, name="BTC") # allowing leverage
    broker.set_filler(bt.broker.filler.FixedBarPerc(perc=25))


    print("Start value %.4f" % broker.getvalue())

    cerebro.run()

    print("End value %.4f" % broker.getvalue())

    cerebro.plot()