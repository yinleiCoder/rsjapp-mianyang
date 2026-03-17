import datetime
import customtkinter
import queue
import threading
from course import RsjApp

# 弹窗----------------------------------------------------------------------
class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400*200")
        
    def display_content(self, text):
        self.label = customtkinter.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=20)

# 日志面板-------------------------------------------------------------------
class LogFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(
            self,
            font=("Consolas", 13),
            text_color="#00FF00",
            fg_color="#000000"
        )
        # self.textbox.configure(state="disabled")
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.tag_config("INFO", foreground="#00FF00")
        self.textbox.tag_config("ERROR", foreground="#FF5555")
        self.textbox.tag_config("SUCCESS", foreground="#00FFFF")
        self.textbox.tag_config("WARNING", foreground="#FFFF55")
        

    def write(self, text, level="INFO"):
        # self.textbox.delete("0.0", "end")
        now = datetime.datetime.now().strftime("%H:%M:%S")
        log = f"[{now}] {level:<7} {text}\n"
        self.textbox.insert("end", log, level)
        self.textbox.see("end")

# 登录面板----------------------------------------------------------------
class LoginFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color="transparent")

        self.title = customtkinter.CTkLabel(self, text="绵阳市继续教育公需课", font=("微软雅黑", 18))
        self.title.grid(row=0, column=0, padx=10, pady=(40, 20), sticky="ew")

        self.account_entry = customtkinter.CTkEntry(self, placeholder_text='身份证号')
        self.account_entry.grid(row=1, column=0, padx=40, pady=10, sticky="ew")

        self.password_entry = customtkinter.CTkEntry(self, placeholder_text='密码', show="*")
        self.password_entry.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        self.login_button = customtkinter.CTkButton(self, text="登录", command=self.login)
        self.login_button.grid(row=3, column=0, padx=40, pady=20, sticky="ew")

    def login(self):
        account = self.account_entry.get()
        password = self.password_entry.get()
        message = self.app.login(account, password)
        if message:
            error_login_window = ToplevelWindow(self)
            error_login_window.focus()
            error_login_window.title('登录失败')
            error_login_window.display_content(message)
        else:
            self.master.title(f"《绵阳市专业技术人员继续教育公需科目培训平台》- {self.app.user_info.get("aac003", self.app.user_info.get("aac002", "用户信息失败"))}")
            self.master.do_main()

# 课程面板
class CourseFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure((0, 1), weight=1)
        self.values = values
        self.checkboxes = []

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(self, text=value["adz121"])
            if i % 2:
                checkbox.grid(row=i, column=i%2, padx=10, pady=(10, 0), sticky="w")
            else:
                checkbox.grid(row=i+1, column=i%2, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        selected_courses = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                selected_courses.append(checkbox.cget("text"))
        return selected_courses

# 主屏幕----------------------------------------------------------------
class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        # 消息队列
        self.log_queue = queue.Queue()
        # tkinter定时读取日志
        self.after(200, self.process_log_queue)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,6), weight=1)
        self.grid_rowconfigure((7, 8), weight=0)

        self.course_frame = CourseFrame(self, title="全部课程", values=self.app.obtain_course_data())
        self.course_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.button = customtkinter.CTkButton(self, text="查看课程信息", command=self.show_course_infomation)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.button = customtkinter.CTkButton(self, text="选课、刷课", command=self.rush_course_callback)
        self.button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.button = customtkinter.CTkButton(self, text="自动考试", command=self.rush_exam_callback)
        self.button.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        self.log_frame = LogFrame(self)
        self.log_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        self.log_frame.write(f'欢迎 {app.user_info["adz503_desc"]}/{app.user_info["adz501"]}/{app.user_info["adz50b_desc"]}/{app.user_info["aac003"]}！')

        self.current_course_label = customtkinter.CTkLabel(
            self,
            text="请选择课程并开始学习",
            font=("微软雅黑", 12)
        )
        self.current_course_label.grid(row=7, column=0, padx=10, pady=(5,0), sticky="w")
        self.progressbar = customtkinter.CTkProgressBar(self, orientation="horizontal")
        self.progressbar.grid(row=8, column=0, padx=0, pady=(0,0), sticky="ew")
        self.progressbar.set(0)

    # 刷课
    def rush_course_callback(self):
        self.progressbar.set(0)
        courses = self.course_frame.get()
        thread = threading.Thread(
            target=self.rush_course_thread,
            args=(courses,),
            daemon=True
        )
        thread.start()
    
    # 子线程刷课
    def rush_course_thread(self, selected_courses):
        total = len(selected_courses)
        for index, course_name in enumerate(selected_courses):
            self.update_current_course(course_name, index, total)
            self.after(0, lambda: self.progressbar.set(0))
            self.log_queue.put((f'程序开始处理课程：《{course_name}》', "WARNING"))
            self.log_queue.put((self.app.select_course(course_name), "INFO"))

            # 刷课
            self.app.rush_course_by_name(
                course_name,
                log_callback=self.log_callback,
                progress_callback=self.update_progress
            )
    
    def log_callback(self, message, level="INFO"):
        self.log_queue.put((message, level))

    def update_progress(self, value):
        self.after(0, lambda: self.progressbar.set(value))

    def update_current_course(self, course_name, index, total):
        self.after(0, lambda: self.current_course_label.configure(text=f'{index+1}/{total} :《{course_name}》'))
    
    def show_course_infomation(self):
        courses = self.course_frame.get()
        self.log_frame.write("正在查询课程信息，请稍等...", "WARNING")
        thread = threading.Thread(
            target=self.query_course_thread,
            args=(courses,),
            daemon=True
        )
        thread.start()
    
    def query_course_thread(self, selected_courses):
        self.app.obtain_course_data()
        for course_name in selected_courses:
            self.log_callback(self.app.display_course_chapter_data(course_name))

    # 实时从消息队列中取日志
    def process_log_queue(self):
        while not self.log_queue.empty():
            message, level = self.log_queue.get()
            self.log_frame.write(message, level)
        self.after(200, self.process_log_queue)
    
    # 考试
    def rush_exam_callback(self):
        self.progressbar.set(0)
        courses = self.course_frame.get()
        thread = threading.Thread(
            target=self.rush_exam_thread,
            args=(courses,),
            daemon=True
        )
        thread.start()

    # 子线程考试
    def rush_exam_thread(self, selected_courses):
        total = len(selected_courses)
        for index, course_name in enumerate(selected_courses):
            self.update_current_course(course_name, index, total)
            self.after(0, lambda: self.progressbar.set(0))
            self.log_queue.put((f'程序开始自动化考试：《{course_name}》', "WARNING"))
            # 考试
            self.app.obtain_exam_info(course_name, log_callback=self.log_callback, progress_callback=self.update_progress)

# 控制面板-------------------------------------------------------------
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_default_color_theme("dark-blue")
        customtkinter.set_appearance_mode("dark")

        self.app = RsjApp()
        self.title("《绵阳市专业技术人员继续教育公需科目培训平台》刷课")
        self.geometry("600x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame = LoginFrame(self, self.app)
        self.login_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        
    def do_main(self):
        self.login_frame.destroy()
        self.main_frame = MainFrame(self, self.app)
        self.main_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")


if __name__ == "__main__":
    app = App()
    app.mainloop()