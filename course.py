import json
import math
import requests
import traceback
import execjs
import ddddocr
from datetime import datetime
import time
import video_helper

class RsjApp:
    def __init__(self):
        self.headers = {}
        self.cookies = {}
        self.all_courses = []
        self.adz012 = 1# 0代表测试考试，1代表正式考试
    
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
            return f"{course_name} 选课成功！"
        else:
            return f"{course_name} 选课失败！"
    
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

    def obtain_exam_info(self, course_name='', log_callback=None,
progress_callback=None):
        current_course = self.find_course_by_name(course_name)
        # 1. 查询卷面头部信息
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://rsjapp.mianyang.cn",
            "Pragma": "no-cache",
            "Referer": f"https://rsjapp.mianyang.cn/jxjy/pc/ksz_1646185391000/index.jhtml?&adz012={self.adz012}&adz280={current_course["adz280"]}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/mye001.do"
        jscode = open('app.js', 'r', encoding='utf-8').read()
        payload = execjs.compile(jscode).call('getExamTitle', self.user_id, self.adz012, current_course["adz280"])
        data = {
            "aac001": payload["aac001"],
            "adz012": payload["adz012"],
            "adz280": payload["adz280"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        if decrypted_data["resultData"]["data"]["code"] == "1":
            decrypted_data = decrypted_data["resultData"]["data"]["data"]
        else:
            if log_callback is not None:
                log_callback(f"程序获取考试试卷失败，请重试！！！", "ERROR")
            return

        paper_header_data = {
            "adz401": decrypted_data["adz401"],# 试卷题目
            "adz420": decrypted_data["adz420"],# 拿到人员考试信息
            "cunt": decrypted_data["cunt"],# 题目数量
            "endtime": decrypted_data["endtime"],# 结束时间
            "starttime": decrypted_data["starttime"],# 开始时间
            "adz614": decrypted_data["adz614"],# 考试时长
            "adz614_remain": decrypted_data["adz614_remain"]# 剩余时间秒数
        }
        if log_callback is not None:
            log_callback(f"考试试卷：{paper_header_data["adz401"]}", "INFO")
            log_callback(f"考试题目数量：{paper_header_data["cunt"]}", "INFO")
            log_callback(f"考试开始时间：{datetime.fromtimestamp(paper_header_data["starttime"] / 1000)}", "INFO")
            log_callback(f"考试开始时间：{datetime.fromtimestamp(paper_header_data["endtime"] / 1000)}", "INFO")
            log_callback(f"考试限定时长：{paper_header_data["adz614"]} 分钟", "INFO")

        # 2. 查询答题卡
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/mye002.do"
        payload = execjs.compile(jscode).call('getExamAnswerCard', self.user_id, self.adz012, current_course["adz280"], paper_header_data["adz420"])
        data = {
            "aac001": payload["aac001"],
            "adz012": payload["adz012"],
            "adz280": payload["adz280"],
            "adz420": payload["adz420"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        dataSource = []# 所有题目
        if decrypted_data["resultData"]["data"]["code"] == "1":
            questionsMap = decrypted_data["resultData"]["data"]["data"]["questionsMap"]
            quesiton_list_1, quesiton_list_2, quesiton_list_3 = questionsMap["questionList_1"],questionsMap["questionList_2"],questionsMap["questionList_3"]
            dataSource.extend(quesiton_list_1)
            dataSource.extend(quesiton_list_2)
            dataSource.extend(quesiton_list_3)
            # '单选题','不定项选择题','判断题'
            # print(dataSource)
        else:
            if log_callback is not None:
                log_callback(f"程序获取答题卡失败，请重试！！！", "ERROR")
            return
        
        total = len(dataSource)
        last_question = {}# 最后一道题
        for index, question in enumerate(dataSource):
            # 3. 查询某道试题（需要轮询查询所有题目）
            url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/mye003.do"
            payload = execjs.compile(jscode).call('getExamSingleQuestionDetail', self.user_id, self.adz012, current_course["adz280"], paper_header_data["adz420"], question["adz010"])
            data = {
                "aac001": payload["aac001"],
                "adz012": payload["adz012"],
                "adz280": payload["adz280"],
                "adz420": payload["adz420"],
                "adz010": payload["adz010"],
                "encodeKey": payload["encodeKey"]
            }
            response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
            decrypted_data = self.decrypt_data(response.text.strip('"'))
            # print(decrypted_data)
            if decrypted_data["resultData"]["data"]["code"] == "1":
                # 单道题目的信息
                questionsMap = decrypted_data["resultData"]["data"]["data"]["questionMap"]
                option, option_list = questionsMap["option"], questionsMap["optionList"]
                option_type = option["adz001"]# 题目类型 "1" "3" "2"
                adz430 = option["adz430"]
                adz432 = option["adz006"]# adz432是用户提交的选项，如果不是多选就是A B C D，如果是多选。option["adz006"]为正确答案，# 正确答案："adz006": "C"， "adz006": "B,C,D,E" "adz006": "B"

                if index+1 == total:# 最后一道题目的信息作为提交整个试卷
                    last_question["adz001"] = option_type
                    last_question["adz430"] = adz430
                    last_question["adz432"] = adz432
                    last_question["adz010"] = question["adz010"]


                # 4. 提交本道题的答案
                url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/mye004.do"
                payload = execjs.compile(jscode).call('submitQuestionRightAnswer', self.user_id, self.adz012, current_course["adz280"], paper_header_data["adz420"], question["adz010"], option_type, adz430, adz432)
                data = {
                    "aac001": payload["aac001"],
                    "adz012": payload["adz012"],
                    "adz280": payload["adz280"],
                    "adz420": payload["adz420"],
                    "adz010": payload["adz010"],
                    "adz001": payload["adz001"],
                    "adz430": payload["adz430"],
                    "adz432": payload["adz432"],
                    "encodeKey": payload["encodeKey"]
                }
                response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
                decrypted_data = self.decrypt_data(response.text.strip('"'))
                # print(decrypted_data)
                if decrypted_data["resultData"]["data"]["code"] == "1":
                    # 本题目已作答
                    if log_callback is not None:
                        log_callback(f"({index+1}/{total})题目: {option["adz002"]} ", "INFO")
                        log_callback(f"({index+1}/{total})正确答案: {option["adz006"]} ", "INFO")
                        if progress_callback is not None:
                            progress_callback((index + 1) / total)
                else:
                    if log_callback is not None:
                        log_callback(f"{index+1}/{total})程序提交答案失败，请重试！！！", "ERROR")
                    return
            else:
                if log_callback is not None:
                    log_callback(f"{index+1}/{total})程序查询本道题目的正确答案失败，请重试！！！", "ERROR")
                return
            
        # 5. 提交试卷（所有题目都提交完）[最后一个题目的答案]
        # 正式考试必须要10分钟以上才能交卷
        self.submit_paper(jscode, current_course["adz280"], paper_header_data["adz420"], last_question["adz010"], last_question["adz001"], last_question["adz430"], last_question["adz432"], paper_header_data["adz401"], paper_header_data["starttime"], log_callback)

        # 6. 查询考试成绩
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://rsjapp.mianyang.cn",
            "Pragma": "no-cache",
            "Referer": f"https://rsjapp.mianyang.cn/jxjy/pc/ksjg_1647414078000/index.jhtml?&adz420={paper_header_data["adz420"]}&adz012={self.adz012}&adz280={current_course["adz280"]}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/mye006.do"
        payload = execjs.compile(jscode).call('queryPaperScore', paper_header_data["adz420"], self.user_id)
        data = {
            "adz420": payload["adz420"],
            "aac001": payload["aac001"],
            "encodeKey": payload["encodeKey"]
        }
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        if decrypted_data["resultData"]["data"]["code"] == "1":
            if log_callback is not None:
                log_callback(f"试卷《{paper_header_data["adz401"]}》考试成绩分数：{decrypted_data["resultData"]["data"]["data"]["adz424"]} 分", "SUCCESS")
        else:
            if log_callback is not None:
                log_callback(f"试卷《{paper_header_data["adz401"]}》考试成绩获取失败，请重试！！！", "ERROR")
            return
    
    def submit_paper(self, jscode, adz280, adz420, adz010, adz001, adz430, adz432, adz401, starttime,log_callback):
        url = "https://rsjapp.mianyang.cn/jxjy/pc/lcService/getData/mye005.do"
        payload = execjs.compile(jscode).call('submitPaper', self.user_id, self.adz012, adz280, adz420, adz010, adz001, adz430, adz432)
        data = {
            "aac001": payload["aac001"],
            "adz012": payload["adz012"],
            "adz280": payload["adz280"],
            "adz420": payload["adz420"],
            "adz010": payload["adz010"],
            "adz001": payload["adz001"],
            "adz430": payload["adz430"],
            "adz432": payload["adz432"],
            "encodeKey": payload["encodeKey"]
        }
        submit_time = int(starttime) + 10 * 60 * 1000# 提交试卷时间
        while True:
            now = int(time.time() * 1000)
            if now >= submit_time:
                break
            remain = int((submit_time - now) / 1000)
            if log_callback is not None:
                log_callback(f"距离交卷还有 {remain} 秒", "WARNING")
            time.sleep(min(remain, 10))
        
        response = requests.post(url, headers=self.headers, cookies=self.cookies, data=data)
        decrypted_data = self.decrypt_data(response.text.strip('"'))
        if decrypted_data["resultData"]["data"]["code"] == "1":
            if log_callback is not None:
                log_callback(f"试卷《{adz401}》提交成功", "SUCCESS")
                return
        else:
            if log_callback is not None:
                # 正式考试要10分钟后才能交卷
                log_callback(f"试卷《{adz401}》提交失败：{decrypted_data["resultData"]["data"]["msg"]}", "ERROR")
                return

if __name__ == "__main__":
    app = RsjApp()
    app.login("510722199805052850", "Yl13795950539@")
    all_courses_data = app.obtain_course_data()
    # app.select_course('2011年：低碳经济与可持续发展')
    # print(app.rush_course_by_name('低碳经济与可持续发展'))
    app.obtain_exam_info('2024年：数字经济与创新驱动发展等')