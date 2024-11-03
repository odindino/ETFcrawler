"""
MoneyDJ ETF網站爬蟲程式 (ETF Website Scraper)

此程式用於抓取 MoneyDJ 理財網站上的 ETF 相關資訊，包括：
This program scrapes ETF information from MoneyDJ financial website, including:

1. 基本資訊 (Basic Information)
   - ETF名稱、代碼、規模等 (ETF name, code, size, etc.)
   - 費用、淨值、折溢價等 (Fees, NAV, premium/discount, etc.)

2. 持股資訊 (Holdings Information)
   - 依區域分布 (Distribution by region)
   - 依產業分布 (Distribution by sector)
   - 主要持股明細 (Top holdings details)

3. 風險分析 (Risk Analysis)
   - 追蹤誤差 (Tracking error)
   - 折溢價率 (Premium/Discount)

4. 報酬比較 (Return Comparison)
   - 與同類型ETF比較 (Comparison with similar ETFs)
   - 月度報酬率 (Monthly returns)

5. 報酬走勢 (Return Trends)
   - 月報酬率 (Monthly returns)
   - 季報酬率 (Quarterly returns)
   - 年報酬率 (Annual returns)

使用方式 (Usage):
    scraper = ETFScraper()
    data = scraper.get_all_data('VTI')
    print(data)

需求套件 (Requirements):
    - requests
    - beautifulsoup4
    - pandas
    - datetime
    - typing

作者 (Author): Zi-Liang Yang
版本 (Version): 1.0.0
日期 (Date): 2024-11-04
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Tuple, Union, Optional
from datetime import datetime


class ETFScraper:
    """
    ETF資料爬蟲類別
    ETF Data Scraper Class

    用於抓取和處理ETF相關資訊的類別，提供多個方法來獲取不同類型的ETF數據。
    A class for scraping and processing ETF-related information, providing multiple methods
    to retrieve different types of ETF data.
    """

    def __init__(self):
        """
        初始化爬蟲器，設置請求標頭
        Initialize the scraper with request headers
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _get_soup(self, url: str) -> BeautifulSoup:
        """
        獲取網頁內容並返回BeautifulSoup對象
        Get webpage content and return BeautifulSoup object

        Args:
            url (str): 目標網頁URL (Target webpage URL)

        Returns:
            BeautifulSoup: 解析後的HTML內容 (Parsed HTML content)
        """
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')

    def _parse_ranking(self, text: str) -> Union[Tuple[Optional[int], Optional[int]], str]:
        """
        解析排名字符串
        Parse ranking string

        根據context返回不同格式:
        Return different formats based on context:
        - 用於風險分析時返回 (rank, total) tuple
        - 用於報酬比較時返回原始字符串
        - For risk analysis: returns (rank, total) tuple
        - For return comparison: returns original string

        Args:
            text (str): 排名文字，例如 "142/859" (Ranking text, e.g., "142/859")

        Returns:
            Union[Tuple[Optional[int], Optional[int]], str]: 
                排名數據或原始字符串 (Ranking data or original string)
        """
        if '/' in str(text):
            try:
                parts = text.strip().split('/')
                if len(parts) == 2:
                    rank = int(parts[0])
                    total = int(parts[1])
                    return rank, total
                return text.strip()
            except ValueError:
                return text.strip()
        return None, None

    def _parse_percentage(self, text: str) -> Optional[float]:
        """
        解析百分比數值
        Parse percentage value

        處理包含百分號和括號的數值字符串
        Process numeric strings containing percentage signs and parentheses

        Args:
            text (str): 百分比文字，例如 "12.34%" (Percentage text, e.g., "12.34%")

        Returns:
            Optional[float]: 轉換後的浮點數值，若無法轉換則返回None
                           Converted float value, or None if conversion fails
        """
        try:
            value = re.sub(r'\([^)]*\)', '', str(text))
            value = value.strip().replace('%', '').strip()
            if value == '' or value == '-':
                return None
            return float(value)
        except (ValueError, AttributeError):
            return None

    def _parse_number(self, text: str) -> Optional[float]:
        """
        解析一般數值
        Parse numeric value

        處理包含逗號和括號的數值字符串
        Process numeric strings containing commas and parentheses

        Args:
            text (str): 數值文字，例如 "1,234.56" (Numeric text, e.g., "1,234.56")

        Returns:
            Optional[float]: 轉換後的浮點數值，若無法轉換則返回None
                           Converted float value, or None if conversion fails
        """
        try:
            value = re.sub(r'\([^)]*\)', '', str(text))
            value = value.replace(',', '').strip()
            if value == '' or value == '-':
                return None
            return float(value)
        except (ValueError, AttributeError):
            return None

    def get_basic_info(self, etf_code: str) -> Dict:
        """
        獲取ETF基本資訊
        Get ETF basic information

        抓取ETF的基本資料，包括名稱、代碼、規模、費用等
        Scrape basic ETF data including name, code, size, fees, etc.

        Args:
            etf_code (str): ETF代碼 (ETF code)

        Returns:
            Dict: 包含以下欄位的字典 (Dictionary containing following fields):
                - ETF名稱 (ETF name)
                - 交易所代碼 (Exchange code)
                - 英文名稱 (English name)
                - 發行公司 (Issuer)
                - 成立日期 (Inception date)
                - ETF規模 (ETF size)
                - 成交量 (Trading volume)
                - ETF市價 (ETF price)
                - ETF淨值 (ETF NAV)
                - 折溢價(%) (Premium/Discount(%))
                - 配息頻率 (Distribution frequency)
                - 總管理費用(%) (Total expense ratio(%))
                - 殖利率(%) (Yield(%))
                - 年化標準差(%) (Annualized standard deviation(%))
        """
        url = f"https://www.moneydj.com/etf/x/basic/basic0004.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        table = soup.find('table', {'id': 'sTable'})
        if not table:
            return {}

        etf_info = {}
        for row in table.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip()

                if len(cols) == 4:
                    key2 = cols[2].text.strip()
                    value2 = cols[3].text.strip()
                    etf_info[key2] = value2

                etf_info[key] = value

        result = {
            'ETF名稱': etf_info.get('ETF名稱', ''),
            '交易所代碼': etf_info.get('交易所代碼', ''),
            '英文名稱': etf_info.get('英文名稱', ''),
            '發行公司': etf_info.get('發行公司', ''),
            '成立日期': etf_info.get('成立日期', '').split('（')[0],
            'ETF規模': etf_info.get('ETF規模', '').split('(')[0],
            '成交量': etf_info.get('成交量(股)', '').split('（')[0],
            'ETF市價': etf_info.get('ETF市價', ''),
            'ETF淨值': etf_info.get('ETF淨值', ''),
            '折溢價(%)': etf_info.get('折溢價(%)', '').split('(')[0],
            '配息頻率': etf_info.get('配息頻率', ''),
            '總管理費用(%)': etf_info.get('總管理費用(%)', '').split(' ')[0],
            '殖利率(%)': etf_info.get('殖利率(%)', '').split('（')[0],
            '年化標準差(%)': etf_info.get('年化標準差(%)', '').split('（')[0]
        }

        return result

    def get_holdings(self, etf_code: str) -> Dict[str, Optional[pd.DataFrame]]:
        """
        獲取ETF的全部持股資訊
        Get all holdings information of the ETF

        抓取三種持股相關資訊：
        Scrape three types of holdings information:
        1. 依區域的持股分布 (Holdings distribution by region)
        2. 依產業的持股分布 (Holdings distribution by sector)
        3. 主要持股明細 (Top holdings details)

        Args:
            etf_code (str): ETF代碼 (ETF code)

        Returns:
            Dict[str, Optional[pd.DataFrame]]: 包含三個DataFrame的字典
                                             Dictionary containing three DataFrames:
                - holdings_by_region: 依區域分布 (Distribution by region)
                - holdings_by_sector: 依產業分布 (Distribution by sector)
                - top_holdings: 主要持股明細 (Top holdings details)
        """
        url = f"https://www.moneydj.com/ETF/X/Basic/Basic0007.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        titles = soup.find_all('div', {'class': 'eTitle'})
        title_texts = [title.text.strip() for title in titles]

        result = {
            'holdings_by_region': None,
            'holdings_by_sector': None,
            'top_holdings': None
        }

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

    def _get_holdings_by_region(self, soup: BeautifulSoup) -> Optional[pd.DataFrame]:
        """
        抓取依區域的持股分布
        Get holdings distribution by region

        Args:
            soup (BeautifulSoup): 網頁解析對象 (Parsed webpage object)

        Returns:
            Optional[pd.DataFrame]: 包含區域分布資料的DataFrame，若無資料則返回None
                                  DataFrame containing region distribution data, 
                                  or None if no data
        """
        try:
            region_table = soup.find(
                'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable'})
            if not region_table:
                return None

            data = []
            for row in region_table.find_all('tr')[1:]:
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

    def _get_holdings_by_sector(self, soup: BeautifulSoup) -> Optional[pd.DataFrame]:
        """
        抓取依產業的持股分布
        Get holdings distribution by sector

        Args:
            soup (BeautifulSoup): 網頁解析對象 (Parsed webpage object)

        Returns:
            Optional[pd.DataFrame]: 包含產業分布資料的DataFrame，若無資料則返回None
                                  DataFrame containing sector distribution data, 
                                  or None if no data
        """
        try:
            sector_table = soup.find(
                'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable2'})
            if not sector_table:
                return None

            data = []
            for row in sector_table.find_all('tr')[1:]:
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

    def _get_top_holdings(self, soup: BeautifulSoup) -> Optional[pd.DataFrame]:
        """
        抓取主要持股明細
        Get top holdings details

        Args:
            soup (BeautifulSoup): 網頁解析對象 (Parsed webpage object)

        Returns:
            Optional[pd.DataFrame]: 包含主要持股資料的DataFrame，若無資料則返回None
                                  DataFrame containing top holdings data, 
                                  or None if no data
        """
        try:
            holdings_table = soup.find(
                'table', {'id': 'ctl00_ctl00_MainContent_MainContent_stable3'})
            if not holdings_table:
                return None

            data = []
            for row in holdings_table.find_all('tr')[1:]:
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

    def get_risk_analysis(self, etf_code: str) -> Dict:
        """
        獲取風險分析數據
        Get risk analysis data

        抓取ETF的風險指標，包括追蹤誤差和季均折溢價等
        Scrape ETF risk indicators including tracking error and quarterly premium/discount

        Args:
            etf_code (str): ETF代碼 (ETF code)

        Returns:
            Dict: 包含以下風險指標的字典 (Dictionary containing following risk indicators):
                - 日期 (date)
                - 數值 (value)
                - 排名 (rank)
                - 總數 (total)
        """
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0013.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        table = soup.find('table', {'class': 'DataTable'})
        if not table:
            return {}

        data = {}
        rows = table.find_all('tr')[1:]  # 跳過表頭 (Skip header)

        for row in rows:
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 4:
                metric = cols[0].text.strip()
                date = cols[1].text.strip()
                value = self._parse_percentage(cols[2].text)

                try:
                    rank, total = self._parse_ranking(cols[3].text)
                    if isinstance(rank, str):
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
        """
        獲取報酬比較數據
        Get return comparison data

        抓取ETF與同類型ETF的報酬率比較數據
        Scrape return comparison data between the ETF and similar ETFs

        Args:
            etf_code (str): ETF代碼 (ETF code)

        Returns:
            Dict[str, pd.DataFrame]: 包含兩個DataFrame的字典 
                                   Dictionary containing two DataFrames:
                - comparison: 報酬率比較表 (Return comparison table)
                - monthly: 月份報酬比較表 (Monthly return comparison table)
        """
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0010.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        tables = soup.find_all('table', {'class': 'datalist'})
        result = {}

        # 處理報酬率比較表 (Process return comparison table)
        if len(tables) >= 1:
            comparison_data = []
            rows = tables[0].find_all('tr')
            headers = [th.text.strip() for th in rows[0].find_all('th')]

            for row in rows[1:]:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 5:
                    row_data = {
                        '項目': cols[0].text.strip(),
                    }
                    for i, header in enumerate(headers[1:], 1):
                        value = cols[i].text.strip()
                        if '/' in value:  # 如果是排名格式 (If it's ranking format)
                            row_data[header] = value
                        else:  # 如果是數值 (If it's numeric value)
                            try:
                                row_data[header] = float(value)
                            except ValueError:
                                row_data[header] = None
                    comparison_data.append(row_data)

            result['comparison'] = pd.DataFrame(comparison_data)

        # 處理月份報酬率比較表 (Process monthly return comparison table)
        if len(tables) >= 2:
            monthly_data = []
            rows = tables[1].find_all('tr')
            headers = [th.text.strip() for th in rows[0].find_all('th')]

            for row in rows[1:]:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 8:
                    row_data = {
                        '項目': cols[0].text.strip(),
                    }
                    for i, header in enumerate(headers[1:], 1):
                        value = cols[i].text.strip()
                        if '/' in value:  # 如果是排名格式 (If it's ranking format)
                            row_data[header] = value
                        else:  # 如果是數值 (If it's numeric value)
                            try:
                                row_data[header] = float(value)
                            except ValueError:
                                row_data[header] = None
                    monthly_data.append(row_data)

            result['monthly'] = pd.DataFrame(monthly_data)

        return result

    def get_return_trends(self, etf_code: str) -> Dict[str, pd.DataFrame]:
        """
        獲取報酬走勢數據
        Get return trend data

        抓取ETF的月度、季度和年度報酬率數據
        Scrape monthly, quarterly, and yearly return data of the ETF

        Args:
            etf_code (str): ETF代碼 (ETF code)

        Returns:
            Dict[str, pd.DataFrame]: 包含三個DataFrame的字典 
                                   Dictionary containing three DataFrames:
                - monthly_return: 月報酬率 (Monthly returns)
                - quarterly_return: 季報酬率 (Quarterly returns)
                - yearly_return: 年報酬率 (Yearly returns)
        """
        url = f"https://www.moneydj.com/etf/x/Basic/Basic0009.xdjhtm?etfid={etf_code}"
        soup = self._get_soup(url)

        result = {}

        tables = {
            'monthly': 'stable2',
            'quarterly': 'stable3',
            'yearly': 'stable'
        }

        for period, table_id in tables.items():
            table = soup.find('table', {'id': table_id})
            if table:
                df = pd.read_html(str(table))[0]
                # 處理數值列 (Process numeric columns)
                for col in df.columns[1:]:
                    df[col] = df[col].apply(self._parse_percentage)
                result[f'{period}_return'] = df

        return result

    def get_all_data(self, etf_code: str) -> Dict:
        """
        獲取ETF的所有數據
        Get all data for the ETF

        整合所有ETF相關資訊的主要方法
        Main method to integrate all ETF-related information

        Args:
            etf_code (str): ETF代碼 (ETF code)

        Returns:
            Dict: 包含所有ETF資訊的字典 (Dictionary containing all ETF information):
                - basic_info: 基本資訊 (Basic information)
                - holdings: 持股資訊 (Holdings information)
                - risk_analysis: 風險分析 (Risk analysis)
                - return_comparison: 報酬比較 (Return comparison)
                - return_trends: 報酬走勢 (Return trends)
        """
        return {
            'basic_info': self.get_basic_info(etf_code),
            'holdings': self.get_holdings(etf_code),
            'risk_analysis': self.get_risk_analysis(etf_code),
            'return_comparison': self.get_return_comparison(etf_code),
            'return_trends': self.get_return_trends(etf_code)
        }


