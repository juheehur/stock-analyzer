import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd

# Page configuration
st.set_page_config(page_title="주식 데이터 분석기", layout="wide")

# Sidebar - 수익률 계산기
with st.sidebar:
    st.header("💰 수익률 계산기")
    
    calc_ticker = st.text_input(
        "종목 코드",
        value="005930.KS",
        help="예: 005930.KS (삼성전자), AAPL (애플)",
        key="calc_ticker"
    )
    
    purchase_date = st.date_input(
        "매수 날짜",
        value=datetime.now().date() - timedelta(days=30),
        max_value=datetime.now().date(),
        key="purchase_date"
    )
    
    purchase_amount = st.number_input(
        "매수 금액 (원)",
        min_value=0.0,
        value=1000000.0,
        step=10000.0,
        format="%.0f",
        key="purchase_amount"
    )
    
    if st.button("계산하기", type="primary", key="calc_button"):
        if calc_ticker and purchase_amount > 0:
            try:
                with st.spinner("계산 중..."):
                    ticker = yf.Ticker(calc_ticker)
                    info = ticker.info
                    company_name = info.get('longName', info.get('shortName', calc_ticker))
                    
                    # Get purchase date price
                    purchase_datetime = datetime.combine(purchase_date, datetime.min.time())
                    purchase_data = ticker.history(start=purchase_datetime, end=purchase_datetime + timedelta(days=1))
                    
                    if not purchase_data.empty:
                        purchase_price = purchase_data['Close'].iloc[0]
                        shares = purchase_amount / purchase_price
                        
                        # Get current price
                        current_data = ticker.history(period="1d")
                        if not current_data.empty:
                            current_price = current_data['Close'].iloc[-1]
                            current_value = shares * current_price
                            profit_loss = current_value - purchase_amount
                            profit_rate = (profit_loss / purchase_amount) * 100
                            
                            # Display results
                            st.divider()
                            st.subheader("📊 계산 결과")
                            
                            st.write(f"**회사명:** {company_name}")
                            st.write(f"**매수 가격:** {purchase_price:,.2f}원")
                            st.write(f"**매수 주식 수:** {shares:.4f}주")
                            st.write(f"**현재 가격:** {current_price:,.2f}원")
                            
                            # Current value and profit/loss with color
                            if profit_loss >= 0:
                                st.metric(
                                    "현재 가치",
                                    f"{current_value:,.0f}원",
                                    delta=f"{profit_loss:,.0f}원 ({profit_rate:+.2f}%)",
                                    delta_color="normal"
                                )
                            else:
                                st.metric(
                                    "현재 가치",
                                    f"{current_value:,.0f}원",
                                    delta=f"{profit_loss:,.0f}원 ({profit_rate:+.2f}%)",
                                    delta_color="inverse"
                                )
                            
                            # Additional info
                            st.divider()
                            st.caption(f"매수일: {purchase_date.strftime('%Y-%m-%d')}")
                            st.caption(f"계산일: {datetime.now().strftime('%Y-%m-%d')}")
                        else:
                            st.error("현재 가격을 가져올 수 없습니다.")
                    else:
                        st.error("매수 날짜의 데이터를 가져올 수 없습니다. 날짜를 확인해주세요.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
        else:
            st.warning("종목 코드와 매수 금액을 입력해주세요.")

# Title
st.title("주식 데이터 분석기")

# Input section
col1, col2 = st.columns(2)

with col1:
    ticker_symbol = st.text_input(
        "종목 코드",
        value="005930.KS",
        help="예: 005930.KS (삼성전자), AAPL (애플)"
    )

with col2:
    period_options = {
        "1개월": 30,
        "3개월": 90,
        "6개월": 180,
        "1년": 365
    }
    selected_period = st.selectbox(
        "기간 선택",
        options=list(period_options.keys()),
        index=0
    )

# Query button
if st.button("데이터 조회", type="primary"):
    if ticker_symbol:
        try:
            with st.spinner("데이터를 가져오는 중..."):
                # Get ticker data
                ticker = yf.Ticker(ticker_symbol)
                
                # Get company info
                info = ticker.info
                company_name = info.get('longName', info.get('shortName', 'N/A'))
                
                # Calculate date range
                days = period_options[selected_period]
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Get historical data
                historical_data = ticker.history(start=start_date, end=end_date)
                
                if not historical_data.empty:
                    # Calculate moving averages
                    historical_data['MA20'] = historical_data['Close'].rolling(window=20).mean()
                    historical_data['MA60'] = historical_data['Close'].rolling(window=60).mean()
                    # Display success message
                    st.success(f"✅ 데이터 조회 완료!")
                    st.info(f"**회사명:** {company_name}")
                    
                    # Display data preview
                    st.subheader("데이터 미리보기")
                    st.dataframe(historical_data.head(10), use_container_width=True)
                    
                    # Display basic statistics
                    st.subheader("기본 통계")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("시가", f"{historical_data['Open'].iloc[-1]:,.2f}")
                    with col2:
                        st.metric("고가", f"{historical_data['High'].max():,.2f}")
                    with col3:
                        st.metric("저가", f"{historical_data['Low'].min():,.2f}")
                    with col4:
                        st.metric("종가", f"{historical_data['Close'].iloc[-1]:,.2f}")
                    
                    # Display price charts in tabs
                    st.subheader("주가 차트")
                    tab1, tab2 = st.tabs(["선 차트", "캔들스틱"])
                    
                    with tab1:
                        # Moving average checkboxes
                        col_ma1, col_ma2 = st.columns(2)
                        with col_ma1:
                            show_ma20 = st.checkbox("20일 이동평균선", value=True, key="ma20_line")
                        with col_ma2:
                            show_ma60 = st.checkbox("60일 이동평균선", value=True, key="ma60_line")
                        
                        # Line chart
                        fig_line = go.Figure()
                        fig_line.add_trace(go.Scatter(
                            x=historical_data.index,
                            y=historical_data['Close'],
                            mode='lines',
                            name='종가',
                            hovertemplate='<b>날짜:</b> %{x}<br><b>가격:</b> %{y:,.2f}<extra></extra>',
                            line=dict(color='#1f77b4', width=2)
                        ))
                        
                        # Add moving averages if checked
                        if show_ma20:
                            fig_line.add_trace(go.Scatter(
                                x=historical_data.index,
                                y=historical_data['MA20'],
                                mode='lines',
                                name='MA20',
                                hovertemplate='<b>날짜:</b> %{x}<br><b>20일 이동평균:</b> %{y:,.2f}<extra></extra>',
                                line=dict(color='orange', width=2, dash='dash')
                            ))
                        
                        if show_ma60:
                            fig_line.add_trace(go.Scatter(
                                x=historical_data.index,
                                y=historical_data['MA60'],
                                mode='lines',
                                name='MA60',
                                hovertemplate='<b>날짜:</b> %{x}<br><b>60일 이동평균:</b> %{y:,.2f}<extra></extra>',
                                line=dict(color='green', width=2, dash='dash')
                            ))
                        
                        fig_line.update_layout(
                            title=f"{company_name} 주가 추이",
                            xaxis_title="날짜",
                            yaxis_title="가격",
                            height=500,
                            hovermode='x unified',
                            template='plotly_white',
                            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
                            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
                        )
                        st.plotly_chart(fig_line, use_container_width=True)
                    
                    with tab2:
                        # Moving average checkboxes
                        col_ma1, col_ma2 = st.columns(2)
                        with col_ma1:
                            show_ma20_candle = st.checkbox("20일 이동평균선", value=True, key="ma20_candle")
                        with col_ma2:
                            show_ma60_candle = st.checkbox("60일 이동평균선", value=True, key="ma60_candle")
                        
                        # Create subplots with shared x-axis
                        fig_candle = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.03,
                            row_heights=[0.7, 0.3],
                            subplot_titles=(f"{company_name} 캔들스틱 차트", "거래량")
                        )
                        
                        # Candlestick chart
                        fig_candle.add_trace(
                            go.Candlestick(
                                x=historical_data.index,
                                open=historical_data['Open'],
                                high=historical_data['High'],
                                low=historical_data['Low'],
                                close=historical_data['Close'],
                                increasing_line_color='blue',
                                decreasing_line_color='red',
                                increasing_fillcolor='blue',
                                decreasing_fillcolor='red',
                                name='주가'
                            ),
                            row=1, col=1
                        )
                        
                        # Add moving averages if checked
                        if show_ma20_candle:
                            fig_candle.add_trace(
                                go.Scatter(
                                    x=historical_data.index,
                                    y=historical_data['MA20'],
                                    mode='lines',
                                    name='MA20',
                                    hovertemplate='<b>날짜:</b> %{x}<br><b>20일 이동평균:</b> %{y:,.2f}<extra></extra>',
                                    line=dict(color='orange', width=2, dash='dash')
                                ),
                                row=1, col=1
                            )
                        
                        if show_ma60_candle:
                            fig_candle.add_trace(
                                go.Scatter(
                                    x=historical_data.index,
                                    y=historical_data['MA60'],
                                    mode='lines',
                                    name='MA60',
                                    hovertemplate='<b>날짜:</b> %{x}<br><b>60일 이동평균:</b> %{y:,.2f}<extra></extra>',
                                    line=dict(color='green', width=2, dash='dash')
                                ),
                                row=1, col=1
                            )
                        
                        # Volume bar chart
                        volume_avg = historical_data['Volume'].mean()
                        colors = ['rgba(0, 100, 200, 0.8)' if vol > volume_avg else 'rgba(0, 100, 200, 0.4)' 
                                 for vol in historical_data['Volume']]
                        
                        fig_candle.add_trace(
                            go.Bar(
                                x=historical_data.index,
                                y=historical_data['Volume'],
                                name='거래량',
                                marker_color=colors,
                                hovertemplate='<b>날짜:</b> %{x}<br><b>거래량:</b> %{y:,.0f}<extra></extra>'
                            ),
                            row=2, col=1
                        )
                        
                        # Update layout
                        fig_candle.update_layout(
                            height=700,
                            hovermode='x unified',
                            template='plotly_white',
                            showlegend=True,
                            xaxis_rangeslider_visible=False
                        )
                        
                        # Update axes
                        fig_candle.update_xaxes(
                            showgrid=True, 
                            gridwidth=1, 
                            gridcolor='lightgray',
                            row=2, col=1
                        )
                        fig_candle.update_yaxes(
                            title_text="가격",
                            showgrid=True, 
                            gridwidth=1, 
                            gridcolor='lightgray',
                            row=1, col=1
                        )
                        fig_candle.update_yaxes(
                            title_text="거래량",
                            showgrid=True, 
                            gridwidth=1, 
                            gridcolor='lightgray',
                            row=2, col=1
                        )
                        
                        st.plotly_chart(fig_candle, use_container_width=True)
                else:
                    st.error("데이터를 가져올 수 없습니다. 종목 코드를 확인해주세요.")
                    
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("종목 코드 형식을 확인해주세요. (예: 005930.KS, AAPL)")
    else:
        st.warning("종목 코드를 입력해주세요.")

