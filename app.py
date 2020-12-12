import streamlit as st
import plotly.graph_objs as go
from stock import stock
from datetime import datetime
from plotly.subplots import make_subplots

#利用st.cache()快取沒有改變過的data
@st.cache()
# 爬蟲程式
def get_stock_data(stock_code, month):
    return stock(stock_code, month).get_all_data()


# ---------------------------------- sidebar --------------------------------- #



st.sidebar.header('Parameter setting')
stock_code = st.sidebar.text_input('pls input the stock code')
month = st.sidebar.number_input('from month...',
                                value=datetime.now().month - 3,
                                step=1,
                                max_value=12,
                                min_value=1)
data_colums = ['外資', '自營商', '投信', '成交量']
Bubble_info = st.sidebar.selectbox('Bubble_info', data_colums)
Bubble_size = st.sidebar.number_input('Bubble_size', step=1, value=10)
sub_info = st.sidebar.selectbox('Sub_info', data_colums)

# ----------------------------------- body ----------------------------------- #
st.image('./icon.png')
st.title('Stock chart')

# ----------------------------------- plot ----------------------------------- #

if stock_code and month:
    data = get_stock_data(stock_code, month)
    st.dataframe(data)
    st.success('Load data success !')

    if Bubble_info != '成交量':
        trace1 = go.Scatter(
            x=data['日期'],
            y=data['收盤價'],
            mode='lines+markers',
            marker=dict(size=data[f'{Bubble_info}'].abs(),
                        sizeref=data[f'{Bubble_info}'].abs().mean() /
                        Bubble_size,
                        color=data[f'{Bubble_info}買賣顏色']),
            line =dict(dash= 'dot'),
            hovertemplate="<b>日期%{x}</b><br> 收盤價 %{y} " + f"{Bubble_info} :" +
            "%{marker.size}<br>",
            name='收盤價')
    else:
        trace1 = go.Scatter(x=data['日期'],
                            y=data['收盤價'],
                            mode='lines+markers',
                            marker=dict(
                                size=data[f'{Bubble_info}'].abs(),
                                sizeref=data[f'{Bubble_info}'].abs().mean() /
                                Bubble_size,
                            ),
                            line =dict(dash= 'dot'),
                             hovertemplate="<b>日期%{x}</b><br> 收盤價 %{y}",
                            name='收盤價')



    trace2 = go.Bar(x=data['日期'],
                    y=data[f'{sub_info}'],
                    name=f'{sub_info}',
                    marker_color=data[f'{sub_info}買賣顏色'])

    fig = make_subplots(rows=2,
                        cols=1,
                        shared_xaxes=True,
                        row_heights=[0.7, 0.3])
    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=2, col=1)

    fig.update_layout(title=f'{stock_code}_chart', template='plotly_dark')

    st.plotly_chart(fig)


