import json
import math
import requests
import traceback
import execjs
import ddddocr

class RsjApp:
    def __init__(self):
        self.headers = {}
        self.cookies = {}
    
    def verify_code(self) -> str:
        self.headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://rsjapp.mianyang.cn/jxjy/pc/member/login.jhtml",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/code/getImgCode.do"
        params = {
            "sid": execjs.eval('Math.random()')
        }
        response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)
        code = ''
        with open('verifyCode.jpg', 'wb') as file:
            file.write(response.content)
            ocr = ddddocr.DdddOcr()
            code = ocr.classification(response.content)
        if len(code) != 4 and not code.isdigit():
            return self.verify_code()
        return code

    def login(self, account, password) -> str:
        # 1.Cookies
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": "https://rsjapp.mianyang.cn/jxjy/pc/index.jhtml",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/member/login.jhtml"
        response = requests.get(url, headers=self.headers)
        self.cookies["JSESSIONID"] = response.cookies.get("JSESSIONID")
        
        # 2.验证码
        code = self.verify_code()
        print(f'程序OCR验证码: {code}')

        # 3. 登录
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://rsjapp.mianyang.cn",
            "Pragma": "no-cache",
            "Referer": "https://rsjapp.mianyang.cn/jxjy/pc/member/login.jhtml",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcUserCoreController/login.do"
        jscode = open('course.js', 'r', encoding='utf-8').read()
        payload = execjs.compile(jscode).call('encryptLoginPayload', account, password, code)
        data = {
            "pspUserAccount": payload["pspUserAccount"],
            "pspUserPwd": payload["pspUserPwd"],
            "verCode": payload["verCode"],
            "loginType": payload["loginType"],
            "pspUserType": payload["pspUserType"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        # 4. 解密响应数据
        decrypted_data = execjs.compile(jscode).call('dealAes', response.text.strip('"'))
        try:
            print(decrypted_data)
            data = decrypted_data['resultData']
            self.user_id = data["aac001"]
            self.user_info = data["userInfo"]
            return ""
        except Exception:
            traceback.print_exc()
            return decrypted_data["message"]
    
    def decrypt_data(self, encrypted_data) -> dict:
        decrypted_data = execjs.compile(open('app.js', 'r', encoding='utf-8').read()).call('decryptData', encrypted_data)
        return decrypted_data

    def obtain_course_data(self):
        course_data = self.obtain_course_list()
        page_total = math.ceil(int(course_data["total"])/int(course_data["size"]))
        all_courses = []
        for page in range(page_total):
            course_data = self.obtain_course_list(str(page + 1))
            all_courses.extend(course_data["list"])
        return all_courses

    def obtain_course_list(self, page="1") -> dict:
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://rsjapp.mianyang.cn",
            "Pragma": "no-cache",
            "Referer": "https://rsjapp.mianyang.cn/jxjy/pc/wdkc_1646108788000/index.jhtml",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/myd001.do"
        jscode = open('app.js', 'r', encoding='utf-8').read()
        payload = execjs.compile(jscode).call('getCourseList', self.user_id, page)
        data = {
            "pageNum": payload["pageNum"],
            "size": payload["size"],
            "adz121": payload["adz121"],
            "adz123": payload["adz123"],
            "adf088": payload["adf088"],
            "sort": payload["sort"],
            "adz280": payload["adz280"],
            "aac001": payload["aac001"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        return decrypted_data["resultData"]["data"]["data"]

if __name__ == "__main__":
    app = RsjApp()
    app.login("510722199805052850", "Tangtao1998@")
    all_courses_data = app.obtain_course_data()
    print(all_courses_data)