# 使用範例 (Usage Example)
if __name__ == "__main__":
    # 建立爬蟲器實例 (Create scraper instance)
    scraper = ETFScraper()

    # 指定要查詢的ETF代碼 (Specify ETF code to query)
    etf_code = 'VT'

    # 獲取所有數據 (Get all data)
    data = scraper.get_all_data(etf_code)

    # 顯示基本資訊 (Display basic information)
    print("\n基本資訊 (Basic Information):")
    print(pd.DataFrame([data['basic_info']]))

    # 顯示持股資訊 (Display holdings information)
    print("\n持股資訊 (Holdings Information):")
    holdings = data.get('holdings', {})
    for holding_type in ['holdings_by_region', 'holdings_by_sector', 'top_holdings']:
        df = holdings.get(holding_type)
        if df is not None and not df.empty:
            print(f"\n{holding_type}:")
            print(df)
        else:
            print(f"\n{holding_type}: 無資料 (No data)")

    # 顯示風險分析 (Display risk analysis)
    print("\n風險分析 (Risk Analysis):")
    print(pd.DataFrame(data['risk_analysis']).T)

    # 顯示報酬比較 (Display return comparison)
    print("\n報酬比較 (Return Comparison):")
    if 'comparison' in data['return_comparison']:
        print(data['return_comparison']['comparison'])

    # 顯示月份報酬比較 (Display monthly return comparison)
    print("\n月份報酬比較 (Monthly Return Comparison):")
    if 'monthly' in data['return_comparison']:
        print(data['return_comparison']['monthly'])

    # 顯示報酬走勢 (Display return trends)
    print("\n報酬走勢 (Return Trends):")
    print("月報酬率 (Monthly Returns):")
    print(data['return_trends']['monthly_return'])
    print("\n季報酬率 (Quarterly Returns):")
    print(data['return_trends']['quarterly_return'])
    print("\n年報酬率 (Yearly Returns):")
    print(data['return_trends']['yearly_return'])
