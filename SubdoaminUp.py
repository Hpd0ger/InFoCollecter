#! /usr/bin/python3
from Jsfinder import Jsfinder
from bs4 import BeautifulSoup
import requests,pymongo,socket,datetime,argparse,sys
import configparser


def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython3 ' + sys.argv[0] + " -u http://www.baidu.com")
    parser.add_argument("-u", "--url", help="The single url")
    parser.add_argument("-d", "--domain", help="The domain you wanna collect")
    parser.add_argument("-c", "--cookie", help="The file which you saved cookies in")
    parser.add_argument("-i", "--flag",help="The script page deep inside", action="store_true")
    parser.add_argument("-e", "--export", help="Export something into txt")
    return parser.parse_args()


class DomainUp:
    def __init__(self,domain,flag=False,cookie=None):
        self.subdomainTXT = 'subdomain.txt'
        self.domain = domain
        self.cookie = cookie
        self.Jsfinder = Jsfinder.Jsfinder()
        self.flag = flag
        self.subdomainKb = []  
        self.subdomainFia = []  
        
    def InitDatabase(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        ip = config.get('server','ip')
        port  = int(config.get('server','port'))
        database  = config.get('server','database')
        account = config.get('server','account')
        password = config.get('server','password')
        
        mongo_client = pymongo.MongoClient(host=ip, port=port)
        self.mongo_database = mongo_client[database]

        # 默认未授权，若存在账号密码则需要认证
        if(account and password):
            self.mongo_database.authenticate(account, password)  


# 获取domain列表，来源txt
    def GetdomainList(self):
        with open(self.subdomainTXT) as file:
            for subdomain in file.readlines():
                if subdomain: self.subdomainKb.append(subdomain.strip('\n'))
                else: file.close()
        

# 对单一url进行api爬取
    def Searchapi(self,url):
        subApis = self.Jsfinder.Judge2api(url,self.domain,self.cookie,self.flag)
        print("[*]接口列表,一共存在"+str(len(subApis))+"个结果:"+'\n')
        for sub in subApis:print(sub+'\n')

# 数据入库
    def Insertdomain(self):
        self.InitDatabase()
        self.GetdomainList()
        subdomains = self.subdomainKb
        self.SubFilter(subdomains)
        print(self.subdomainFia)

        for subdomain in self.subdomainFia:
            print("[-]正在整理域名:",subdomain)
            subApis = self.Jsfinder.Judge2api("http://"+subdomain,self.domain,self.cookie,self.flag)
            print("[*]接口列表:",subApis)
            subdomainJs = self.Jsfinder.Findsub(subApis)
            print("[@]api搜集的子域名:",subdomainJs)
            self.SubFilter(subdomainJs)  # 再次去重
            self.InsertMongo(subdomain,subApis)           


    def Selectdomain(self,subdomain):
        result = self.mongo_database[self.domain].find_one({"domain": subdomain})
        if result:return True
        else:return False  # 暂时return一个布尔值

    def Export(self,output):
        # print(output)
        results = self.mongo_database[self.domain].find({'apis':{'$ne':"null"}})
        for result in results:
            for api in result['apis']:
                with open(output,'a') as file:
                    file.write(api+'\n')
        print("[!@!]所有结果已导出在",output)


    def InsertMongo(self,subdomain,apis):
        if self.Selectdomain(subdomain) == False:
            title,size,status = self.Assort(subdomain)
            time = datetime.datetime.now().strftime('%Y-%m-%d')
            data = dict(domain = subdomain,apis = apis, title=title, html_size=size, status = status, insert_time=time)
            self.mongo_database[self.domain].insert_one(data)
            print(subdomain,"域名插入成功")
        else:
            print("域名已存在")

    def SubFilter(self,subdomainList):
        # print(subdomainList1,"分割",subdomainList2)
        rubbish = 0
        for domain in subdomainList:
            if domain not in self.subdomainFia:
                self.subdomainFia.append(domain)
            else:
                rubbish +=1
                continue
        print("[+]:本次共整合",len(subdomainList),"个子域名,删除",rubbish,"个重复域名...")

    def Assort(self,subdomain):
        url = "http://"+subdomain
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www.google.com',
            'X-Forwarded-For': '127.0.0.1'
        }

        try:
            rec = requests.get(url=url,timeout=5,headers=header,allow_redirects=False)
            if rec.status_code == 200:
                rec.encoding = rec.apparent_encoding
                soup = BeautifulSoup(rec.text,"html.parser")
                title = soup.title.string.strip('\n')
                status = "200"
                size = len(list(rec.text))
                print(title)
            elif rec.status_code == 302 or rec.status_code == 301:
                rec_302 = requests.get(url=url,headers=header)
                rec_302.encoding = rec_302.apparent_encoding
                soup = BeautifulSoup(rec_302.text,"html.parser")
                title = soup.title.string.strip('\n')
                status = "302"
                size = len(list(rec_302.text))
                print(title)
            else:
                title = "null"
                status = str(rec.status_code)
                size = 0
        except:
            status = size = title = "null"

        return title,size,status

if __name__ == "__main__":
    args = parse_args()
    if args.url == None and args.export == None:  # 开启domain模式
        if args.domain != None:
            DomainUp(args.domain,args.flag,args.cookie).Insertdomain()
        else:
            print("[-]please give me a domain name"+'\n')
    elif args.export == None: #开启url模式
        if args.cookie != None:
            if args.domain != None:
                DomainUp(args.domain,args.flag,args.cookie).Searchapi(args.url) #还未做cookie判断
            else:print("[-]please give me a domain name"+'\n')
        else:DomainUp("null",args.flag).Searchapi(args.url)
    else: #开启导出txt模式
        if args.domain != None:
            DomainUp(args.domain,args.flag,args.cookie).Export(args.export)
        else:print("[-]please give me a domain name"+'\n')
