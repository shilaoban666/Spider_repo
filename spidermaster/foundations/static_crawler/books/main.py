import requests
from lxml import etree
from urllib.parse import urljoin
from tqdm import tqdm
import re
url = "https://www.bq01.cc/index/36525/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def main():
    content(url)


def content(url):
    response = requests.get(url, headers=headers)
    text = response.content.decode('utf-8')
    html = etree.HTML(text)

    # 获取书名
    a_name = html.xpath('//div[@class="info"]/h1/text()')
    a_name = a_name[0].strip() if a_name else "未知书名"

    # 获取章节列表
    a_list = html.xpath('//div[@class="listmain"]//dl//dd/a/@href')
    # 智能清洗链接（保留合法路径）
    a_list = [
        link for link in a_list
        if re.match(r'^(/|https?://|\.)', link)  # 允许相对路径、绝对URL、点开头的路径
        and not link.startswith('javascript:')    # 过滤JS伪协议
    ]
    total_chapters = len(a_list)  # 总章节数

    # 初始化进度条
    with tqdm(total=total_chapters, desc="下载进度", unit="章") as pbar:
        for index in a_list:
            chapter_url = urljoin(url, index)
            download_book(a_name, chapter_url)
            pbar.update(1)  # 更新进度条


def download_book(name, url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return

        text = response.content.decode('utf-8')
        html = etree.HTML(text)

        # 章节标题
        timu = html.xpath('//div[@class="content"]/h1/text()')
        timu = timu[0].strip() if timu else "未知章节"

        # 章节内容
        content_lines = html.xpath('//div[@id="chaptercontent"]//text()')
        content = "\n\n".join(line.strip() for line in content_lines if line.strip())
        savepath = ".\\" + name + ".txt"
        # 保存到文件
        with open(savepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{timu}\n{content}\n")

    except Exception as e:
        print(f"章节下载失败: {url}，错误: {e}")


if __name__ == '__main__':
    main()
    print('下载完成')