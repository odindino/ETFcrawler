# import requests
# from bs4 import BeautifulSoup
# import pandas as pd


# def get_etf_info(etf_code):
#     # 構建URL
#     url = f"https://www.moneydj.com/etf/x/basic/basic0004.xdjhtm?etfid={etf_code}"

#     # 發送GET請求
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
#     response = requests.get(url, headers=headers)
#     response.encoding = 'utf-8'

#     # 解析HTML
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # 找到資料表格
#     table = soup.find('table', {'id': 'sTable'})

#     # 創建一個字典來存儲提取的資訊
#     etf_info = {}

#     # 遍歷表格行提取資訊
#     for row in table.find_all('tr'):
#         cols = row.find_all(['th', 'td'])
#         if len(cols) >= 2:
#             key = cols[0].text.strip()
#             value = cols[1].text.strip()

#             # 針對有4列的行特殊處理
#             if len(cols) == 4:
#                 key2 = cols[2].text.strip()
#                 value2 = cols[3].text.strip()
#                 etf_info[key2] = value2

#             etf_info[key] = value

#     # 提取所需的特定欄位
#     result = {
#         'ETF名稱': etf_info.get('ETF名稱', ''),
#         '交易所代碼': etf_info.get('交易所代碼', ''),
#         '英文名稱': etf_info.get('英文名稱', ''),
#         '發行公司': etf_info.get('發行公司', ''),
#         '成立日期': etf_info.get('成立日期', '').split('（')[0],  # 只取日期部分
#         'ETF規模': etf_info.get('ETF規模', '').split('(')[0],  # 只取數值部分
#         '成交量': etf_info.get('成交量(股)', '').split('（')[0],  # 只取數值部分
#         'ETF市價': etf_info.get('ETF市價', ''),
#         'ETF淨值': etf_info.get('ETF淨值', ''),
#         '折溢價(%)': etf_info.get('折溢價(%)', '').split('(')[0],  # 只取當前值
#         '配息頻率': etf_info.get('配息頻率', ''),
#         '總管理費用(%)': etf_info.get('總管理費用(%)', '').split(' ')[0],  # 只取費用率
#         '殖利率(%)': etf_info.get('殖利率(%)', '').split('（')[0],  # 只取當前值
#         '年化標準差(%)': etf_info.get('年化標準差(%)', '').split('（')[0]  # 只取當前值
#     }

#     return result


# # 使用範例
# etf_code = "00770.TW"
# etf_data = get_etf_info(etf_code)

# # 轉換成DataFrame顯示
# df = pd.DataFrame([etf_data])
# print(df)

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd


# def get_holdings_by_region(soup):
#     """抓取依區域的持股分布"""
#     try:
#         # 找到區域分布的表格
#         region_table = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable'})
#         if not region_table:
#             return None

#         # 解析表格數據
#         data = []
#         for row in region_table.find_all('tr')[1:]:  # 跳過表頭
#             cols = row.find_all('td')
#             if len(cols) >= 4:
#                 data.append({
#                     '區域': cols[1].text.strip(),
#                     '投資金額(萬美元)': float(cols[2].text.strip().replace(',', '')),
#                     '比例(%)': float(cols[3].text.strip())
#                 })

#         return pd.DataFrame(data)
#     except Exception as e:
#         print(f"Error in get_holdings_by_region: {e}")
#         return None


# def get_holdings_by_sector(soup):
#     """抓取依產業的持股分布"""
#     try:
#         # 找到產業分布的表格
#         sector_table = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable2'})
#         if not sector_table:
#             return None

#         # 解析表格數據
#         data = []
#         for row in sector_table.find_all('tr')[1:]:  # 跳過表頭
#             cols = row.find_all('td')
#             if len(cols) >= 4:
#                 data.append({
#                     '產業': cols[1].text.strip(),
#                     '投資金額(萬美元)': float(cols[2].text.strip().replace(',', '')),
#                     '比例(%)': float(cols[3].text.strip())
#                 })