# 종목 비교 섹션
st.divider()
st.subheader("종목 비교")

compare_tickers = st.text_input(
    "종목 코드 (쉼표로 구분)",
    value="005930.KS, 000660.KS",
    help="예: 005930.KS, 000660.KS, AAPL"
)

compare_period_options = {
    "1개월": 30,
    "3개월": 90,
    "6개월": 180,
    "1년": 365
}
compare_period = st.selectbox(
    "기간 선택",
    options=list(compare_period_options.keys()),
    index=0,
    key="compare_period"
)

if st.button("종목 비교", type="primary", key="compare_button"):
    if compare_tickers:
        try:
            with st.spinner("데이터를 가져오는 중..."):
                # Parse ticker symbols
                ticker_list = [t.strip() for t in compare_tickers.split(',') if t.strip()]
                
                if len(ticker_list) == 0:
                    st.warning("종목 코드를 입력해주세요.")
                else:
                    # Calculate date range
                    days = compare_period_options[compare_period]
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days)
                    
                    # Color palette for different stocks
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                    
                    # Store normalized data
                    normalized_data = {}
                    company_names = {}
                    
                    # Fetch data for each ticker
                    for idx, ticker_symbol in enumerate(ticker_list):
                        try:
                            ticker = yf.Ticker(ticker_symbol)
                            info = ticker.info
                            company_name = info.get('longName', info.get('shortName', ticker_symbol))
                            company_names[ticker_symbol] = company_name
                            
                            # Get historical data
                            data = ticker.history(start=start_date, end=end_date)
                            
                            if not data.empty and len(data) > 0:
                                # Normalize to starting price (100% = starting price)
                                first_close = data['Close'].iloc[0]
                                normalized_close = (data['Close'] / first_close) * 100
                                normalized_data[ticker_symbol] = {
                                    'dates': data.index,
                                    'normalized': normalized_close,
                                    'color': colors[idx % len(colors)]
                                }
                        except Exception as e:
                            st.warning(f"{ticker_symbol} 데이터를 가져오는 중 오류 발생: {str(e)}")
                    
                    if normalized_data:
                        # Create comparison chart
                        fig_compare = go.Figure()
                        
                        for ticker_symbol, data_dict in normalized_data.items():
                            company_name = company_names.get(ticker_symbol, ticker_symbol)
                            fig_compare.add_trace(go.Scatter(
                                x=data_dict['dates'],
                                y=data_dict['normalized'],
                                mode='lines',
                                name=company_name,
                                hovertemplate=f'<b>{company_name}</b><br><b>날짜:</b> %{{x}}<br><b>수익률:</b> %{{y:.2f}}%<extra></extra>',
                                line=dict(color=data_dict['color'], width=2)
                            ))
                        
                        fig_compare.update_layout(
                            title="종목 비교 (시작일 기준 수익률)",
                            xaxis_title="날짜",
                            yaxis_title="수익률 (%)",
                            height=500,
                            hovermode='x unified',
                            template='plotly_white',
                            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
                            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
                            legend=dict(
                                yanchor="top",
                                y=0.99,
                                xanchor="left",
                                x=0.01
                            )
                        )
                        st.plotly_chart(fig_compare, use_container_width=True)
                        
                        # Display comparison summary
                        st.subheader("비교 요약")
                        summary_data = []
                        for ticker_symbol, data_dict in normalized_data.items():
                            company_name = company_names.get(ticker_symbol, ticker_symbol)
                            final_return = data_dict['normalized'].iloc[-1] - 100
                            summary_data.append({
                                '종목명': company_name,
                                '종목코드': ticker_symbol,
                                '수익률 (%)': f"{final_return:.2f}"
                            })
                        
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    else:
                        st.error("비교할 수 있는 데이터가 없습니다.")
                        
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("종목 코드 형식을 확인해주세요. (예: 005930.KS, 000660.KS)")
    else:
        st.warning("종목 코드를 입력해주세요.")
