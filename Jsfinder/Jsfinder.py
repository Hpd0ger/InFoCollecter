from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities
import requests,re,os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib3


class Jsfinder:
    def __init__(self):
        self.url = ""
        self.proxy = ""
        self.domain = ""
        self.timeout = 10
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",--headless')
        # 不加载图片/不开启浏览器
        self.options.add_argument('--headless')
        self.options.add_argument('blink-settings=imagesEnabled=false')
        self.options.add_argument('--disable-gpu')
        self.blacklist = 'jpg|css|png|docx|pdf|jquery.min|gif'
        self.js_url = [] 
        self.urls = [] 
        self.spiderHeader = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "Connection": "close"
            }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # 取消ssl的认证

    def Judge2api(self,url,domain,cookie,flag=False):
        self.urls.clear()
        self.url = url
        self.domain = domain
        self.proxy = "127.0.0.1:8080"
        # 后面会使用代理池随机获取代理proxy
        self.options.add_argument('--proxy-server=%s'%(self.proxy))
        self.driver = webdriver.Chrome(chrome_options=self.options)
        print("[@]:当前使用的代理:",self.proxy)

        if cookie != None:
            if self.deal_cookie(cookie) == True:
                print("[@]设置cookie成功")
            else:print("[-]设置cookie失败～")

# 深度递归爬取所有url
        if flag != False: 
            print("[*]Warning..开始深度爬取模式...")
            self.urls.append(self.url)
            for self.url in self.urls:
                results = self.Findapi()
                for result in results:
                    if result not in self.urls and re.search(self.blacklist,result) == None:
                        self.urls.append(result)
                    else:continue
                print(self.urls)
            self.driver.quit()
            return self.urls
        else: return self.Findapi()

    def Findapi(self):
        try:
            rec = requests.get(url=self.url,headers=self.spiderHeader,timeout=self.timeout-2,verify=False)
            if rec.status_code == 404 or rec.status_code == 403:
                return "null"
            else:               
                self.driver.get(self.url)
                result = EC.alert_is_present()(self.driver)
                if result:result.dismiss()
                self.driver.implicitly_wait(self.timeout-1)
                self.driver.set_script_timeout(self.timeout-1)
                self.driver.set_page_load_timeout(self.timeout)  
                html_raw = self.driver.page_source
                rec.close()
        except Exception as e:
            return "null"

        html = BeautifulSoup(html_raw, "html.parser")
        html_scripts = html.find_all("script")  
        # print(html_scripts)
        script_array = {}
        script_temp = ""
        purl = ""
        for html_script in html_scripts:
            script_src = html_script.get("src")  
            if script_src == None:
                script_temp += html_script.get_text() + "\n"
            else:
                purl = self.process_url(self.url, script_src) 
            script_array[purl] = self.Extract_html(purl)
        script_array[self.url] = script_temp
        self.js_url = []  
        for script in script_array: 
            # print(script)
            temp_urls = self.extract_URL(script_array[script])  
            if len(temp_urls) == 0: continue
            for temp_url in temp_urls:
                self.js_url.append(self.process_url(script, temp_url)) 
        result = []

        url_raw = urlparse(self.url)
        domain = url_raw.netloc
        positions = self.find_last(domain, ".")
        miandomain = domain

        for singerurl in self.js_url:
            if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
            suburl = urlparse(singerurl)
            subdomain = suburl.netloc
            if miandomain in subdomain or subdomain.strip() == "":
                if singerurl.strip() not in result:
                    result.append(singerurl)
        self.driver.quit()
        return result

    def Findsub(self,urls):
        url_raw = urlparse(self.url)
        domain = url_raw.netloc
        miandomain = domain
        positions = self.find_last(domain, ".")
        if len(positions) > 1:miandomain = domain[positions[-2] + 1:]
        subdomains = []
        for url in urls:
            suburl = urlparse(url)
            subdomain = suburl.netloc
            #print(subdomain)
            if subdomain.strip() == "": continue
            if miandomain in subdomain:
                if subdomain not in subdomains:
                    subdomains.append(subdomain)
        self.driver.quit()
        return subdomains


    def process_url(self,URL, re_URL):
        black_url = ["javascript:"]	
        URL_raw = urlparse(URL)
        ab_URL = URL_raw.netloc
        host_URL = URL_raw.scheme
        if re_URL[0:2] == "//":
            result = host_URL  + ":" + re_URL
        elif re_URL[0:4] == "http":
            result = re_URL
        elif re_URL[0:2] != "//" and re_URL not in black_url:
            if re_URL[0:1] == "/":
                result = host_URL + "://" + ab_URL + re_URL
            else:
                if re_URL[0:1] == ".":
                    if re_URL[0:2] == "..":
                        result = host_URL + "://" + ab_URL + re_URL[2:]
                    else:
                        result = host_URL + "://" + ab_URL + re_URL[1:]
                else:
                    result = host_URL + "://" + ab_URL + "/" + re_URL
        else:
            result = URL
        return result

    def deal_cookie(self,cookie_txt):
        # 需要验证一次 否则无法set-cookie
        self.driver.get(self.url)
        with open(cookie_txt,"r") as file:
            cookies = file.read()
        for cookie in cookies.split("; "):
            form = {}
            form['domain'] = "."+self.domain
            form['name'] = cookie.split("=",1)[0]
            form['value'] = cookie.split("=",1)[1]
            self.driver.delete_cookie(form['name'])
            self.driver.add_cookie(cookie_dict=form)
        return True

    def Extract_html(self,URL):
        try:
            raw = requests.get(URL, headers = self.spiderHeader,timeout=3, verify=False)
            raw = raw.content.decode("utf-8", "ignore")
            return raw
        except:
            return None

    def extract_URL(self,JS):
        pattern_raw = r"""
        (?:"|')                               # Start newline delimiter
        (
            ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
            [^"'/]{1,}\.                        # Match a domainname (any character + dot)
            [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
            |
            ((?:/|\.\./|\./)                    # Start with /,../,./
            [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
            [^"'><,;|()]{1,})                   # Rest of the characters can't be
            |
            ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
            [a-zA-Z0-9_\-/]{1,}                 # Resource name
            \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
            (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
            |
            ([a-zA-Z0-9_\-]{1,}                 # filename
            \.(?:php|asp|aspx|jsp|json|
                action|html|js|txt|xml)             # . + extension
            (?:\?[^"|']{0,}|))                  # ? mark with parameters
        )
        (?:"|')                               # End newline delimiter
        """
        pattern = re.compile(pattern_raw, re.VERBOSE)
        result = re.finditer(pattern, str(JS))
        if result == None:
            return None
        return [match.group().strip('"').strip("'") for match in result
            if match.group() not in self.js_url]

    def find_last(self,string,str):
        positions = []
        last_position=-1
        while True:
            position = string.find(str,last_position+1)
            if position == -1:break
            last_position = position
            positions.append(position)
        return positions


    

