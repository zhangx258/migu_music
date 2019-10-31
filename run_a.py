import requests, json
import os, time
import eyed3

# 10/18更新，找到个新的API，似乎更方便
# 默认下载高品质(无损品质更改download_song_url里的参数'formatType=SQ resourceType=E'即可)

class Migu():
    def __init__(self):
        self.path = os.path.abspath('F:/咪咕下载')
        self.search_url = 'http://pd.musicapp.migu.cn/MIGUM2.0/v1.0/content/search_all.do?&ua=Android_migu&version=5.0.1&text={}&pageNo={}&pageSize=10&searchSwitch='
        self.to_add_url = '{"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0,"bestShow":1}'
        self.download_song_url = 'http://app.pd.nf.migu.cn/MIGUM2.0/v1.0/content/sub/listenSong.do?toneFlag=HQ&netType=00&userId=15548614588710179085069&ua=Android_migu&version=5.1&copyrightId=0&contentId={}&resourceType=2&channel=0'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                        }
    
    def get_searchlist(self, text):
        # 搜索关键字，将所有歌曲信息存入list
        get_page_url = self.search_url.format(text, 1)+self.to_add_url
        get_page_html = requests.get(get_page_url, headers = self.headers)
        get_page_josn = json.loads(get_page_html.text)
        if get_page_josn['info']!='成功':
            print('查询失败！')
            return []
        total_count = get_page_josn['songResultData']['totalCount']
        page_numner = int(total_count)//10+1
        search_list = []
        for page in range(page_numner):
            url = self.search_url.format(text, page+1)+self.to_add_url
            html = requests.get(url, headers = self.headers)
            js = json.loads(html.text)
            result = js['songResultData']['result']
            for item in result:
                song = {}
                song['name'] = item.get('name', '')
                song['singer'] = [i['name'] for i in item.get('singers', [])]
                song['albums'] = [i['name'] for i in item.get('albums', [])]
                song['lyricUrl'] = item.get('lyricUrl', '')
                song['imgUrls'] = [i['img'] for i in item.get('imgItems', [])]
                song['contentId'] = item.get('contentId', '')
                song['copyrightId'] = item.get('copyrightId', '')
                song['songId'] = item.get('id', '')
                search_list.append(song)
        print('一共查到%s首歌曲！'%len(search_list))
        return search_list
    
    def download_song(self, search_list, text):
        # 创建歌手文件夹，存放歌曲
        os.mkdir(self.path + './' + text)
        for song in search_list:
            contentId = song['contentId']
            name = song['name']
            url = self.download_song_url.format(contentId)
            try:
                response = requests.get(url, headers = self.headers)
            except TimeoutError:
                time.sleep(2)
                response = requests.get(url, headers = self.headers, timeout=None)
            filename = os.path.join(self.path, text, name+'.mp3')
            with open(filename, 'wb') as f:
                f.write(response.content)
                print('已下载%s'%name)
            time.sleep(1)
    
    def download_pic_and_lyc(self, text):
        # 下载图片和歌词
        filename = os.path.join(self.path, text+'.json')
        with open(filename, 'r') as f:
            for line in f:
                song = json.loads(line)
                name = song['name']
                lyc_url = song['lyricUrl']
                pic_url = song['imgUrls'][-1]
                pic_res = requests.get(pic_url, headers=self.headers)
                pic_filename = os.path.join(self.path, text, name+'.jpg')
                with open(pic_filename, 'wb') as fp:
                    fp.write(pic_res.content)
                lyc_res = requests.get(lyc_url, headers=self.headers)
                lyc_filename = os.path.join(self.path, text, name+'.lyc')
                with open(lyc_filename, 'wb',) as fp:
                    fp.write(lyc_res.content)
                
    def wirte_lsit(self, search_list, text):
        # 将搜索的歌手信息存入json文件
        filename = os.path.join(self.path, text+'.json')
        with open(filename, 'a+') as f:
            for song in search_list:
                resultJson = json.dumps(song)
                f.write(resultJson + '\n')
                print('已写入: %s' % song)

    def run(self):
        # text = input('请输入需要下载歌曲的歌手：')
        # print('你输入的歌手名是：{}, 已发送请求！'.format(text))
        text = '周杰伦'
        #search_list = self.get_searchlist(text)
        #self.wirte_lsit(search_list, text)
        #self.download_song(search_list, text)
        self.download_pic_and_lyc(text)

if __name__ == '__main__':
    test = Migu()
    test.run()
