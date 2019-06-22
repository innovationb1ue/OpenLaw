import requests
import re
import time
from bs4 import BeautifulSoup as bs
import execjs

PRE_SCRIPT_1 = '''

function abc111(){
var document = Object();
document.createElement = function () {
    return 0
}
document.getElementsByTagName = function (a) {
    return [document];
}
document.parentNode = Object();
document.parentNode.insertBefore = function (a,b) {
    return 0;
}'''

PRE_SCRIPT_2 = '''}'''

SCRIPT_PROCESS = '''
function _process(s) {
	var result = s.substring(4, 6).concat('m').concat(s.substring(13, 14)).concat('p').concat(s.substring(8, 12)).concat('u').concat(s.substring(4)).concat('z').concat(s.substring(10, 18));
	return result.substr(0, 32);
};
'''
# type in the SESSION after you login
# 写上你登陆之后的cookie里面的SESSION=的值
SESSION = 'MWQ4OWJiYWQtNTA3Mi00OWNjLWJjYWEtNWFhOGU0NTA3YjI0'
class openLaw():
    def __init__(self):
        self.s = requests.Session()
        self.Header = {'Cookie':'SESSION=MjQxODc0MWItZWRjNC00NWFhLWE4MmQtMDJkODJiYzE3ZDY3',
                       'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"}
        self._process = execjs.compile(SCRIPT_PROCESS)
        self.main()

    def main(self):
        for i in range(1,2):
            i = str(i)
            res1 = self.s.get('http://openlaw.cn/',headers=self.Header)
            print('res1 cookie = ',res1.cookies.get_dict())
            # 在这里修改你想要的日期，修改代码加循环等等...
            res = self.s.get('http://openlaw.cn/search/judgement/advanced?judgeDateBegin=2019-06-01&judgeDateEnd=2019-06-03&page='+i,headers=self.Header)
            content =res.content.decode('utf-8')
            print(content)
            print()
            if "如果你能看到这个" in content:
                self.jsProcess(content)
                content = self.s.get('http://openlaw.cn/search/judgement/advanced?judgeDateBegin=2019-06-01&judgeDateEnd=2019-06-03&page='+i,headers=self.Header).content.decode('utf-8')
            # 返回搜索页面，自己提取url再访问，解析即可
            print(content)
    def jsProcess(self,content):
        # handle the script and get anomynous function
        script = bs(content,'lxml').script.text
        flag = script.find("$")
        script1 = script[:flag]
        script2 = script[flag:]
        flag2 = script2.find('$.$($.$($.$')
        script2 = script2[:flag2] + 'return '+script2[flag2:][:-4]+'.toString();'
        finalScript = PRE_SCRIPT_1 + script1+script2 + PRE_SCRIPT_2
        ctx = execjs.compile(finalScript)
        result =ctx.call("abc111")
        print(result)
        #get Keys
        OPEN_S_INDEX = re.findall('OPEN_S=(.*?);',result)[0][-3:].replace('0','')
        print('OPEN_S_INDEX=',OPEN_S_INDEX)
        temp = re.findall('[a-z0-9]{32}',result)
        SIGNIN_ID = temp[0]
        SIGNIN_UC = temp[1]
        UNDEFINED = temp[2]
        print(temp)
        process = result[result.find('function _process'):result.find('var _switch')]

        OPEN_S = re.findall('[a-z0-9]{32}',script1)[eval(OPEN_S_INDEX)-1]
        OPEN_C = execjs.compile(process).call('_process',re.findall('[a-z0-9]{32}',script1)[eval(OPEN_S_INDEX)-1])
        print('OPEN_S = ',OPEN_S)
        print('OPEN_C = ',OPEN_C)
        # set Cookie
        self.Header['Cookie'] = 'SESSION=%s; OPEN_S=%s; OPEN_C=%s; SIGNIN_ID=%s; SIGNIN_UC=%s;UNDEFINED=%s; Hm_lvt_a105f5952beb915ade56722dc85adf05=1560915411,1560943092,1560944621,1561191343; Hm_lpvt_a105f5952beb915ade56722dc85adf05=1561192080' % (SESSION,OPEN_S,OPEN_C,SIGNIN_ID,SIGNIN_UC,UNDEFINED)
        self.Header['Referer'] = 'http://openlaw.cn/search/judgement/default?type=&typeValue=&lawyerId=&lawFirmId=&courtId=&keyword='
        self.Header['Host'] = 'openlaw.cn'
        print("更新后Header=",self.Header)


if __name__ == '__main__':
    e  = openLaw()
