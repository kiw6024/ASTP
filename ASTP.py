# 한투
import mojito

# 시간
import datetime
from pytz import timezone

# 크롤링
import requests
from bs4 import BeautifulSoup

# 주식데이터 불러오기
import yfinance as yf

# 엑셀 읽기 & 쓰기
import FinanceDataReader as fdr
import pandas as pd
import re




### 변수 선언란

# 크롤링
response = requests.get('https://finance.yahoo.com/quote/%5ENDX/')

# 기초 계좌정보 연결
mock_acc = open("C:\ASTP\python\mock.key")   # real_acc = open("real.key", 'r')  # 실제 계좌
lines = mock_acc.readlines()
key    = lines[0].strip()
secret = lines[1].strip()
acc_no = lines[2].strip()                                                        # 모의 계좌

# 상위 10개 기업 리스트
top10_stock_list = []

# 액셀 읽기
df_ndf_data = pd.read_excel('C:\\ASTP\\python\\ndq_data.xlsx')
buis_day = 20                                                                    # 20 영업일





### 함수 작성란

# 미국 시간
class time_US:

    # 기초정보고시용
    def guide_form():

        cur_time_US_raw = datetime.datetime.now(timezone('America/New_York'))
        cur_time_US_formed = cur_time_US_raw.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
        return cur_time_US_formed

    # 엑셀 입력용
    def cell_form():

        cur_time_US_raw = datetime.datetime.now(timezone('America/New_York'))
        cur_time_US_formed = cur_time_US_raw.strftime("%Y.%m.%d %H:%M:%S")
        return cur_time_US_formed


# NDX 크롤링
def get_ndx():

    if response.status_code == 200:
    
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # HTML 태그 내 클래스명으로 검색, 텍스트 추출
        ndx_class = soup.find(class_ = 'Fw(b) Fz(36px) Mb(-4px) D(ib)')
        ndx = re.sub(r'[^0-9]', '', ndx_class.get_text())                        # 문자열에서 특수문자 제거

    else :
        print(response.status_code)
    
    return ndx                                                                   # 리턴값 형식은 str


# 기초정보고시
def get_info():

    bullet = broker.fetch_present_balance()       

    print("\n\n\n"
        + "######################################################################\n"
        + "########################## -프로그램 시작- ###########################\n"
        + "######################################################################\n"
        + "\n"
        + "현재 나스닥-100 지수는 " + get_ndx() + "이며, \n"
        + "미국 뉴욕 현지 시간은 " + time_US.guide_form() + " 입니다. \n"
        + "총자산평가 수치는 다음과 같습니다 : " + bullet['output3']['tot_asst_amt'] + "."
    )


# 나스닥 엑셀 40칸 공백 확인
def if_all_filled():

    all_filled = True

    if len(df_ndf_data) < buis_day * 2:                                          # 하루 장 시작, 종료 시점에 "두 번씩" NDX지수를 입력받는다.
        all_filled = False

    return all_filled


# NDX 엑셀 입력
def write_ndq_data():

    if if_all_filled() == False:                                                 # 40칸이 다 채워지지 않았을 시
        df_ndf_data.loc[len(df_ndf_data)] = {'date'      : time_US.cell_form(),  # 데이터 입력
                                             'ndx_index' : get_ndx()}

        df_ndf_data.to_excel('C:\\ASTP\\python\\ndq_data.xlsx',                  # 엑셀 입력
                          sheet_name = 'ndx_data_20bis_day',
                          index      = False)

    else:                                                                        # 40칸이 다 채워져있을 시
        for row in range(buis_day * 2 - 1):
            df_ndf_data.loc[row] = df_ndf_data.loc[row + 1]                      # 40번째 이전 행 앞으로 이동

        df_ndf_data.loc[buis_day * 2 - 1] = {'date'      : time_US.cell_form(),  # 40번째 행 입력
                                             'ndx_index' : get_ndx()}
        
        df_ndf_data.to_excel('C:\\ASTP\\python\\ndq_data.xlsx',                  # 엑셀 입력
                          sheet_name = 'ndx_data_20bis_day',
                          index      = False)


