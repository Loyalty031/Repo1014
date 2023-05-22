"""
bot_operation.py

用于执行用户指令对应的操作
"""
import os
import json
import requests
from bot_api import BlankApi
from bot_config import config
# ChatBot
from transformers import AutoTokenizer, AutoModel
# Drawer
import io
import base64
import hashlib
from PIL import Image
from PIL import PngImagePlugin
from datetime import datetime
# SysInfo
import nvidia_smi
import psutil
# Translate
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


class Operation(object):
    """
    操作类
    :param api: 该操作对应的API
    :param rev: 该操作返回的信息
    :param user_id: 发起操作的用户
    :param group_id: 发起操作的用户所在群组
    """
    help: str
    total = 0
    effective = 0
    running = 0

    def __init__(self, api, rev, user_id: int, group_id: int = None):
        self.__api = api
        self.rev = rev
        self.user_id = user_id
        self.group_id = group_id
        Operation.total += 1
        Operation.running += 1

    def __del__(self):
        Operation.running -= 1

    def __run(self):
        return None

    @classmethod
    def get_help(cls):
        """
        获取帮助信息
        :return: 帮助信息
        """
        return cls.help

    @staticmethod
    def get_all_help():
        """
        获取所有帮助信息
        :return: 所有帮助信息
        """
        total = ''
        for cls in Operation.__subclasses__():
            if len(cls.get_help()) > 0:
                total += cls.get_help() + '\n'
        return total


class BlankOperation(Operation):
    help = ''

    def __init__(self, api=BlankApi, user_id: int = 0, group_id: int = None):
        super().__init__(api, self.__run(), user_id, group_id)


class ChatBot(Operation):
    """
    AI聊天
    :param api: 该操作对应的API
    :param choice: '-b' for newbing, '-d' for davinci-003, '-o' for gpt3-turbo, '-t' for chat-glm
    :param prompt: 告诉AI的话
    :param user_id: 发起操作的用户
    :param group_id: 发起操作的用户所在群组
    """
    help = """-c 或 --chat 聊天bot
    -d Davinci
    -o ChatGPT
    -t ChatGLM"""
    __tokenizer = {}
    __model = {}
    __token_usage = 0
    __temperature = 0.5

    def __init__(self, api, choice: str, prompt: str, user_id: int, group_id: int = None):
        Operation.effective += 1
        self.choice = choice
        self.prompt = prompt
        super().__init__(api, self.__run(), user_id, group_id)

    @staticmethod
    def __set_tokenizer(key, value):
        ChatBot.__tokenizer.update({key: value})

    @staticmethod
    def get_tokenizer():
        """
        获取tokenizer
        :return: tokenizer
        """
        return tuple(ChatBot.__tokenizer)

    @staticmethod
    def __set_model(key, value):
        ChatBot.__model.update({key: value})

    @staticmethod
    def get_model():
        """
        获取model
        :return: model
        """
        return tuple(ChatBot.__model)

    @staticmethod
    def get_token_usage():
        """
        获取token使用量
        :return: token使用量
        """
        return ChatBot.__token_usage

    @staticmethod
    def set_temperature(temperature: float):
        """
        设置temperature, 0 <= temperature <= 2
        :param temperature: AI聊天的随机性
        """
        if 0 <= temperature <= 2:
            ChatBot.__temperature = temperature

    @staticmethod
    def get_temperature():
        """
        获取temperature
        :return: temperature
        """
        return ChatBot.__temperature

    def __run(self):
        if self.choice == '-b':
            return self.__bing()
        elif self.choice == '-d':
            return self.__davinci()
        elif self.choice == '-o':
            return self.__gpt3_turbo()
        elif self.choice == '-t':
            return self.__chat_glm()

    def __bing(self):
        try:
            response = requests.post(
                url=f'http://{config["bing"]["host"]}:{config["bing"]["port"]}/bing/ask',
                json={
                    'style': 'balanced',
                    'question': self.prompt,
                }
            ).json()
            return response['data']['answer'].strip()
        except requests.exceptions.RequestException as err:
            return str(err)

    def __davinci(self):
        try:
            response = requests.post(
                url=config['openai']['url'] + '/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + config['openai']['key']
                },
                json={
                    'model': 'text-davinci-003',
                    'prompt': self.prompt,
                    'temperature': ChatBot.__temperature
                }
            ).json()
        except requests.exceptions.RequestException as err:
            return str(err)
        ChatBot.__token_usage += int(response["usage"]["total_tokens"])
        return response["choices"][0]["text"].strip()

    def __gpt3_turbo(self):
        try:
            response = requests.post(
                url=config['openai']['url'] + '/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + config['openai']['key']
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {'role': 'user', 'content': self.prompt}
                    ]
                }
            ).json()
        except requests.exceptions.RequestException as err:
            return str(err)
        ChatBot.__token_usage += int(response["usage"]["total_tokens"])
        return response["choices"][0]["message"]["content"].strip()

    def __chat_glm(self):
        if ChatBot.__tokenizer.get(self.choice) is None:
            try:
                self.__set_tokenizer(
                    self.choice,
                    AutoTokenizer.from_pretrained(
                        "THUDM/chatglm-6b-int4",
                        cache_dir=r'E:\torch-model',
                        trust_remote_code=True
                    )
                )
            except Exception as err:
                return '加载tokenizer时出错' + str(err)
        if ChatBot.__model.get(self.choice) is None:
            try:
                self.__set_model(
                    self.choice,
                    AutoModel.from_pretrained(
                        "THUDM/chatglm-6b-int4",
                        trust_remote_code=True,
                        cache_dir=r'E:\torch-model'
                    ).half().cuda().eval()
                )
            except Exception as err:
                return '加载model时出错' + str(err)
        try:
            return ChatBot.__model[self.choice].chat(ChatBot.__tokenizer[self.choice], self.prompt)[0]
        except Exception as err:
            return '生成回答时出错' + str(err)


