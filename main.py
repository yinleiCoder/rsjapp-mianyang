import datetime
import threading
from course import RsjApp
import customtkinter

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
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.tag_config("INFO", foreground="#00FF00")
        self.textbox.tag_config("ERROR", foreground="#FF5555")
        self.textbox.tag_config("SUCCESS", foreground="#00FFFF")
        self.textbox.tag_config("WARNING", foreground="#FFFF55")
        self.textbox.insert("end", ">>> 程序日志模块准备就绪\n\n")

    def write(self, text, level="INFO"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        log = f"[{now}] {level:<7} {text}\n"
        self.textbox.insert("end", log, level)
        self.textbox.see("end")

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400*200")
        
    def display_content(self, text):
        self.label = customtkinter.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=20)
    

class MyRadiobuttonFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = customtkinter.StringVar(value="")

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = customtkinter.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

class CourseFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.checkboxes = []

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
    

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
        isLoginSuccess = self.app.login(account, password)
        if isLoginSuccess:
            self.master.do_main()
        else:
            error_login_window = ToplevelWindow(self)
            error_login_window.focus()
            error_login_window.title('登录失败')
            error_login_window.display_content('账号、密码或自动识别验证码错误，请检查后重试！')


class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.running = False 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,5), weight=1)

        values = ["计算机网络", "操作系统", "组成原理", "信息技术", "办公应用"]
        self.course_frame = CourseFrame(self, title="全部课程", values=values)
        self.course_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.button = customtkinter.CTkButton(self, text="一键刷课", command=self.button_callback)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.button = customtkinter.CTkButton(self, text="自动考试", command=self.button_callback)
        self.button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.log_frame = LogFrame(self)
        self.log_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
    
    def button_callback(self):
        pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_default_color_theme("dark-blue")
        customtkinter.set_appearance_mode("dark")

        self.app = RsjApp()
        self.title("《绵阳市专业技术人员继续教育公需科目培训平台》刷课")
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame = LoginFrame(self, self.app)
        self.login_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        
        
    def do_main(self):
        self.login_frame.destroy()
        self.main_frame = MainFrame(self)
        self.main_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")


if __name__ == "__main__":
    app = App()
    app.mainloop()