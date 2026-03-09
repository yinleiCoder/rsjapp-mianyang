import json
import math
import requests
import traceback
import execjs
import ddddocr
import video_helper

class RsjApp:
    def __init__(self):
        self.headers = {}
        self.cookies = {}
        self.all_courses = []
    
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
        self.all_courses = []
        for page in range(page_total):
            course_data = self.obtain_course_list(str(page + 1))
            self.all_courses.extend(course_data["list"])
        return self.all_courses

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

    def find_course_by_name(self, course_name):
        for item in self.all_courses:
            if item.get('adz121') == course_name:
                return item
        return None

    def select_course(self, course_name='') -> str:
        current_course = self.find_course_by_name(course_name)
        if current_course is None or current_course["adz175"] == 1:
            return f"{course_name} 已选课"
        
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
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/myd002.do"
        jscode = open('app.js', 'r', encoding='utf-8').read()
        payload = execjs.compile(jscode).call('selectCourse', current_course["adz280"], self.user_id)
        data = {
            "adz280": payload["adz280"],
            "aac001": payload["aac001"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        if decrypted_data["resultData"]["data"]["code"] == "1" and decrypted_data["resultData"]["data"]["message"] == "成功":
            return f"{course_name} 选课成功"
        else:
            return f"{course_name} 选课失败"
    
    def obtain_chapter_list(self, course_id):
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://rsjapp.mianyang.cn",
            "Pragma": "no-cache",
            "Referer": f"https://rsjapp.mianyang.cn/jxjy/pc/zxxx_1646619915000/index.jhtml?adz280={course_id}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/myd003.do"
        jscode = open('app.js', 'r', encoding='utf-8').read()
        payload = execjs.compile(jscode).call('getChapterList', course_id, self.user_id)
        data = {
            "adz280": payload["adz280"],
            "aac001": payload["aac001"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        return decrypted_data['resultData']['data']['data']

    def display_course_chapter_data(self, course_name='') -> str:
        current_course = self.find_course_by_name(course_name)
        course_id = current_course["adz280"]
        # 获取某课程的章节视频数据
        chapter = self.obtain_chapter_list(course_id)
        display_content = ''
        display_content += f'课程标题: 《{chapter['adz121']}》\n'
        display_content += f'课程选课状态：{"已选课" if current_course['adz175'] == 1 else "未选课"}\n课程学习状态: {"已学完" if current_course['study'] == 1 else "未学完"}\n课程考试状态: {"已考试" if current_course['test'] == 1 else "未考试"}\n'
        display_content += f'课程类别: {chapter['adz123']}\n课程时间: {chapter['aae036']}\n'
        display_content += f'课程简介: {chapter['adz124']}\n\n'

        directories = chapter['directory']
        for directory in directories:
            display_content += f'视频ID: {directory['adz290']}\n'
            display_content += f'视频标题: {directory['adz125']}\n'
            display_content += f'视频学习状态: {"未学完" if directory['videoOver'] == "0" else "已学完"}\n'
            display_content += '\n'
        return display_content

    def rush_course_by_name(self, course_name='', log_callback=None, progress_callback=None):
        if log_callback is not None:
            log_callback(f"程序开始学习课程：《{course_name}》", "INFO")

        current_course = self.find_course_by_name(course_name)
        if current_course is None or current_course["study"] == 1:
            if log_callback is not None:
                log_callback(f"{course_name} 已学习，程序跳过该课程学习", "ERROR")
                return

        course_id = current_course["adz280"]
        # 获取某课程的章节视频数据
        chapter = self.obtain_chapter_list(course_id)
        directories = chapter['directory']
        total = len(directories)
        is_finished_course = False
        for index, video_data in enumerate(directories):
            if log_callback is not None:
                log_callback(f"({index+1}/{total})开始刷章节视频：{video_data["adz125"]}", "INFO")
            is_finished_course = self.rush_chapter_video(course_id, video_data)
            if progress_callback is not None:
                progress_callback((index + 1) / total)

        if log_callback is not None and is_finished_course:
            log_callback(f"《{course_name}》成功完成共{len(directories)}个章节视频刷课！！！", "SUCCESS")
                
    def rush_chapter_video(self, course_id, video_data) -> bool:
        video_id = video_data['adz290']
        # 1. 初始化视频信息
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://rsjapp.mianyang.cn",
            "Pragma": "no-cache",
            "Referer": f"https://rsjapp.mianyang.cn/jxjy/pc/zxxx_1646619915000/index.jhtml?adz280={course_id}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/myd004.do"
        jscode = open('app.js', 'r', encoding='utf-8').read()
        payload = execjs.compile(jscode).call('getVideoStructure', video_data["adz127"], video_id,self.user_id)
        data = {
            "adz127": payload["adz127"],
            "adz290": payload["adz290"],
            "aac001": payload["aac001"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        antiStealingLinkMap = decrypted_data["resultData"]["data"]["data"]

        # 2. 获取mp4视频信息, 得到视频总时长
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getVideoData.do"
        payload = execjs.compile(jscode).call('getVideoDetailData', antiStealingLinkMap.get("adz166", ""), antiStealingLinkMap["adz168"])
        data = {
            "fileId": payload["fileId"],
            "adz168": payload["adz168"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        data_dict = decrypted_data['resultData']
        file_format, file_id = data_dict["fileFormat"], data_dict["fileId"]
        video_structure = {
            "src": f"https://rsjapp.mianyang.cn/jxjy/psp/resource/ZJSITE/CYYQPC/video/videoFile/{file_id}",
            "type": f"video/{file_format}"
        }
        video_structure["duration"] = video_helper.obtain_video_duration_by_ffprobe(video_structure["src"])

        # 3. 秒刷视频
        url = 'https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/myd007.do'
        payload = execjs.compile(jscode).call('rushWatchCourse', video_id, self.user_id, video_structure["duration"])
        data = {
            "adz290": payload["adz290"],
            "aac001": payload["aac001"],
            "adz341": payload["adz341"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        
        # 4. 保存播放记录
        if decrypted_data["resultData"]["data"]["code"] == "1":
            url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/myd005.do"
            payload = execjs.compile(jscode).call('saveVideoPlayRecord', video_id, self.user_id, video_structure["duration"])
            data = {
                "adz290": payload["adz290"],
                "aac001": payload["aac001"],
                "adz341": payload["adz341"],
                "encodeKey": payload["encodeKey"]
            }
            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
            decrypted_data = self.decrypt_data(response.text.strip('"'))
            # if decrypted_data["resultData"]["data"]["code"] == "1" and decrypted_data["resultData"]["data"]["data"]["complete"] == "1":
            if decrypted_data["resultData"]["data"]["code"] == "1":
                return True
        else:
            return False

if __name__ == "__main__":
    app = RsjApp()
    app.login("510722199805052850", "Yl13795950539@")
    all_courses_data = app.obtain_course_data()
    # app.select_course('2011年：低碳经济与可持续发展')
    print(app.rush_course_by_name('低碳经济与可持续发展'))