class Drawer(Operation):
    """
    Stable Diffusion
    :param api: 该操作对应的API
    :param user_id: 发起操作的用户
    :param choice: '-e' for extra batch images, '-i' for img to img, '-p' for png info, '-t' for txt to img
    :param save_path: 图片保存路径
    :param save_file: 图片名
    :param data: 生成参数
    :param src_img_url: the url of the source image
    :param group_id: 发起操作的用户所在群组
    """
    help = """-s 或 --stablediffusion AI画画
    -e 图片放大
        -r [int:1-8] 放大的倍率
        -j [str] 完整的json参数
            -h 或 --help 样例
    -i 图片转图片 [img] [cmd] [arg]
        -b [int] 图片数量
        -j [str] 完整的json参数
            -h 或 --help 样例
    -p 获取png格式图片信息(技术原因，停用)
    -t 文本转图片
        -b [int] 图片数量
        -j [str] 完整的json参数
            -h 或 --help 样例"""
    __np = """((watermark)), ((nsfw)), ((out of frame)), ((extra fingers)), mutated hands, ((poorly drawn hands)),
        ((poorly drawn face)), (((mutation))), (((deformed))), (((tiling))), ((naked)), ((tile)), ((fleshpile)),
        ((ugly)), (((abstract))), blurry, ((bad anatomy)), ((bad proportions)), ((extra limbs)), cloned face, 
        (((skinny))), glitchy, ((extra breasts)), ((double torso)), ((extra arms)), ((extra hands)), 
        ((mangled fingers)), ((missing breasts)), (missing lips), ((ugly face)), ((fat)), ((extra legs)), longbody
        , lowres,bad anatomy, bad hands, missing fingers, pubic hair, extradigit, fewer digits, cropped, worst 
        quality, low quality,"""
    __api = {
        'txt2img': fr'http://{config["sd"]["host"]}:{config["sd"]["port"]}/sdapi/v1/txt2img',
        'img2img': fr'http://{config["sd"]["host"]}:{config["sd"]["port"]}/sdapi/v1/img2img',
        'png-info': fr'http://{config["sd"]["host"]}:{config["sd"]["port"]}/sdapi/v1/png-info',
        'extra_batch_images': fr'http://{config["sd"]["host"]}:{config["sd"]["port"]}/sdapi/v1/extra-batch-images',
    }
    __path = {
        'txt2img': r'.\img\txt2img',
        'img2img': r'.\img\img2img',
        'extra_batch_images': r'.\img\extra_batch_image',
    }
    __intial_data = {
        'prompt': '',
        'negative_prompt': __np,
        'sampler_name': 'Euler a',
        'width': 512,
        'height': 512,
        'step': 25,
    }
    __override_payload = {
        "override_settings": {

        }
    }

    def __init__(
            self, api, user_id: int, choice: str,
            save_path: str = None, save_file: str = None, data: dict = None,
            src_img_path: str = None, src_img_b64: str = None, src_img_url: str = None, group_id: int = None
    ):
        self.choice = choice
        self.src_img_path = src_img_path
        self.src_img_b64 = src_img_b64
        self.src_img_url = src_img_url
        self.src_img = None
        self.save_path = save_path
        self.save_file = save_file
        self.data = data
        self.response = None
        Operation.effective += 1
        super().__init__(api, self.__run(), user_id, group_id)

    @staticmethod
    def image_to_base64(image: Image.Image, fmt: str = 'png') -> str:
        """
        将Image对象转换为base64编码
        :param image: Image对象
        :param fmt: 图片格式
        :return: base64编码
        """
        output_buffer = io.BytesIO()
        image.save(output_buffer, format=fmt)
        byte_data = output_buffer.getvalue()
        base64_str = base64.b64encode(byte_data).decode('utf-8')
        return f'data:image/{fmt};base64,' + base64_str

    def __get_src_img(self) -> bool:
        if self.src_img_path is not None:
            img = Image.open(self.src_img_path)
        elif self.src_img_b64 is not None:
            img = Image.open(io.BytesIO(base64.b64decode(self.src_img_b64)))
        elif self.src_img_url is not None:
            img = Image.open(io.BytesIO(requests.get(self.src_img_url).content))
        else:
            img = None
        if img is None:
            return False
        self.src_img = img
        return True

    def __run(self):
        if self.choice == '-e':  # extra batch images
            if self.save_path is None:
                self.save_path = Drawer.__path['extra_batch_images']
            return self.__extra_batch_images()
        elif self.choice == '-i':  # img to img
            if self.save_path is None:
                self.save_path = Drawer.__path['img2img']
            return self.__img_to_img()
        elif self.choice == '-p':  # png info
            return self.__png_info()
        elif self.choice == '-t':  # txt to img
            if self.save_path is None:
                self.save_path = Drawer.__path['txt2img']
            return self.__txt_to_img()

    def __extra_batch_images(self) -> str | list[str]:
        if self.data is None:
            self.data = {
                "resize_mode": 0,
                "upscaling_resize": 2,
                "upscaler_1": "R-ESRGAN 4x+ Anime6B",
            }
        if not self.__get_src_img():
            return '获取源图片失败'
        self.data.update({
            'imageList': [{
                'data': Drawer.image_to_base64(self.src_img, self.src_img.format.lower()),
                'name': self.save_path + os.sep + self.save_file + f'.{self.src_img.format.lower()}'
            }]
        })
        self.__override_setting()
        self.response = requests.post(Drawer.__api['extra_batch_images'], data=json.dumps(self.data))
        return self.__handle_response()

    def __img_to_img(self):
        if self.data is None:
            self.data = Drawer.__intial_data
        if self.src_img_b64 is None:
            if not self.__get_src_img():
                return '获取源图片失败'
            init_images = [Drawer.image_to_base64(self.src_img, self.src_img.format.lower())]
        else:
            init_images = [self.src_img_b64]
        if not self.__get_src_img():
            return '获取源图片失败'
        self.data.update(
            {
                'init_images': init_images,
                'prompt': Translate(BlankApi, 0, self.data.get('prompt'), tar='en').rev,
                'negative_prompt': Drawer.__np + self.data.get('negative_prompt')
            }
        )
        self.__override_setting()
        self.response = requests.post(Drawer.__api['img2img'], data=json.dumps(self.data))
        return self.__handle_response()

    def __png_info(self):
        if self.src_img_b64 is None:
            if not self.__get_src_img():
                return '获取源图片失败'
            self.data.update({'image': Drawer.image_to_base64(self.src_img, self.src_img.format.lower())})
        else:
            self.data.update({'image': self.src_img_b64})
        response = requests.post(Drawer.__api['png-info'], data=json.dumps(self.data)).json()
        rev_str = '' if self.group_id is None else '\n'
        for num, category in enumerate(response):
            rev_str += '{}.{}:{}\n'.format(num + 1, category, response[category])
        return rev_str

    def __txt_to_img(self):
        if self.data is None:
            self.data = Drawer.__intial_data
        en_prompt = Translate(BlankApi, 0, self.data.get('prompt'), tar='en')
        self.data['prompt'] = en_prompt.rev
        del en_prompt
        self.__override_setting()
        self.response = requests.post(Drawer.__api['txt2img'], data=json.dumps(self.data))
        return self.__handle_response()

    def __override_setting(self) -> None:
        self.data.update(Drawer.__override_payload)

    def __handle_response(self) -> str | list[str]:
        response_json = self.response.json()
        if self.response.status_code != 200:
            rev_str = '\n'
            for num, category in enumerate(response_json):
                rev_str += '{}.{}:{}\n'.format(num + 1, category, response_json[category])
            return rev_str
        rev = []
        for index, b64data in enumerate(response_json['images']):
            rev.append(self.__get_png_info_and_save(index, b64data))
        for index, path in enumerate(rev):
            if os.stat(path).st_size >= 10485760:
                rev.pop(index)
        return rev

    def __get_png_info_and_save(self, index: int, b64data: str):
        image = Image.open(io.BytesIO(base64.b64decode(b64data.split(",", 1)[0])))
        time = datetime.now()
        if self.save_file is None:
            temp = hashlib.md5(b64data.encode()).hexdigest()
        else:
            temp = '.'.join(self.save_file.split('.')[:-2])
        img_name = f'''{self.save_path}{os.sep}{temp.replace(' ', '_')}.{time.strftime("%Y-%m-%d_%H-%M-%S")}''' + \
                   f'''.{time.microsecond}({index}).{image.format.lower()}'''
        image.save(
            fp=img_name,
            pnginfo=PngImagePlugin.PngInfo().add_text(
                key="parameters",
                value=requests.post(
                    url=Drawer.__api['png-info'],
                    json={"image": f"data:image/{image.format.lower()};base64,{b64data}"}
                ).json().get("info")
            )
        )
        return img_name


