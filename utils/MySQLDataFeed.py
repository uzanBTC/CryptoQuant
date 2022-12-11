import backtrader as bt
import pymysql


class MysqlData(bt.feeds.DataBase):
    '''
    table create statement

    CREATE TABLE `ethxxxx` (
        `date` date NOT NULL,
        `open` double NOT NULL,
        `high` double NOT NULL,
        `low` double NOT NULL,
        `close` double NOT NULL,
        `volume` bigint NOT NULL,
        PRIMARY KEY (`date`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

    feed = MysqlData(
        db='eth',
        dataname='ethxxxx',
        fromdate=datetime.date(2013,1,1),
        todate=datetime.date(2019,12,31),
    )
    '''

    def __init__(self, db, **kwargs):
        super(MysqlData, self).__init__(**kwargs)

        assert(self.p.fromdate is not None)
        assert(self.p.todate is not None)

        # name pf db
        self.db = db

        # iterator 4 data in the list
        self.iter = None
        self.data = None

    def start(self):
        if self.data is None:
            # connect to mysql db
            # hard coded bd config
            connection = pymysql.connect(host='localhost',
                                         port=3306,
                                         user='root',
                                         password='',
                                         db=self.db,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = 'SELECT * FROM `{:s}` WHERE data BETWEEN %s AND %s'.format(self.p.datename)
                cursor.execute(sql,(self.p.fromdate,self.p.todate))
                self.data = cursor.fetchall()
        finally:
            connection.close()

        self.iter = iter(self.data)

    def stop(self):
        pass

    def _load(self):
        if self.iter is None:
            # if no data ... no parsing
            return False

        try:
            row = next(self.iter)
        except StopIteration:
            return False

        self.lines.datetime[0] = self.date2num(row['date'])
        self.lines.open[0] = row['open']
        self.lines.high[0] = row['high']
        self.lines.low[0] = row['low']
        self.lines.close[0] =row['close']
        self.lines.volume[0] = row['volume']
        self.lines.openinterest[0] = -1

        return True