#         return pd.DataFrame(data)
#     except Exception as e:
#         print(f"Error in get_holdings_by_sector: {e}")
#         return None


# def get_top_holdings(soup):
#     """抓取主要持股明細"""
#     try:
#         # 找到持股明細的表格
#         holdings_table = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable3'})
#         if not holdings_table:
#             return None

#         # 解析表格數據
#         data = []
#         for row in holdings_table.find_all('tr')[1:]:  # 跳過表頭
#             cols = row.find_all('td')
#             if len(cols) >= 3:
#                 data.append({
#                     '個股名稱': cols[0].text.strip(),
#                     '投資比例(%)': float(cols[1].text.strip()),
#                     '持有股數': float(cols[2].text.strip().replace(',', ''))
#                 })

#         return pd.DataFrame(data)
#     except Exception as e:
#         print(f"Error in get_top_holdings: {e}")
#         return None


# def get_etf_holdings(etf_code):
#     """主函數：獲取ETF的全部持股資訊"""
#     # 構建URL
#     url = f"https://www.moneydj.com/ETF/X/Basic/Basic0007.xdjhtm?etfid={etf_code}"

#     # 發送GET請求
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
#     response = requests.get(url, headers=headers)
#     response.encoding = 'utf-8'

#     # 解析HTML
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # 獲取所有標題來確認有哪些資訊
#     titles = soup.find_all('div', {'class': 'eTitle'})
#     title_texts = [title.text.strip() for title in titles]

#     # 創建結果字典
#     result = {}

#     # 根據標題決定要抓取的資訊
#     for title in title_texts:
#         if '依區域' in title:
#             result['holdings_by_region'] = get_holdings_by_region(soup)
#         elif '依產業' in title:
#             result['holdings_by_sector'] = get_holdings_by_sector(soup)
#         elif '持股明細' in title:
#             result['top_holdings'] = get_top_holdings(soup)

#     return result


# # 使用範例
# if __name__ == "__main__":
#     etf_code = "VOO"
#     holdings_data = get_etf_holdings(etf_code)

#     # 顯示結果
#     for key, df in holdings_data.items():
#         if df is not None:
#             print(f"\n{key}:")
#             print(df)

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd


# def get_risk_metrics(soup):
#     """提取風險分析頁面的追蹤誤差和季均折溢價"""
#     try:
#         metrics = {}
#         table = soup.find('table', {'class': 'DataTable'})
#         if not table:
#             return None

#         rows = table.find_all('tr')
#         for row in rows[1:]:  # 跳過表頭
#             cols = row.find_all(['th', 'td'])
#             if len(cols) >= 3:
#                 metric_name = cols[0].text.strip()
#                 if metric_name == '追蹤誤差':
#                     metrics['tracking_error'] = float(cols[2].text.strip())
#                 elif metric_name == '季均折溢價':
#                     metrics['quarterly_premium_discount'] = float(
#                         cols[2].text.strip())

#         return metrics
#     except Exception as e:
#         print(f"Error in get_risk_metrics: {e}")
#         return None


# def get_return_comparison(soup):
#     """提取報酬比較頁面的報酬率比較表"""
#     try:
#         # 找到第一個表格 - 報酬率比較表
#         table1 = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable'})
#         if table1:
#             data1 = []
#             rows = table1.find_all('tr')
#             headers = [th.text.strip() for th in rows[0].find_all('th')]

#             for row in rows[1:]:
#                 cols = row.find_all(['th', 'td'])
#                 row_data = {
#                     '項目': cols[0].text.strip(),
#                     '年平均報酬率': float(cols[1].text.strip()),
#                     'Sharpe': float(cols[2].text.strip()),
#                     'Beta': float(cols[3].text.strip()),
#                     '標準差': float(cols[4].text.strip())
#                 }
#                 data1.append(row_data)

