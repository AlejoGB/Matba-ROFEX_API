'''
reMarkets API 
INPUT:
    User
    Password
    Account
> Consulta LP segun símbolo
> Consulta BID según símbolo
> genera orden de compra
'''
import sys
import logging
import pyRofex
import argparse
import time

class reMarketsAPI:
    def __init__(self, date_symbol, remarkets_account, remarkets_user, remarkets_pass, verbose=True, timeout=10,*args, **kwargs):
        self.timeout=timeout
        self.date_symbol = date_symbol
        self.status = 'OK'
        self.verbose = verbose

        try:
            pyRofex.initialize(user=remarkets_user,
                       password=remarkets_pass,
                       account=remarkets_account,
                       environment=pyRofex.Environment.REMARKET)
        except Exception as e:
                self.print(remarkets_pass)
                self.print(remarkets_user)
                self.print(remarkets_account)
                self.print('Error de autentificación : {}'.format(e))
                self.status = 'ERROR'


    def print(self, string=''):
        if self.verbose:
            print(string)
        
            
    def get_last_price(self):
        try:
            lp = pyRofex.get_market_data(ticker=self.date_symbol,
                            entries=[pyRofex.MarketDataEntry.BIDS, pyRofex.MarketDataEntry.LAST])
        except Exception as e:
            self.print('Error al buscar último precio : {}'.format(e))
        if lp['status']!='ERROR':
            self.print('Último precio operado: ${}'.format(str(round(lp["marketData"]["LA"]["price"],2)).replace('.',',')))
            return lp["marketData"]["LA"]["price"]
        elif lp['description'][-18:]=="ROFX doesn't exist":
            self.print('Símbolo inválido')
            return False
        else:
            # otro tipo de error
            self.print('Error al buscar último precio')
            return False


    def get_ingresar_orden(self, buy):
        cont = 0
        self.print('Consultando BID')
        try:
            md = pyRofex.get_market_data(ticker=self.date_symbol,
                            entries=[pyRofex.MarketDataEntry.BIDS])
        except Exception as e:
            self.print('Error al buscar BIDs : {}'.format(e))
            logging.error('Error al buscar BIDs : {}'.format(e))

        if md["marketData"]["BI"][0]["price"]:
            self.print('Precio de BID: ${}'.format(str(round(md["marketData"]["BI"][0]["price"], 2)).replace('.', ',')))
            entrada = round(float(md["marketData"]["BI"][0]["price"]) - 0.01, 2)
        else:
            self.print('No hay BIDs activos')
            entrada = float(buy)

        order = pyRofex.send_order(ticker=self.date_symbol,
                           side=pyRofex.Side.BUY,
                           size=1,
                           price=entrada,
                           order_type=pyRofex.OrderType.LIMIT)

        if order['status']=='ERROR':
            self.print('Error al realizar una órden: {}'.format(order['description']))
            return False

        order_status = pyRofex.get_order_status(order["order"]["clientId"])

        while True:
            if order_status["order"]['status']=='NEW':
                self.print('Ingresando orden a ${}'.format(entrada))
                return True
            else:
                # TODO: control de errores para otros posibles estados 
                time.sleep(1)
                cont +=1

            if cont==self.timeout:
                self.print('Orden cancelada por TIMEOUT')
                return False




        


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Consulta Remarkets last price + BID', usage='%(prog)s -u [username] -p [password]')

    parser.add_argument('date_symbol', nargs=1,
                              type=str,
                              help='date symbol')

    parser.add_argument('-u', nargs=1,
                             type=str,
                             help='username',
                             dest='user')

    parser.add_argument('-p', nargs=1,
                             type=str,
                             help='password',
                             dest='pw')

    parser.add_argument('-a', nargs=1,
                             type=str,
                             help='account',
                             dest='acc')
    print('Iniciando sesión en Remarkets')
    
    args = parser.parse_args()
    remarkets = reMarketsAPI(args.date_symbol[0], args.acc[0], args.user[0], args.pw[0])
    if remarkets.status=='ERROR':
        print('Cerrando sesión en Remarkets')
        sys.exit(0)

    print('Consultando símbolo')
    if remarkets.get_last_price():
        remarkets.get_ingresar_orden(75.84)

    print('Cerrando sesión en Remarkets')



