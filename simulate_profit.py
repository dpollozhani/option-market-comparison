import pandas as pd

class SimulateProfit:

    def __init__(self, option_price: int, no_of_options: int, subsidy: float, initial_stock_price: int, strike_price_factor: float = 1.25):
        self.option_price = option_price
        self.no_of_options = no_of_options
        self.gross_option_cost = option_price*no_of_options
        self.option_cost = self.gross_option_cost - self.gross_option_cost*subsidy*0.5 #assuming 50% taxable
        self.initial_stock_price = initial_stock_price
        self.strike_price_factor = strike_price_factor
        self.strike_price = self.strike_price_factor*self.initial_stock_price
        self.no_of_stocks = self.option_cost/self.initial_stock_price
        self.stock_cost_at_strike = self.strike_price*self.no_of_options

    def stock_price_ratio(self, stock_price):
        return round(100*(stock_price-self.initial_stock_price)/self.initial_stock_price, 1)

    @classmethod
    def to_table(self, columns, column_names):
        assert len(columns) == len(column_names), 'columns and column_names must match in length'
        column_list = list(zip(*columns))
        table = pd.DataFrame(column_list, columns=column_names)
        return table

class Market(SimulateProfit):
    
    def stock_value(self, stock_price):
        return self.no_of_stocks*stock_price
        
    def net_profit(self, stock_value):
        return stock_value-self.option_cost

class Options(SimulateProfit):
    
    def stock_value(self, stock_price):
        return self.no_of_options*stock_price

    def net_profit(self, stock_value):
        return stock_value-self.stock_cost_at_strike-self.option_cost