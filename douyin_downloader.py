# -*- coding:utf-8 -*-
# Author: Z.W.
from splinter.driver.webdriver.chrome import Options, Chrome
from splinter.browser import Browser
from contextlib import closing
import requests, json, time, re, os, sys, datetime
from bs4 import BeautifulSoup
import argparse
import random

class LemonLemon_douyin(object):
    def __init__(self, width = 500, height = 300):
        """
        抖音App视频下载
        """
        # 无头浏览器
        chrome_options = Options()
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"')
        self.driver = Browser(driver_name='chrome', options=chrome_options, headless=True)

    def get_video_urls(self, input_f):
        """
        获得视频播放地址
        Parameters:
            user_id：查询的用户ID
        Returns:
            video_names: 视频名字列表
            video_urls: 视频链接列表
            nickname: 用户昵称
        """
        video_names = []
        video_urls = []
        i = 1
        now_date = datetime.datetime.now()
        self.date_today = str(now_date.date())+'_'+str(now_date.hour)+':'+str(now_date.minute)
        #unique_id = ''
        #while unique_id != user_id:
        #    search_url = 'https://api.amemv.com/aweme/v1/discover/search/?cursor=0&keyword=%s&count=10&type=1&retry_type=no_retry&iid=17900846586&device_id=34692364855&ac=wifi&channel=xiaomi&aid=1128&app_name=aweme&version_code=162&version_name=1.6.2&device_platform=android&ssmix=a&device_type=MI+5&device_brand=Xiaomi&os_api=24&os_version=7.0&uuid=861945034132187&openudid=dc451556fc0eeadb&manifest_version_code=162&resolution=1080*1920&dpi=480&update_version_code=1622' % user_id
        #    req = requests.get(url = search_url, verify = False)
        #    html = json.loads(req.text)
        #    aweme_count = html['user_list'][0]['user_info']['aweme_count']
        #    uid = html['user_list'][0]['user_info']['uid']
        #    nickname = html['user_list'][0]['user_info']['nickname']
        #    unique_id = html['user_list'][0]['user_info']['unique_id']
        #user_url = 'https://www.douyin.com/aweme/v1/aweme/post/?user_id=%s&max_cursor=0&count=%s' % (uid, aweme_count)
        #req = requests.get(url = user_url, verify = False)
        #html = json.loads(req.text)
        #i = 1
        #for each in html['aweme_list']:
        #    share_desc = each['share_info']['share_desc']
        #    if '抖音-原创音乐短视频社区' == share_desc:
        #        video_names.append(str(i) + '.mp4')
        #        i += 1
        #    else:
        #        video_names.append(share_desc + '.mp4')
        #    video_urls.append(each['share_info']['share_url'])
        with open(input_f) as f:
            for line in f:
                if line.startswith('http'):
                    video_urls.append(line)
                    video_names.append(self.date_today+'_'+str(i)+'.mp4')
                    i += 1

        return video_names, video_urls#video_names, video_urls, nickname

    def get_download_url(self, video_url):
        """
        获得带水印的视频播放地址
        Parameters:
            video_url：带水印的视频播放地址
        Returns:
            download_url: 带水印的视频下载地址
        """
        req = requests.get(url = video_url, verify = False)
        bf = BeautifulSoup(req.text, 'lxml')
        script = bf.find_all('script')[-1]
        video_url_js = re.findall('var data = \[(.+)\];', str(script))[0]
        video_html = json.loads(video_url_js)
        download_url = video_html['video']['play_addr']['url_list'][0]
        return download_url

    def video_downloader(self, video_url, video_name, watermark_flag=True):
        """
        视频下载
        Parameters:
            video_url: 带水印的视频地址
            video_name: 视频名
            watermark_flag: 是否下载不带水印的视频
        Returns:
            无
        """
        size = 0
        if watermark_flag == True:
            video_url = self.remove_watermark(video_url)
        else:
            video_url = self.get_download_url(video_url)
        with closing(requests.get(video_url, stream=True, verify = False)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length']) 
            if response.status_code == 200:
                sys.stdout.write('  [文件大小]:%0.2f MB\n' % (content_size / chunk_size / 1024))

                with open(video_name, "wb") as file:  
                    for data in response.iter_content(chunk_size = chunk_size):
                        file.write(data)
                        size += len(data)
                        file.flush()

                        sys.stdout.write('  [下载进度]:%.2f%%' % float(size / content_size * 100) + '\r')
                        sys.stdout.flush()


    def remove_watermark(self, video_url):
        """
        获得无水印的视频播放地址
        Parameters:
            video_url: 带水印的视频地址
        Returns:
            无水印的视频下载地址
        """
        self.driver.visit('http://douyin.iiilab.com/')
        self.driver.find_by_tag('input').fill(video_url)
        self.driver.find_by_xpath('//button[@class="btn btn-default"]').click()
        html = self.driver.find_by_xpath('//div[@class="thumbnail"]/div/p')[0].html
        bf = BeautifulSoup(html, 'lxml')
        return bf.find('a').get('href')

    def run(self, input_f):
        """
        运行函数
        Parameters:
            None
        Returns:
            None
        """
        #self.hello()
        #user_id = input('请输入ID(例如40103580):')
        error_url = []
        video_names, video_urls = self.get_video_urls(input_f)
        if 'douyin_download'+self.date_today not in os.listdir():
            os.mkdir('douyin_download'+self.date_today)
        print('视频下载中:共有%d个作品!\n' % len(video_urls))
        for num in range(len(video_urls)):
            print('  解析第%d个视频链接 [%s] 中，请稍后!\n' % (num+1, video_urls[num]))
            random_wait = random.uniform(3,5)
            print('waiting...', random_wait)
            time.sleep(random_wait)
            if '\\' in video_names[num]:
                video_name = video_names[num].replace('\\', '')
            elif '/' in video_names[num]:
                video_name = video_names[num].replace('/', '')
            else:
                video_name = video_names[num]
            try:
                self.video_downloader(video_urls[num], os.path.join('douyin_download'+self.date_today, video_name))
            except:
                print('**************************')
                print('ERROR', video_urls[num])
                error_url.append(video_urls[num])

            
            print('\n')
        self.driver.close()
        with open('error_url.txt', 'w') as f:
            f = error_url
        print('下载完成!')
        print('出错数量：', len(error_url))


#

if __name__ == '__main__':
    #Parsing args
    parser = argparse.ArgumentParser( description = 'Please state dowload list file' )
    parser.add_argument( "input_file", help = "path to input file" )


    args = parser.parse_args()

    douyin = LemonLemon_douyin()
    douyin.run(args.input_file)

