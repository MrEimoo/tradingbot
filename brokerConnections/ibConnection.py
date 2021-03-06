#!/usr/bin/env python
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, message
from .brokerConnection import BrokerConnection
from time import sleep

class IBConnection(BrokerConnection):

    def __init__(self):
        self.name = "Interactive Broker Connection"

    def error_handler(self, msg):
        """Handles the capturing of error messages"""
        print ("Server Error: %s" % msg)

    def reply_handler(self, msg):
        """Han(dles of server replies"""
        print ("Server Response: %s, %s" % (msg.typeName, msg))

    def create_contract(self, symbol, sec_type, exch, prim_exch, curr):
        """Create a Contract object defining what will
        be purchased, at which exchange and in which currency.

        symbol - The ticker symbol for the contract
        sec_type - The security type for the contract ('STK' is 'stock')
        exch - The exchange to carry out the contract on
        prim_exch - The primary exchange to carry out the contract on
        curr - The currency in which to purchase the contract"""
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = sec_type
        contract.m_exchange = exch
        contract.m_primaryExch = prim_exch
        contract.m_currency = curr
        return contract

    def create_order(self, order_type, quantity, action):
        """Create an Order object (Market/Limit) to go long/short.

        order_type - 'MKT', 'LMT' for Market or Limit orders
        quantity - Integral number of assets to order
        action - 'BUY' or 'SELL'"""
        order = Order()
        order.m_orderType = order_type
        order.m_totalQuantity = quantity
        order.m_action = action
        return order

    def order(self, ticker, action, shares, exchange=None, curr="USD"):
        # Connect to the Trader Workstation (TWS) running on the
        # usual port of 7496, with a clientId of 100
        # (The clientId is chosen by us and we will need 
        # separate IDs for both the execution connection and
        # market data connection)
        tws_conn = Connection.create("127.0.0.1", port=7499, clientId=420)
        tws_conn.connect()

        # Assign the error handling function defined above
        # to the TWS connection

        tws_conn.register(self.error_handler, 'Error')

        # Assign all of the server reply messages to the
        # reply_handler function defined above
      
        tws_conn.registerAll(self.reply_handler)

        # Create an order ID which is 'global' for this session. This
        # will need incrementing once new orders are submitted.
        order_id = 3

        if exchange is None:
            exchange = "SMART"
        # Create a contract in GOOG stock via SMART order routing
        contract = self.create_contract(ticker, 'STK', exchange, exchange, curr)

        # Go long 100 shares of Google
        order = self.create_order('MKT', shares, action)

        # Use the connection to the send the order to IB
        tws_conn.placeOrder(order_id, contract, order)    

        sleep(1)

        # Disconnect from TWS
        tws_conn.disconnect()