#         # 找到第二個表格 - 報酬率比較表(月份)
#         table2 = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable2'})
#         if table2:
#             data2 = []
#             rows = table2.find_all('tr')
#             headers = [th.text.strip() for th in rows[0].find_all('th')]

#             for row in rows[1:]:
#                 cols = row.find_all(['th', 'td'])
#                 if len(cols) >= 8:
#                     row_data = {
#                         '項目': cols[0].text.strip(),
#                         '今年起': float(cols[1].text.strip()),
#                         '一個月': float(cols[2].text.strip()),
#                         '三個月': float(cols[3].text.strip()),
#                         '六個月': float(cols[4].text.strip()),
#                         '一年': float(cols[5].text.strip()),
#                         '二年': float(cols[6].text.strip()),
#                         '三年': float(cols[7].text.strip())
#                     }
#                     data2.append(row_data)

#         return pd.DataFrame(data1), pd.DataFrame(data2)
#     except Exception as e:
#         print(f"Error in get_return_comparison: {e}")
#         return None, None


# def get_yearly_return_risk(soup):
#     """提取風險報酬頁面的年報酬率比較表"""
#     try:
#         table = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable'})
#         if not table:
#             return None

#         data = []
#         rows = table.find_all('tr')
#         headers = [th.text.strip() for th in rows[0].find_all('th')]

#         for row in rows[1:]:
#             cols = row.find_all(['th', 'td'])
#             if len(cols) >= 5:
#                 row_data = {
#                     '項目': cols[0].text.strip(),
#                     '2023': float(cols[1].text.strip()),
#                     '2022': float(cols[2].text.strip()),
#                     '2021': float(cols[3].text.strip()),
#                     '2020': float(cols[4].text.strip()),
#                     '2019': float(cols[5].text.strip())
#                 }
#                 data.append(row_data)

#         return pd.DataFrame(data)
#     except Exception as e:
#         print(f"Error in get_yearly_return_risk: {e}")
#         return None


# def get_return_analysis(soup):
#     """提取報酬分析頁面的市價、淨值報酬表格"""
#     try:
#         table = soup.find(
#             'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable'})
#         if not table:
#             return None

#         data = []
#         rows = table.find_all('tr')
#         headers = [th.text.strip() for th in rows[0].find_all('th')]

#         for row in rows[1:]:
#             cols = row.find_all(['th', 'td'])
#             if len(cols) >= 11:
#                 row_data = {
#                     '項目': cols[0].text.strip(),
#                     '一日': float(cols[1].text.strip()),
#                     '一週': float(cols[2].text.strip()),
#                     '一個月': float(cols[3].text.strip()),
#                     '三個月': float(cols[4].text.strip()),
#                     '六個月': float(cols[5].text.strip()),
#                     '一年': float(cols[6].text.strip()),
#                     '三年': float(cols[7].text.strip()),
#                     '五年': float(cols[8].text.strip()),
#                     '十年': float(cols[9].text.strip()),
#                     '成立日': float(cols[10].text.strip())
#                 }
#                 data.append(row_data)

#         return pd.DataFrame(data)
#     except Exception as e:
#         print(f"Error in get_return_analysis: {e}")
#         return None

# # 使用示例


# def get_etf_metrics(etf_code):
#     """主函數: 獲取ETF的各項指標"""
#     base_url = "https://www.moneydj.com/ETF/X/Basic/"
#     urls = {
#         'risk': f"{base_url}Basic0013.xdjhtm?etfid={etf_code}",
#         'return_comparison': f"{base_url}Basic0010.xdjhtm?etfid={etf_code}",
#         'return_risk': f"{base_url}Basic0011.xdjhtm?etfid={etf_code}",
#         'return_analysis': f"{base_url}Basic0008.xdjhtm?etfid={etf_code}"
#     }

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }

#     results = {}