# NDX -3% 여부 확인
def ndx_collapsed():

    df_ndf_data['ndx_index'] = df_ndf_data['ndx_index'].astype(float)            # 엑셀값 문자열에서 실수로 변경
    ndx_decrse_3per = False

    ndx_max = df_ndf_data['ndx_index'].max()
    ndx_min = df_ndf_data['ndx_index'].min()

    if 100 * (ndx_max - ndx_min) / ndx_max > 3:
        ndx_decrse_3per = True
        print("\nNDX 수치의 변동이 심합니다.\n")
    else:
        print("\nNDX 수치는 안정적입니다.\n")

    return ndx_decrse_3per


# 나스닥 상위 10개 기업 리스트 생성
def top10_stock_list_maker():

    # FinanceDataReader, 거래소 + 시총 상위 10위 기업
    df_nsq = fdr.StockListing('NASDAQ')

    for i in range(10):
        top10_stock_list.append(df_nsq.iloc[i, 0]) # 행, 열


# 매수종목선정함수
def stock_selector():

    fstock = yf.Ticker(top10_stock_list[0]).info["marketCap"]                   # 시가총액 1위
    sstock = yf.Ticker(top10_stock_list[1]).info["marketCap"]                   # 시가총액 2위

    if (sstock - fstock) * 100 / sstock > 10:                                   # 1,2위 기업간 시총이 10% 이상 차이날 때
        divrs_invst = False                                                     # diversified investment, 분산 투자
    else:
        divrs_invst = True

    print("\n"
    + "나스닥 시가총액 1위 기업코드는 " + top10_stock_list[0] + ",\n"
    + "나스닥 시가총액 2위 기업코드는 " + top10_stock_list[1] + "입니다.\n"
    )
    
    return divrs_invst


# 주문함수
def stock_buying(symbol_input, price_input):

    resp = broker.create_limit_buy_order(
        symbol   = symbol_input,
        price    = price_input,
        quantity = 1
    )
    print(resp['msg1'])


# 조건부종목주문함수
def if_buy_divrs(divrs_invst):

    info_fstock = broker.fetch_price(top10_stock_list[0])                       # 시총 1위 기업정보
    info_sstock = broker.fetch_price(top10_stock_list[1])                       # 시총 2위 기업정보

    if divrs_invst == True:                                                     # 두 기업의 시가총액이 10% 이상 차이난다면
        print(top10_stock_list[0] + "와 "
            + top10_stock_list[1] + "에는 시가총액상의 큰 차이가 없습니다.\n"
            + top10_stock_list[0] + "의 2주치 매수주문을 올립니다.\n")
        stock_buying(top10_stock_list[0], info_fstock['output']['last'])        # 1위 기업만 매수
        stock_buying(top10_stock_list[0], info_fstock['output']['last'])

    elif divrs_invst == False:                                                  # 그렇지 않은 경우
        print(top10_stock_list[0] + "와"
            + top10_stock_list[1] + "는 시가총액상 큰 차이를 보이고 있습니다.\n"
            + "각각 1주치의 매수주문을 분산하여 올립니다.\n")
        stock_buying(top10_stock_list[0], info_fstock['output']['last'])        # 1, 2위 기업을 분산 매수
        stock_buying(top10_stock_list[1], info_sstock['output']['last'])


# 공황상황대응함수
def crisis_activated():
    print("임시 코드")





### 실질 코드란

if __name__=="__main__":

    # 증권사 객체 생성
    broker = mojito.KoreaInvestment(
    api_key = key,
    api_secret = secret,
    acc_no = acc_no,
    exchange = '나스닥',
    mock = True                                                             # 모의투자 여부
    )

    # 자산고지
    get_info()

    while ndx_collapsed() == False:

        # NDX지수 입력
        write_ndq_data()

        # 상위 10개 기업 산출
        top10_stock_list_maker()

        # 매수종목선정함수 및 매수
        if_buy_divrs(stock_selector())
    
    print("코드를 종료합니다.")





''' 메모



# base	전일종가
# pvol	전일 거래량
# last	당일 조회시점의 현재가격
# tvol	당일 조회시점까지의 전체 거래량
# tamt	당일 조회시점까지의 전체 거래금액



# 데이터프레임 접근
dataframe.iloc[i, 0]와 같이 행, 열 순이다.



'''