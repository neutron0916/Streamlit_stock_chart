import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

class stock:
    now = datetime.now()
    def __init__(self, stock_code, from_month) -> None:
        self.stock_code = stock_code
        self.from_month = from_month
        if self.now.month< from_month:
            self.start = datetime(self.now.year-1, self.from_month, 1)
        else:
            self.start = datetime(self.now.year, self.from_month, 1)

    def get_three_major(self): 
        """
        	日期	外資	投信	自營商	單日合計
        0	109/12/04	18731	77	-340	18468
        1	109/12/03	-4885	13	-57	-4929
        2	109/12/02	10469	106	-415	10160
        3	109/12/01	587	211	397	1195
        4	109/11/30	-33427	-42	1226	-32243
        
        """
        
        end = self.now
        time_format = "%Y-%m-%d"
        start_string = self.start.strftime(time_format)
        end_string = end.strftime(time_format)
        # 日盛證卷
        url = f'http://jsjustweb.jihsun.com.tw/z/zc/zcl/zcl.djhtm?a={self.stock_code}&d={end_string}&c={start_string}'
        df_orignal = pd.read_html(url)
        df_extracted = df_orignal[2][7:-1]
        
        #如果沒有資料回傳，則 回傳錯誤
        if len(df_extracted.index) < 2:
            raise Exception('No data retrun from this stock code')
        #設定df columns 不然都會是1.2.3......
        df_extracted.columns = df_orignal[2].iloc[6]
        df_extracted.columns.name = ''
        
        return df_extracted.reset_index(drop = True).iloc[:,:5]

    def get_price_value(self):
        """
        
        1	日期	開盤價	最高價	最低價	收盤價	成交量
        0	109/06/30	313.50	314.00	311.00	313.00	48784
        1	109/06/29	314.00	315.00	310.00	312.00	56455
        2	109/06/24	319.00	320.00	316.00	317.50	54019
        3	109/06/23	316.00	316.50	312.50	315.00	41183
        4	109/06/22	314.50	316.50	312.00	312.00	37295
        
        
        """
        data_list = []
        query_time = self.start
        while (query_time<self.now):
            #聚財網
            url = f'https://stock.wearn.com/cdata.asp?Year={query_time.year-1911}&month={query_time.month:0>2d}&kind={self.stock_code}'
            df_orignal =  pd.read_html(url)
            df_extracted = df_orignal[0][2:]
            df_extracted.columns = df_orignal[0].iloc[1]
            data_list.append(df_extracted)
            query_time += relativedelta(months = +1)
        data_final = pd.concat(data_list).drop_duplicates().reset_index(drop = True)
        data_final.columns.name = ''
        return data_final

    def get_all_data(self, enable_color = True):
        """
        	日期	外資	投信	自營商	單日合計	開盤價	最高價	最低價	收盤價	成交量
        0	109/12/04	18731	77	-340	18468	498.50	505.00	497.50	503.00	50920
        1	109/12/03	-4885	13	-57	-4929	499.50	499.50	495.00	497.00	35557
        2	109/12/02	10469	106	-415	10160	499.50	500.00	493.50	499.00	50422
        3	109/12/01	587	211	397	1195	489.50	490.00	483.50	490.00	36915
        """
        data1 = self.get_three_major()
        data2 = self.get_price_value()
        data = data1.merge(data2, left_on = '日期', right_on = '日期')

        # 將日期109/11/1 轉換 至2020/11/1...
        data['日期'] = data['日期'].apply(lambda x: f'{int((x :=x.split("/"))[0])+1911}/{x[1]}/{x[2]}')
        
       

        # 屬性轉換 --> 將其餘資料轉至 number
        for i in data.columns:
            data[i] = pd.to_numeric(data[i], errors='ignore')

        # 屬性轉換 --> 將日期從object to datetime
        data['日期'] = data['日期'].astype('datetime64[ns]')
        
        if enable_color:
            data['外資買賣顏色'] = data['外資'].apply(lambda x : '#FF0000' if x>0 else '#008E09' )
            data['投信買賣顏色'] =  data['投信'].apply(lambda x : '#FF0000' if x>0 else '#008E09' )
            data['自營商買賣顏色'] =  data['自營商'].apply(lambda x : '#FF0000' if x>0 else '#008E09' )
            data['收盤價買賣顏色'] =  (data['收盤價']-data['開盤價']).apply(lambda x : '#FF0000' if x>0 else '#008E09' )
            data['成交量買賣顏色'] =  (data['收盤價']-data['開盤價']).apply(lambda x : '#FF0000' if x>0 else '#008E09' )
        
        return data

        

        
        