class UnAuthorizedAccess(Operation):
    """
    未授权访问
    """
    help = ''

    def __init__(self, api, user_id: int = 0, group_id: int = None):
        super().__init__(api, '你没有足够的权限使用该功能', user_id, group_id)


class SysInfo(Operation):
    """
    获取系统信息
    :param api: 该操作对应的API
    :param detail: 是否显示详细信息
    :param user_id: 发起操作的用户
    :param group_id: 发起操作的用户所在群组
    """
    help = """--sys 查看服务端运行状态
    -d 提供更多细节"""

    def __init__(self, api, detail: bool = False, user_id: int = 0, group_id: int = None):
        self.detail = detail
        super().__init__(api, self.__run(), user_id, group_id)

    # noinspection PyTypeChecker
    def __run(self):
        """
        获取系统信息
        :return: 系统信息
        """
        # 获取cpu使用情况
        cpu_info = {
            'cpu_avg': psutil.cpu_percent(interval=0),  # cpu平均使用率
            'per_cpu_avg': psutil.cpu_percent(interval=0, percpu=True),  # 每个cpu使用率
        }
        rev = "CPU平均使用率: {}%\n".format(cpu_info['cpu_avg'])
        if self.detail:
            for num, item in enumerate(cpu_info['per_cpu_avg']):
                rev += "CPU{}使用率: {}%\n".format(num, item)
        # 获取内存使用情况
        mem = psutil.virtual_memory()
        mem_total = mem.total / 1024 / 1024
        mem_percent = mem.percent
        rev += "内存使用情况: {:.2f}MB / {:.2f}MB ({:.2f}%)\n".format(mem.used / 1024 / 1024, mem_total, mem_percent)
        # 获取磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_total = disk.total / 1024 / 1024
        disk_percent = disk.percent
        rev += "磁盘使用情况: {:.2f}MB / {:.2f}MB ({:.2f}%)\n".format(disk.used / 1024 / 1024, disk_total, disk_percent)
        # 初始化NVIDIA SMI
        nvidia_smi.nvmlInit()
        # 获取GPU数量
        device_count = nvidia_smi.nvmlDeviceGetCount()
        # 遍历所有GPU，获取显卡信息
        for i in range(device_count):
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(i)
            temp = nvidia_smi.nvmlDeviceGetTemperature(handle, nvidia_smi.NVML_TEMPERATURE_GPU)
            power = nvidia_smi.nvmlDeviceGetPowerUsage(handle)
            rev += "GPU{}温度: {}°C\n".format(i, temp)
            rev += "GPU{}功耗: {} W\n".format(i, power / 1000)
        # 关闭NVIDIA SMI
        nvidia_smi.nvmlShutdown()
        return rev


