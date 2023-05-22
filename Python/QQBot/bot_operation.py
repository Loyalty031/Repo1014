import os
import json
import requests
import bot_data
import bot_api
from bot_config import config
# ChatBot
from transformers import AutoTokenizer, AutoModel
# Drawer
import io
import base64
from PIL import Image
from PIL import PngImagePlugin
from datetime import datetime
# Translate
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


class Operation(object):
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

    def run(self):
        return None


class BlankOperation(Operation):
    def __init__(self, api=bot_api.BlankApi, user_id: int = 0, group_id: int = 0):
        super().__init__(api, self.run(), user_id, group_id)


class ChatBot(Operation):
    """
    chat with chatbots
    :param api: the api of the operation
    :param choice: '-b' for newbing, '-d' for davinci-003, '-o' for gpt3-turbo, '-t' for chat-glm
    :param prompt: the prompt to chat with
    :param user_id: the user id of the operation
    :param group_id: the group id of the operation
    """
    __tokenizer = {}
    __model = {}
    __token_usage = 0
    __temperature = 0.5

    def __init__(self, api, choice: str, prompt: str, user_id: int, group_id: int = None):
        Operation.effective += 1
        self.choice = choice
        self.prompt = prompt
        super().__init__(api, self.run(), user_id, group_id)

    @staticmethod
    def __set_tokenizer(key, value):
        ChatBot.__tokenizer.update({key: value})

    @staticmethod
    def get_tokenizer():
        return tuple(ChatBot.__tokenizer)

    @staticmethod
    def __set_model(key, value):
        ChatBot.__model.update({key: value})

    @staticmethod
    def get_model():
        return tuple(ChatBot.__model)

    @staticmethod
    def get_token_usage():
        return ChatBot.__token_usage

    @staticmethod
    def set_temperature(temperature: float):
        if 0 <= temperature <= 2:
            ChatBot.__temperature = temperature

    @staticmethod
    def get_temperature():
        return ChatBot.__temperature

    def run(self):
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
        except requests.exceptions.RequestException as err:
            return str(err)
        return response['data']['answer'].strip()

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
            self.__set_tokenizer(
                self.choice,
                AutoTokenizer.from_pretrained(
                    "THUDM/chatglm-6b-int4",
                    cache_dir=r'E:\torch-model',
                    trust_remote_code=True
                )
            )
        if ChatBot.__model.get(self.choice) is None:
            self.__set_model(
                self.choice,
                AutoModel.from_pretrained(
                    "THUDM/chatglm-6b-int4",
                    trust_remote_code=True,
                    cache_dir=r'E:\torch-model'
                ).half().cuda().eval()
            )
        return ChatBot.__model[self.choice].chat(ChatBot.__tokenizer[self.choice], self.prompt)[0]


