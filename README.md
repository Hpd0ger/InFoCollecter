# InFoCollecter
针对域名/页面的接口爬取，递归模式入库

## 主要功能

* 根据给出的域名，调用Jsfinder去爬取每个页面的api接口、标签，并判断爬取的接口/标签是否属于域名下资产：同域名下资产则入库后队列继续递归爬取，否则直接入库。

* 获取每个域名主页相应的title、状态码、html大小并入库存储

* 携带cookie去递归爬取页面接口，针对单点登陆的情况，或者页面权鉴的情况

* 支持爬取单页面的接口，可以选择一层/深度爬取

* 把数据库所有结果导出到txt，以便转存数据&进一步扫描器测试接口

## 配置说明

### 配置chromedriver

下载chromedriver后放入python根目录或加入全局环境变量
下载地址:http://npm.taobao.org/mirrors/chromedriver/ 

注:必须要与当前chrome浏览器的版本匹配

### 同目录下config.ini中配置config
```
[server]
ip: 222.18.158.226
port: 65530
database: Baidu
account: 
password: 
```

## 使用说明
### 参数说明
* -u:指定url爬取
* -i:深度爬取flag标志
* -d:指定域名，深度爬取/携带cookie的时候必须存在的参数
* -c:指定cookie文件


### 携带COOKIE
需要在脚本同目录下的cookies.txt中填入自己的cookie，形式如下
![image_1dl0v63sn10c71i9m18q31tkikgk20.png-111.4kB][1]

### 爬取单页面

* 只爬取单个页面，不携带cookie，以爬取asrc为例
```
python3 SubdoaminUp.py -u https://security.alibaba.com//leak/profile.htm
```
![image_1dkvvlvk71d4noejcm7ljb1e30m.png-205.7kB][2]

* 携带cookie进行深度爬取
```
python3 SubdoaminUp.py -u https://security.alibaba.com//leak/profile.htm -c cookies.txt -d alibaba.com
```
![image_1dkvvn6pf1utj18rs1cnk4201b5s13.png-181.7kB][3]


### 递归爬取域名入库

在subdomain.txt中加入域名
```
union.baidu.com
mssp.baidu.com
yingxiao.baidu.com
baiyi.baidu.com
developer.baidu.com
bes.baidu.com
tongji.baidu.com
dmp.baidu.com
jianyi.baidu.com
absample.baidu.com
```

* 跟单页面爬取一样，可以选择深度爬取/单页面爬取&是否携带cookie
```
python3 SubdoaminUp.py -d oppo.com -i 
```

![image_1dl0vvkav5sv1lnsjm7vl7are29.png-1111.3kB][4]

![](https://s2.ax1x.com/2019/09/18/nTPhsU.jpg)





  [1]: http://static.zybuluo.com/1160307775/i8kpgm828h9vh7cjwzcu2hni/image_1dl0v63sn10c71i9m18q31tkikgk20.png
  [2]: http://static.zybuluo.com/1160307775/sruhzvi2jd6875gh61eoajmc/image_1dkvvlvk71d4noejcm7ljb1e30m.png
  [3]: http://static.zybuluo.com/1160307775/0lqnghbrfjxi3penyu388zqy/image_1dkvvn6pf1utj18rs1cnk4201b5s13.png
  [4]: http://static.zybuluo.com/1160307775/iajcefzdiq9wbkkrrh9r2h04/image_1dl0vvkav5sv1lnsjm7vl7are29.png