class Translate(Operation):
    """
    文本翻译
    :param api: 该操作对应的API
    :param user_id: 发起操作的用户
    :param text: 要翻译的文本
    :param untranslated: 避免翻译的文本，仅限一个单词
    :param src: 源语言
    :param tar: 目标语言
    :param group_id: 发起操作的用户所在群组
    """
    help = """--translate <text> 翻译文本"""

    def __init__(
            self, api, user_id: int, text: str,
            untranslated: str = '', src: str = 'auto', tar: str = 'zh', group_id: int = None
    ):
        self.text = text
        self.untranslated = untranslated
        self.src = src
        self.tar = tar
        super().__init__(api, self.__run(), user_id, group_id)

    def __run(self):
        return self.__tencent_translate()

    def __tencent_translate(self):
        """
        腾讯云翻译，每月免费200万字符
        :return: 翻译结果
        """
        try:
            cred = credential.Credential(config['tencent']['secret_id'], config['tencent']['secret_key'])
            http_profile = HttpProfile()
            http_profile.endpoint = 'tmt.tencentcloudapi.com'
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            client = tmt_client.TmtClient(cred, 'ap-shanghai', client_profile)
            translate_request = models.TextTranslateRequest()
            translate_request.SourceText = self.text  # 要翻译的语句
            translate_request.Source = self.src  # 源语言类型
            translate_request.Target = self.tar  # 目标语言类型
            translate_request.ProjectId = 0
            translate_request.UntranslatedText = self.untranslated  # 未翻译文本
            return json.loads(client.TextTranslate(translate_request).to_json_string())['TargetText']
        except TencentCloudSDKException as err:
            return str(err)


print(Operation.get_all_help())
