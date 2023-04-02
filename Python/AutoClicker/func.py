import random
import sys
import cv2
import pyautogui
import win32api
import win32con
import win32gui
import time
from ctypes import windll
from PyQt5.QtWidgets import QApplication


class AutoClickError(Exception):
    """
    简介：\n
    AutoClickError是AutoClick类的实例在运行时可能会产生的错误\n
    使用方法：\n
    raise AutoClickError('some error')
    """

    def __init__(self, detail: str):
        self.str = detail


class AutoClick(object):
    """
    AutoClick类是AutoClikcer的核心，负责执行用户给定的操作，目前没有类属性\n
    实例属性：\n
    img_x, img_y: 上一次匹配图片时得到的坐标\n
    img_flag: fing_image函数是否找到对应图片\n
    admin: 当前程序是否获得管理员权限，没有获得将影响部分操作\n
    handle: 当前操作的窗口句柄\n
    class_str, title_str: 上一次更新时的窗口的类名和标题\n
    left, top, right, bot: 上一次更新时的窗口坐标\n
    win_width, win)heighr: 上一次更新时的窗口宽高\n
    """

    def __init__(self):
        self.img_x = 0
        self.img_y = 0
        self.img_flag = False
        self.admin = False
        self.handle = None
        self.class_str = ''
        self.title_str = ''
        self.left = 0
        self.top = 0
        self.right = 0
        self.bot = 0
        self.win_width = 0
        self.win_height = 0

    def get_admin(self, file: str):
        """
        get_admin函数会判断当前程序是否获得了管理员权限，如果没有，就尝试获得管理员权限，如果成功了，就将admin设为True，失败了会报错\n
        一般使用方法为self.get_admin(__file__)
        :param file: 要获得管理员权限的文件名，类型为str
        :return: None，无返回值
        """
        if not windll.shell32.IsUserAnAdmin():
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, file, None, 0)
        if windll.shell32.IsUserAnAdmin():
            self.admin = True
        else:
            raise AutoClickError("未获得管理员权限")

    def get_handle(self, self_class: str, self_title: str):
        """
        get_handle函数会寻找self_class和self_title对应的句柄，并把句柄存到self.handle中，如果没有找到，则会报错，
        如果成功找到窗口句柄，它还会调用update_position函数获得窗口的其他信息\n
        通过Visual Studio自带的spy++可以方便地获得这两个参数，你也可以到网上单独下载spy++\n
        再提一嘴，理论上来说，self_class和self_title至少有一个就可以找到窗口的句柄，另外一个可以填None，
        但是，这两个参数一般可以同时找到，所以你还是两个都填进去比较好\n
        SeeAlso: update_position
        :param self_class: 窗口的类名，类型为str
        :param self_title: 窗口的标题，类型为str
        :return: None，无返回值
        """
        self.handle = win32gui.FindWindow(self_class, self_title)
        if not self.handle:
            raise AutoClickError("未找到对应的句柄")
        else:
            self.update_position()

    def update_position(self):
        """
        update_position函数会更新实例的大部分属性，除了img_x，img_y，img_flag，admin，handle\n
        :return: None，无返回值
        """
        self.class_str = win32gui.GetClassName(self.handle)
        self.title_str = win32gui.GetWindowText(self.handle)
        self.left, self.top, self.right, self.bot = win32gui.GetWindowRect(self.handle)
        self.win_width = self.right - self.left
        self.win_height = self.bot - self.top

    def maximize_ui(self):
        """
        maximize_ui函数会使得窗口最大化
        :return: None，无返回值
        """
        win32gui.ShowWindow(self.handle, win32con.SW_MAXIMIZE)
        print("最大化程序窗口")

    def mouse_click(self, pos: (int, int), click_num: int = 1, rand: int = 7):
        """
        mouse_click函数会向窗口发送click_num次鼠标左键点击的命令，其中，点击的范围是以pos为左上角，边长为rand的正方形\n
        默认情况下，click_num=1，rand=7，即鼠标左键单击，以pos为左上角，边长为7的正方形
        :param pos: 鼠标点击的位置坐标，是一个有两个元素的列表(int,int)
        :param click_num: 鼠标左键点击次数，默认为1次
        :param rand: 点击范围的边长，默认为7像素
        :return: None，无返回值
        """
        if not self.admin:
            raise AutoClickError("未获得管理员权限")
        x = pos[0] + random.randint(0, rand)
        y = pos[1] + random.randint(0, rand)
        param = win32api.MAKELONG(x, y)
        for num in range(0, click_num):
            win32api.SendMessage(self.handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, param)
            time.sleep(0.1)
            win32api.SendMessage(self.handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, param)
            time.sleep(1)
        print(f"鼠标点击{self.title_str}的({x},{y})处，共{click_num}次")
        time.sleep(0.5)

    def find_image(self, img: str):
        """
        find_image函数会检测当前屏幕（注意：不是窗口）上是否能找到img，
        如果可以，则把找到图片的中心坐标保存在img_x，img_y中，并将img_flag设为True，
        如果不行，则将img_x，img_y设为-1，并将img_flag设为False
        :param img: 要匹配的图片的路径，类型为str
        :return: None，无返回值
        """
        try:
            self.img_x, self.img_y = pyautogui.locateCenterOnScreen(img)
            self.img_flag = True
        except TypeError:
            self.img_x, self.img_y = -1, -1
            self.img_flag = False
            print(f"没有找到{img}")

    def screen_capture(self, file_name: str):
        """
        screen_capture函数会对当前屏幕进行一次截屏，保存在当前目录中，以file_name命名
        :param file_name: 截屏文件的文件名
        :return:  None，无返回值
        """
        app = QApplication(sys.argv)
        screen = QApplication.primaryScreen()
        img = screen.grabWindow(self.handle).toImage()
        img.save(file_name)

    def img_cmp(self, img_name: str, sub_img_name: str):
        """
        img_cmp函数会在img_name图片中寻找最接近sub_img_name图片的坐标，并在img_x, img_y中存放子图片的中心位置，并返回该位置坐标
        :param img_name:
        :param sub_img_name:
        :return:  None，无返回值
        """
        img = cv2.imread(img_name)
        sub_img = cv2.imread(sub_img_name)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sub_img_gray = cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img_gray, sub_img_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        bottom_right = (top_left[0] + sub_img.shape[1], top_left[1] + sub_img.shape[0])
        self.img_x = int((top_left[0] + bottom_right[0]) / 2)
        self.img_y = int((top_left[1] + bottom_right[1]) / 2)
        print(f"在{img_name}与{sub_img_name}最接近的位置是({self.img_x},{self.img_y})")
        return self.img_x, self.img_y