#     for page_type, url in urls.items():
#         response = requests.get(url, headers=headers)
#         response.encoding = 'utf-8'
#         soup = BeautifulSoup(response.text, 'html.parser')

#         if page_type == 'risk':
#             results['risk_metrics'] = get_risk_metrics(soup)
#         elif page_type == 'return_comparison':
#             results['return_comparison'], results['monthly_return_comparison'] = get_return_comparison(
#                 soup)
#         elif page_type == 'return_risk':
#             results['yearly_return_risk'] = get_yearly_return_risk(soup)
#         elif page_type == 'return_analysis':
#             results['return_analysis'] = get_return_analysis(soup)

#     return results


# etf_code = "VT"
# results = get_etf_metrics(etf_code)

# # 查看各項結果
# print("風險指標:", results['risk_metrics'])
# print("\n報酬率比較表:")
# print(results['return_comparison'])
# print("\n月份報酬率比較表:")
# print(results['monthly_return_comparison'])
# print("\n年報酬率風險表:")
# print(results['yearly_return_risk'])
# print("\n報酬分析表:")
# print(results['return_analysis'])

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Tuple, Union
from datetime import datetime


class ETFScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_soup(self, url: str) -> BeautifulSoup:
        """獲取網頁內容並返回BeautifulSoup對象"""
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')

    def _parse_ranking(self, text: str) -> Tuple[int, int]:
        """解析排名字符串，返回(當前排名, 總數)"""
        if '/' in str(text):
            rank, total = map(int, text.split('/'))
            return rank, total
        return None, None

    def _parse_table_value(self, cell: str) -> float:
        """解析表格單元格中的數值"""
        try:
            # 移除所有空白字符
            value = str(cell).strip()
            if value == '':
                return None
            return float(value)
        except (ValueError, AttributeError):
            return None

    def _parse_percentage(self, text: str) -> float:
        """改進的百分比解析方法"""
        try:
            # 移除所有空白字符和百分號
            value = str(text).strip().replace('%', '').strip()
            if value == '':
                return None
            return float(value)
        except (ValueError, AttributeError):
            return None

    def get_return_trends(self, etf_code: str) -> Dict[str, pd.DataFrame]:
        """獲取報酬走勢數據"""
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0009.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        result = {}

        # 處理月報酬率表格
        monthly_table = soup.find('table', {'id': 'stable2'})
        if monthly_table:
            # 創建列表存儲數據
            data = []
            headers = []

            # 處理表頭
            header_rows = monthly_table.find_all('tr')[:2]
            year_headers = [th.text.strip()
                            for th in header_rows[0].find_all('th')[1:]]
            month_headers = [th.text.strip()
                             for th in header_rows[1].find_all('th')]

            # 處理數據行
            for row in monthly_table.find_all('tr')[2:]:
                row_data = []
                # 獲取指標名稱
                name = row.find('th').text.strip()
                # 獲取數據
                for td in row.find_all('td'):
                    value = self._parse_percentage(td.text)
                    row_data.append(value)
                data.append([name] + row_data)

            # 創建列名
            columns = ['指標'] + month_headers
            # 創建DataFrame
            df_monthly = pd.DataFrame(data, columns=columns)
            result['monthly_return'] = df_monthly

        # 處理季報酬率表格
        quarterly_table = soup.find('table', {'id': 'stable3'})
        if quarterly_table:
            data = []

            # 處理數據行
            for row in quarterly_table.find_all('tr')[2:]:
                row_data = []
                # 獲取指標名稱
                name = row.find('th').text.strip()
                # 獲取數據
                for td in row.find_all('td'):
                    value = self._parse_percentage(td.text)
                    row_data.append(value)
                data.append([name] + row_data)

            # 創建列名（可以從表格中提取，這裡簡化處理）
            columns = ['指標'] + [f'Q{i}' for i in range(1, len(row_data)+1)]
            # 創建DataFrame
            df_quarterly = pd.DataFrame(data, columns=columns)
            result['quarterly_return'] = df_quarterly

        # 處理年報酬率表格
        yearly_table = soup.find('table', {'id': 'stable'})
        if yearly_table:
            data = []

            # 處理數據行
            for row in yearly_table.find_all('tr')[1:]:  # 跳過表頭
                row_data = []
                # 獲取指標名稱
                name = row.find('th').text.strip()
                # 獲取數據
                for td in row.find_all('td'):
                    value = self._parse_percentage(td.text)
                    row_data.append(value)
                data.append([name] + row_data)

            # 提取年份作為列名
            year_headers = [th.text.strip() for th in yearly_table.find_all('tr')[
                0].find_all('th')[1:]]
            columns = ['指標'] + year_headers
            # 創建DataFrame
            df_yearly = pd.DataFrame(data, columns=columns)
            result['yearly_return'] = df_yearly

        return result

    def get_risk_analysis(self, etf_code: str) -> Dict:
        """獲取風險分析數據"""
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0013.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        # 尋找風險分析表格
        table = soup.find('table', {'class': 'DataTable'})
        if not table:
            return {}

        data = {}
        rows = table.find_all('tr')[1:]  # 跳過表頭

        for row in rows:
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 4:
                metric = cols[0].text.strip()
                date = cols[1].text.strip()
                value = self._parse_percentage(cols[2].text)
                rank, total = self._parse_ranking(cols[3].text)

                data[metric] = {
                    'date': datetime.strptime(date, '%Y/%m/%d').date(),
                    'value': value,
                    'rank': rank,
                    'total': total
                }

        return data

    def get_return_comparison(self, etf_code: str) -> Dict[str, pd.DataFrame]:
        """獲取報酬比較數據"""
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0010.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        tables = soup.find_all('table', {'class': 'datalist'})
        result = {}

        # 處理報酬率比較表
        if len(tables) >= 1:
            df_comparison = pd.read_html(str(tables[0]))[0]
            # 處理排名欄位
            for col in df_comparison.columns[1:]:
                mask = df_comparison[col].astype(str).str.contains('/')
                df_comparison.loc[mask, col] = df_comparison.loc[mask, col].apply(
                    lambda x: self._parse_ranking(x)[0]
                )
            result['comparison'] = df_comparison

        # 處理月份報酬率比較表
        if len(tables) >= 2:
            df_monthly = pd.read_html(str(tables[1]))[0]
            result['monthly'] = df_monthly

        return result

    def get_return_trends(self, etf_code: str) -> Dict[str, pd.DataFrame]:
        """獲取報酬走勢數據"""
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0009.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        tables = soup.find_all('table', {'class': 'DataTable'})
        result = {}

        table_names = ['monthly_return', 'quarterly_return', 'yearly_return']

        for i, table in enumerate(tables):
            if i < len(table_names):
                df = pd.read_html(str(table))[0]
                # 將百分比轉換為浮點數
                for col in df.columns[1:]:
                    df[col] = df[col].apply(self._parse_percentage)
                result[table_names[i]] = df

        return result

    def get_all_data(self, etf_code: str) -> Dict:
        """獲取所有ETF數據"""
        return {
            'risk_analysis': self.get_risk_analysis(etf_code),
            'return_comparison': self.get_return_comparison(etf_code),
            'return_trends': self.get_return_trends(etf_code)
        }


# 使用示例
if __name__ == "__main__":
    scraper = ETFScraper()

    # 獲取VT的所有數據
    data = scraper.get_all_data('VT')

    # 打印風險分析數據
    print("\n風險分析:")
    print(pd.DataFrame(data['risk_analysis']).T)

    # 打印報酬比較數據
    print("\n報酬比較:")
    for key, df in data['return_comparison'].items():
        print(f"\n{key}:")
        print(df)

    # 打印報酬走勢數據
    print("\n報酬走勢:")
    for key, df in data['return_trends'].items():
        print(f"\n{key}:")
        print(df)