class Drawer(Operation):
    """
    draw images
    :param api: the api of the operation
    :param user_id: the user id of the operation
    :param choice: '-e' for extra batch images, '-i' for img to img, '-p' for png info, '-t' for txt to img
    :param save_path: the path of the saved image
    :param save_file: the file name of the saved image
    :param data: the data of the operation
    :param src_img_url: the url of the source image
    :param group_id: the group id of the operation
    """
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

    def __init__(
            self, api, user_id: int,
            choice: str, save_path: str, save_file: str, data: dict,
            src_img_url: str = None, group_id: int = None
    ):
        self.choice = choice
        self.src_img_url = src_img_url
        self.save_path = save_path
        self.save_file = save_file
        self.data = data
        self.response = None
        Operation.effective += 1
        super().__init__(api, self.run(), user_id, group_id)

    def run(self):
        if self.choice == '-e':
            if not self.__path:
                self.__path = Drawer.__path['extra_batch_images']
            return self.__extra_batch_images()
        elif self.choice == '-i':
            if not self.__path:
                self.__path = Drawer.__path['img2img']
            return self.__img_to_img()
        elif self.choice == '-p':
            return self.__png_info()
        elif self.choice == '-t':
            if not self.__path:
                self.__path = Drawer.__path['txt2img']
            return self.__txt_to_img()

    def __extra_batch_images(self) -> str | list[str]:
        if self.data is None:
            self.data = {
                "resize_mode": 0,
                "upscaling_resize": 2,
                "upscaler_1": "R-ESRGAN 4x+ Anime6B",
            }
        img = Image.open(io.BytesIO(requests.get(self.src_img_url).content))
        self.data.update(
            {
                'imageList':
                    [
                        {
                            'data': bot_data.image_to_base64(img, img.format.lower()),
                            'name': self.save_path + os.sep + self.save_file + f'.{img.format.lower()}'
                        }
                    ]
            }
        )
        self.__override_setting()
        self.response = requests.post(Drawer.__api['extra_batch_images'], data=json.dumps(self.data))
        return self.__handle_response()

    def __img_to_img(self):
        if self.data is None:
            self.data = Drawer.__intial_data
        img = Image.open(io.BytesIO(requests.get(self.src_img_url).content))
        en_prompt = Translate(bot_api.BlankApi, 0, self.data.get('prompt'), target_lan='en')
        en_prompt.run()
        self.data.update(
            {
                'init_images': [
                    bot_data.image_to_base64(img, img.format.lower())
                ],
                'prompt': en_prompt.rev,
                'negative_prompt': Drawer.__np + self.data.get('negative_prompt')
            }
        )
        del en_prompt
        self.__override_setting()
        self.response = requests.post(Drawer.__api['img2img'], data=json.dumps(self.data))
        return self.__handle_response()

    def __png_info(self):
        img = Image.open(io.BytesIO(requests.get(self.src_img_url).content))
        data = {'image': bot_data.image_to_base64(img, img.format.lower())}
        response = requests.post(Drawer.__api['png-info'], data=json.dumps(data)).json()
        rev_str = '' if self.group_id is None else '\n'
        for num, category in enumerate(response):
            rev_str += '{}.{}:{}\n'.format(num + 1, category, response[category])
        return rev_str

    def __txt_to_img(self):
        if self.data is None:
            self.data = Drawer.__intial_data
        en_prompt = Translate(bot_api.BlankApi, 0, self.data.get('prompt'), target_lan='en')
        en_prompt.run()
        self.data['prompt'] = en_prompt.rev
        del en_prompt
        self.__override_setting()
        self.response = requests.post(Drawer.__api['txt2img'], data=json.dumps(self.data))
        return self.__handle_response()

    def __override_setting(self) -> None:
        override_payload = {
            "override_settings": {

            }
        }
        self.data.update(override_payload)

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
        temp = bot_data.encrypt(b64data) if self.save_file is None else '.'.join(self.save_file.split('.')[:-2])
        temp_name = f'''{self.save_path}{os.sep}{temp.replace(' ', '_')}.{time.strftime("%Y-%m-%d_%H-%M-%S")}''' + \
                    f'''.{time.microsecond}({index}).{image.format.lower()}'''
        image.save(
            fp=temp_name,
            pnginfo=PngImagePlugin.PngInfo().add_text(
                key="parameters",
                value=requests.post(
                    url=Drawer.__api['png-info'],
                    json={
                        "image": f"data:image/{image.format.lower()};base64,{b64data}"
                    }
                ).json().get("info")
            )
        )
        return temp_name


class Translate(Operation):
    """
    :param text: 要翻译的文本
    :param source_lan: 源语言
    :param target_lan: 目标语言
    """

    def __init__(
            self,
            api,
            user_id: int,
            text: str,
            source_lan: str = 'auto',
            target_lan: str = 'zh',
            group_id: int = None
    ):
        self.text = text
        self.source_lan = source_lan
        self.target_lan = target_lan
        super().__init__(api, self.run(), user_id, group_id)

    def run(self):
        return self.tencent_translate()

    def tencent_translate(self):
        try:
            cred = credential.Credential(config['tencent']['secret_id'], config['tencent']['secret_key'])
            http_profile = HttpProfile()
            http_profile.endpoint = 'tmt.tencentcloudapi.com'
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            client = tmt_client.TmtClient(cred, 'ap-shanghai', client_profile)
            translate_request = models.TextTranslateRequest()
            translate_request.SourceText = self.text  # 要翻译的语句
            translate_request.Source = self.source_lan  # 源语言类型
            translate_request.Target = self.target_lan  # 目标语言类型
            translate_request.ProjectId = 0
            # translate_request.UntranslatedText = 'Jerry'
            return json.loads(client.TextTranslate(translate_request).to_json_string())['TargetText']
        except TencentCloudSDKException as err:
            return str(err)
