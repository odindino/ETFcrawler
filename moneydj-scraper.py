import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Tuple, Union, Optional
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

    def _parse_ranking(self, text: str) -> Union[Tuple[Optional[int], Optional[int]], str]:
        """解析排名字符串
        根據context返回不同格式:
        - 用於風險分析時返回 (rank, total) tuple
        - 用於報酬比較時返回原始字符串
        """
        if '/' in str(text):
            try:
                parts = text.strip().split('/')
                if len(parts) == 2:
                    # 如果可以轉換為數字，返回tuple
                    rank = int(parts[0])
                    total = int(parts[1])
                    return rank, total
                return text.strip()  # 否則返回原始字符串
            except ValueError:
                return text.strip()  # 如果轉換失敗，返回原始字符串
        return None, None

    def _parse_percentage(self, text: str) -> Optional[float]:
        """改進的百分比解析方法"""
        try:
            # 移除所有空白字符、百分號和括號內容
            value = re.sub(r'\([^)]*\)', '', str(text))
            value = value.strip().replace('%', '').strip()
            if value == '' or value == '-':
                return None
            return float(value)
        except (ValueError, AttributeError):
            return None

    def _parse_number(self, text: str) -> Optional[float]:
        """解析數值，處理逗號和括號"""
        try:
            value = re.sub(r'\([^)]*\)', '', str(text))
            value = value.replace(',', '').strip()
            if value == '' or value == '-':
                return None
            return float(value)
        except (ValueError, AttributeError):
            return None

    def get_basic_info(self, etf_code: str) -> Dict:
        """獲取ETF基本資訊"""
        url = f"https://www.moneydj.com/etf/x/basic/basic0004.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        # 找到資料表格
        table = soup.find('table', {'id': 'sTable'})
        if not table:
            return {}

        # 創建一個字典來存儲提取的資訊
        etf_info = {}

        # 遍歷表格行提取資訊
        for row in table.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip()

                # 針對有4列的行特殊處理
                if len(cols) == 4:
                    key2 = cols[2].text.strip()
                    value2 = cols[3].text.strip()
                    etf_info[key2] = value2

                etf_info[key] = value

        # 提取所需的特定欄位
        result = {
            'ETF名稱': etf_info.get('ETF名稱', ''),
            '交易所代碼': etf_info.get('交易所代碼', ''),
            '英文名稱': etf_info.get('英文名稱', ''),
            '發行公司': etf_info.get('發行公司', ''),
            '成立日期': etf_info.get('成立日期', '').split('（')[0],  # 只取日期部分
            'ETF規模': etf_info.get('ETF規模', '').split('(')[0],  # 只取數值部分
            '成交量': etf_info.get('成交量(股)', '').split('（')[0],  # 只取數值部分
            'ETF市價': etf_info.get('ETF市價', ''),
            'ETF淨值': etf_info.get('ETF淨值', ''),
            '折溢價(%)': etf_info.get('折溢價(%)', '').split('(')[0],  # 只取當前值
            '配息頻率': etf_info.get('配息頻率', ''),
            '總管理費用(%)': etf_info.get('總管理費用(%)', '').split(' ')[0],  # 只取費用率
            '殖利率(%)': etf_info.get('殖利率(%)', '').split('（')[0],  # 只取當前值
            '年化標準差(%)': etf_info.get('年化標準差(%)', '').split('（')[0]  # 只取當前值
        }

        return result

    def _get_holdings_by_region(self, soup: BeautifulSoup) -> pd.DataFrame:
        """抓取依區域的持股分布"""
        try:
            region_table = soup.find(
                'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable'})
            if not region_table:
                return None

            data = []
            for row in region_table.find_all('tr')[1:]:  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 4:
                    data.append({
                        '區域': cols[1].text.strip(),
                        '投資金額(萬美元)': float(cols[2].text.strip().replace(',', '')),
                        '比例(%)': float(cols[3].text.strip())
                    })

            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_holdings_by_region: {e}")
            return None

    def _get_holdings_by_sector(self, soup: BeautifulSoup) -> pd.DataFrame:
        """抓取依產業的持股分布"""
        try:
            sector_table = soup.find(
                'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable2'})
            if not sector_table:
                return None

            data = []
            for row in sector_table.find_all('tr')[1:]:  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 4:
                    data.append({
                        '產業': cols[1].text.strip(),
                        '投資金額(萬美元)': float(cols[2].text.strip().replace(',', '')),
                        '比例(%)': float(cols[3].text.strip())
                    })

            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_holdings_by_sector: {e}")
            return None

    def _get_top_holdings(self, soup: BeautifulSoup) -> pd.DataFrame:
        """抓取主要持股明細"""
        try:
            holdings_table = soup.find(
                'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable3'})
            if not holdings_table:
                return None

            data = []
            for row in holdings_table.find_all('tr')[1:]:  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 3:
                    data.append({
                        '個股名稱': cols[0].text.strip(),
                        '投資比例(%)': float(cols[1].text.strip()),
                        '持有股數': float(cols[2].text.strip().replace(',', ''))
                    })

            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_top_holdings: {e}")
            return None

    def get_holdings(self, etf_code: str) -> Dict[str, Optional[pd.DataFrame]]:
        """獲取ETF的全部持股資訊"""
        url = f"https://www.moneydj.com/ETF/X/Basic/Basic0007.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        # 獲取所有標題來確認有哪些資訊
        titles = soup.find_all('div', {'class': 'eTitle'})
        title_texts = [title.text.strip() for title in titles]

        # 創建結果字典
        result = {
            'holdings_by_region': None,
            'holdings_by_sector': None,
            'top_holdings': None
        }

        # 根據標題決定要抓取的資訊
        for title in title_texts:
            if '依區域' in title:
                df = self._get_holdings_by_region(soup)
                if df is not None and not df.empty:
                    result['holdings_by_region'] = df
            elif '依產業' in title:
                df = self._get_holdings_by_sector(soup)
                if df is not None and not df.empty:
                    result['holdings_by_sector'] = df
            elif '持股明細' in title:
                df = self._get_top_holdings(soup)
                if df is not None and not df.empty:
                    result['top_holdings'] = df

        return result

    # 在使用時也要加入相應的檢查：
    def print_holdings(holdings_data: Dict[str, Optional[pd.DataFrame]]) -> None:
        """格式化打印持股資訊"""
        print("\n持股分析:")
        for category, df in holdings_data.items():
            if df is not None and not df.empty:
                print(f"\n{category}:")
                print(df)
            else:
                print(f"\n{category}: 無資料")

    def get_return_trends(self, etf_code: str) -> Dict[str, pd.DataFrame]:
        """獲取報酬走勢數據"""
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0009.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        result = {}

        tables = {'monthly': 'stable2',
                  'quarterly': 'stable3', 'yearly': 'stable'}

        for period, table_id in tables.items():
            table = soup.find('table', {'id': table_id})
            if table:
                df = pd.read_html(str(table))[0]
                # 處理數值列
                for col in df.columns[1:]:
                    df[col] = df[col].apply(self._parse_percentage)
                result[f'{period}_return'] = df

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

                # 特別處理排名數據
                try:
                    rank, total = self._parse_ranking(cols[3].text)
                    if isinstance(rank, str):  # 如果返回原始字符串
                        rank_str = rank
                        rank, total = map(int, rank_str.split('/'))
                except (ValueError, TypeError):
                    rank, total = None, None

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
            comparison_data = []
            rows = tables[0].find_all('tr')

            # 獲取列名
            headers = [th.text.strip() for th in rows[0].find_all('th')]

            # 處理每一行數據
            for row in rows[1:]:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 5:
                    row_data = {
                        '項目': cols[0].text.strip(),
                    }
                    # 處理每一列的數據
                    for i, header in enumerate(headers[1:], 1):
                        value = cols[i].text.strip()
                        if '/' in value:  # 如果是排名格式
                            row_data[header] = value
                        else:  # 如果是數值
                            try:
                                row_data[header] = float(value)
                            except ValueError:
                                row_data[header] = None
                    comparison_data.append(row_data)

            result['comparison'] = pd.DataFrame(comparison_data)

        # 處理月份報酬率比較表
        if len(tables) >= 2:
            monthly_data = []
            rows = tables[1].find_all('tr')

            # 獲取列名
            headers = [th.text.strip() for th in rows[0].find_all('th')]

            # 處理每一行數據
            for row in rows[1:]:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 8:
                    row_data = {
                        '項目': cols[0].text.strip(),
                    }
                    # 處理每一列的數據
                    for i, header in enumerate(headers[1:], 1):
                        value = cols[i].text.strip()
                        if '/' in value:  # 如果是排名格式
                            row_data[header] = value
                        else:  # 如果是數值
                            try:
                                row_data[header] = float(value)
                            except ValueError:
                                row_data[header] = None
                    monthly_data.append(row_data)

            result['monthly'] = pd.DataFrame(monthly_data)

        return result

    def get_all_data(self, etf_code: str) -> Dict:
        """獲取ETF的所有數據"""
        return {
            'basic_info': self.get_basic_info(etf_code),
            'holdings': self.get_holdings(etf_code),
            'risk_analysis': self.get_risk_analysis(etf_code),
            'return_comparison': self.get_return_comparison(etf_code),
            'return_trends': self.get_return_trends(etf_code)
        }


scraper = ETFScraper()
data = scraper.get_all_data('VOO')

# 查看各部分數據
print("\n基本資訊:")
print(pd.DataFrame([data['basic_info']]))


# 更細緻的控制
holdings = data.get('holdings', {})

# 安全地訪問各類持股資料
for holding_type in ['holdings_by_region', 'holdings_by_sector', 'top_holdings']:
    df = holdings.get(holding_type)
    if df is not None and not df.empty:
        print(f"\n{holding_type}:")
        print(df)
    else:
        print(f"\n{holding_type}: 無資料")

print("\n風險分析:")
print(pd.DataFrame(data['risk_analysis']).T)

print("\n報酬比較:")
if 'comparison' in data['return_comparison']:
    print(data['return_comparison']['comparison'])

print("\n月份報酬比較:")
if 'monthly' in data['return_comparison']:
    print(data['return_comparison']['monthly'])

print("\n報酬走勢:")
print(data['return_trends']['monthly_return'])
print(data['return_trends']['quarterly_return'])
print(data['return_trends']['yearly_return'])

#     for key, df in data['return_trends'].items():
#         print(f"\n{key}:")
#         print(df)
