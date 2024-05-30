import httpx
import re
import logging
from os import makedirs
from os.path import exists

stock = '博思软件'
announcement_list = ['分红派息实施公告', '利润分配预案', '年度报告', '半年度|季度', '招股说明书']
announcement = '季度报告'
ban = '摘要|已取消|提示性公告'
RESULTS_DIR = f'D:\\报告\\{stock}\\{announcement}'
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
                return {
                    'code': stock_list['code'],
                    'orgid': stock_list['orgId']
                }


def get_pdf_url(page, data):
    """获得公告的pdf下载信息"""
    code = data.get('code')
    orgid = data.get('orgid')
    post_data = {
        'stock': f'{code},{orgid}',
        'tabName': 'fulltext',
        'pageSize': 30,
        'pageNum': page,
        'column': 'szse',
        'category': '',
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
            if re.search(ban, dat['announcementTitle']):
                continue
            elif re.search(announcement, dat['announcementTitle']):
                stock_list.append({
                    'announcementTitle': dat['announcementTitle'],
                    'adjunctUrl': dat['adjunctUrl']
                })
        return stock_list


def get_totalpages(data):
    """获得公告的总页数"""
    code = data.get('code')
    orgid = data.get('orgid')
    post_data = {
        'stock': f'{code},{orgid}',
        'tabName': 'fulltext',
        'pageSize': 30,
        'pageNum': 1,
        'column': 'szse',
        'category': '',
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
        totalpages = an.get('totalpages')
        return totalpages


def save_pdf(datas):
    """保存公告pdf"""
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
    pages = get_totalpages(get_orgid())
    logging.info(f'一共{pages}页公告信息...')
    for page in range(1, pages + 1):
        pdfdata = get_pdf_url(page, get_orgid())
        logging.info(f'获得第{page}页股票信息...')
        save_pdf(pdfdata)
    logging.info('下载完成')


if __name__ == '__main__':
    main()
