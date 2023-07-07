import httpx
import re
import logging
from os import makedirs
from os.path import exists

stock = '博思软件'
RESULTS_DIR = f'D:\\年报\\{stock}'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'}
orgid_url = 'http://www.cninfo.com.cn/new/data/szse_stock.json'
url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
DETAIL_URL = 'http://static.cninfo.com.cn/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def get_orgid():
    """获取股票的orgid"""
    with httpx.Client(headers=headers) as client:
        response = client.get(orgid_url)
        orgids = response.json()
        stock_lists = orgids['stockList']
        for stock_list in stock_lists:
            if stock_list['zwjc'] == stock:
                logging.info(f'获得股票信息: {stock}')
                return {
                    'code': stock_list['code'],
                    'orgid': stock_list['orgId']
                }


def get_pdf_url(page, data):
    """获得年报及招股说明书pdf下载信息"""
    code = data.get('code')
    orgid = data.get('orgid')

    post_data = {
        'stock': f'{code},{orgid}',
        'tabName': 'fulltext',
        'pageSize': 30,
        'pageNum': page,
        'column': 'szse',
        'category': 'category_ndbg_szsh;category_sf_szsh;',
        'plate': 'sz',
        'seDate': '',
        'searchkey': '',
        'secid': '',
        'sortName': '',
        'sortType': '',
        'isHLtitle': 'true'
    }

    with httpx.Client(headers=headers) as client:
        res = client.post(url, data=post_data)
        an = res.json()
        dats = an.get('announcements')
        stock_list = []
        for dat in dats:
            if re.search('摘要', dat['announcementTitle']) or re.search('已取消', dat['announcementTitle']):
                continue
            elif re.search('招股说明书', dat['announcementTitle']):
                stock_list.append({
                    'announcementTitle': dat['announcementTitle'],
                    'adjunctUrl': dat['adjunctUrl']
                })
            elif re.search('年度报告', dat['announcementTitle']):
                stock_list.append({
                    'announcementTitle': dat['announcementTitle'],
                    'adjunctUrl': dat['adjunctUrl']
                })
        return stock_list


def save_pdf(datas):
    """保存年报pdf"""
    for data in datas:
        part_url = data.get('adjunctUrl')
        name = data.get('announcementTitle')
        pdf_name = stock + '：' + name
        pdf_url = DETAIL_URL + part_url
        with httpx.Client(headers=headers) as client:
            response = client.get(pdf_url)
            pdf = f"{RESULTS_DIR}\\{pdf_name}.pdf"
            logging.info(f'saving pdf: {pdf_name}')
            with open(pdf, 'wb') as f:
                f.write(response.content)


def main():
    for page in range(1, 2):
        pdfdata = get_pdf_url(page, get_orgid())
        save_pdf(pdfdata)


if __name__ == '__main__':
    main()
