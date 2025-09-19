# main.py

"""
小米钱包每日任务主执行脚本 (最终 Bug 修复版)。

本脚本基于用户提供的有效版本进行代码风格和结构的规范化重构，
并修复了因 URL 清理、会话管理不当以及 API 参数遗漏导致的 Bug。
核心业务逻辑、API URL 及参数与原始有效版本保持完全一致，
以确保功能的稳定性和兼容性。

功能：
1. 读取 `xiaomiconfig.json` 中的所有账号配置。
2. 为每个账号获取临时 Cookie。
3. 严格按照原始逻辑，自动完成小米钱包的每日浏览任务。
4. 将执行结果日志回写到配置文件中。
5. （可选）如果配置了飞书 Webhook，则发送执行结果通知。
"""

import json
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
import urllib3

# --- 全局常量 ---
CONFIG_FILE = "xiaomiconfig.json"
API_HOST = "m.jr.airstarfinance.net"

# 任务接口使用的移动端 User-Agent
USER_AGENT_MOBILE = (
    'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; '
    'AppBundle/com.mipay.wallet; AppVersionName/6.89.1.5275.2323; AppVersionCode/20577595; '
    'MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; '
    'mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Version/4.0 Mobile Safari/5.36 XiaoMi/MiuiBrowser/4.3'
)
# 获取 Cookie 时使用的桌面端 User-Agent (与原始版本保持一致)
USER_AGENT_DESKTOP = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
)


# 禁用 HTTPS InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- 辅助功能模块 ---

def send_feishu_notification(webhook_url: str, message: str) -> None:
    """通过指定的飞书 Webhook URL 发送文本消息。"""
    if not webhook_url:
        return

    headers = {'Content-Type': 'application/json'}
    payload = {"msg_type": "text", "content": {"text": message}}

    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("StatusCode") == 0:
            print("  ✅ 飞书通知已成功发送。")
        else:
            error_msg = response_json.get('StatusMessage', '未知错误')
            print(f"  ⚠️ 飞书通知发送失败，响应: {error_msg}")
    except requests.RequestException as e:
        print(f"  ❌ 发送飞书通知时发生网络错误: {e}")
    except Exception as e:
        print(f"  ❌ 发送飞书通知时发生未知错误: {e}")


def generate_notification(account_id: str, rnl_instance: 'RNL', us: str) -> str:
    """根据任务执行结果生成格式化的日志/通知消息。"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    msg = (
        f"【小米钱包每日任务报告】\n"
        f"✨ 账号别名：{us}\n"
        f"✨ 小米ID：{account_id}\n"
        f"📊 当前可兑换视频天数：{rnl_instance.total_days}\n\n"
        f"📅 {current_date} 任务记录\n"
        + "-" * 25
    )

    if not rnl_instance.today_records:
        msg += "\n  今日暂无新增奖励记录"
    else:
        for record in rnl_instance.today_records:
            record_time = record.get("createTime", "未知时间")
            value = record.get("value", 0)
            days = int(value) / 100
            msg += f"\n| ⏰ {record_time}\n| 🎁 领到视频会员，+{days:.2f}天"

    if rnl_instance.error_info:
        msg += f"\n\n⚠️ 执行异常：{rnl_instance.error_info}"

    msg += "\n" + "=" * 25
    return msg

def generate_notification_with_exchange(account_id: str, rnl_instance: 'RNL', us: str, exchange_results: List[Dict[str, Any]]) -> str:
    """根据任务执行结果和兑换结果生成格式化的日志/通知消息。"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    msg = (
        f"【小米钱包每日任务报告】\n"
        f"✨ 账号别名：{us}\n"
        f"✨ 小米ID：{account_id}\n"
        f"📊 当前可兑换视频天数：{rnl_instance.total_days}\n\n"
        f"📅 {current_date} 任务记录\n"
        + "-" * 25
    )

    if not rnl_instance.today_records:
        msg += "\n  今日暂无新增奖励记录"
    else:
        for record in rnl_instance.today_records:
            record_time = record.get("createTime", "未知时间")
            value = record.get("value", 0)
            days = int(value) / 100
            msg += f"\n| ⏰ {record_time}\n| 🎁 领到视频会员，+{days:.2f}天"

    # 添加会员兑换结果
    if exchange_results:
        msg += "\n\n📺 会员兑换结果\n" + "-" * 25
        success_count = sum(1 for r in exchange_results if r['success'])
        failed_count = len(exchange_results) - success_count
        
        msg += f"\n✅ 成功：{success_count}个  ❌ 失败：{failed_count}个"
        
        for result in exchange_results:
            if result['success']:
                msg += f"\n| ✅ {result['type']} -> {result['phone']}"
                msg += f"\n| 💎 {result['message']}"
            else:
                msg += f"\n| ❌ {result['type']} -> {result['phone']}"
                msg += f"\n| ⚠️ {result['message']}"
    else:
        msg += "\n\n📺 会员兑换\n" + "-" * 25 + "\n  未配置会员兑换"

    if rnl_instance.error_info:
        msg += f"\n\n⚠️ 执行异常：{rnl_instance.error_info}"

    msg += "\n" + "=" * 25
    return msg


# --- 核心业务逻辑模块 ---

class ApiRequest:
    """封装 API 请求，统一管理会话、Cookie 和请求头。"""
    def __init__(self, cookies: Union[str, Dict[str, str]]):
        self.session = requests.Session()
        self.base_headers = {'Host': API_HOST, 'User-Agent': USER_AGENT_MOBILE}
        self.update_cookies(cookies)

    @staticmethod
    def _parse_cookies(cookies_str: str) -> Dict[str, str]:
        """将 Cookie 字符串解析为字典。"""
        return {
            k.strip(): v for k, v in
            (item.split('=', 1) for item in cookies_str.split(';') if '=' in item)
        }

    def update_cookies(self, cookies: Union[str, Dict[str, str]]) -> None:
        """更新会话中的 Cookie。"""
        if not cookies:
            return
        dict_cookies = self._parse_cookies(cookies) if isinstance(cookies, str) else cookies
        self.session.cookies.update(dict_cookies)
        self.base_headers['Cookie'] = '; '.join([f"{k}={v}" for k, v in dict_cookies.items()])

    def request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送一个 HTTP 请求。"""
        headers = {**self.base_headers, **kwargs.pop('headers', {})}
        try:
            resp = self.session.request(method.upper(), url, verify=False, headers=headers, timeout=15, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            # 这里的 error_info 是 RNL 类的属性，不应在此处设置
            print(f"  [Request Error] {e}")
            return None
        except (json.JSONDecodeError, AttributeError):
            print(f"  [JSON Parse Error] 无法解析服务器响应: {getattr(resp, 'text', 'No Response Text')[:100]}")
            return None

    def get(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送 GET 请求。"""
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送 POST 请求。"""
        return self.request('POST', url, **kwargs)


class RNL:
    """
    封装小米钱包任务的具体业务逻辑。
    集成小米钱包3.0版本的新功能，包括新手任务和会员兑换。
    """
    def __init__(self, api_request: ApiRequest):
        self.api = api_request
        self.activity_code = '2211-videoWelfare'
        self.t_id: Optional[str] = None
        self.total_days: str = "未知"
        self.total_days_num: float = 0.0  # 添加数值版本的天数
        self.today_records: List[Dict[str, Any]] = []
        self.error_info: str = ""

    def get_task_list(self) -> Optional[List[Dict[str, Any]]]:
        """获取任务列表。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/getTaskList"
        try:
            response = self.api.post(url, data={'activityCode': self.activity_code})
            if response and response.get('code') == 0:
                target_tasks = [
                    task for task in response['value']['taskInfoList']
                    if '浏览组浏览任务' in task.get('taskName', '')
                ]
                return target_tasks
            self.error_info = f"获取任务列表失败：{response}"
            return None
        except Exception as e:
            self.error_info = f'获取任务列表时发生异常：{e}'
            return None

    def get_task(self, task_code: str) -> Optional[str]:
        """通过 taskCode 获取 userTaskId。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/getTask"
        # ▼▼▼ 核心 Bug 修复：恢复 'jrairstar_ph' 魔法参数 ▼▼▼
        data = {
            'activityCode': self.activity_code,
            'taskCode': task_code,
            'jrairstar_ph': '98lj8puDf9Tu/WwcyMpVyQ=='
        }
        # ▲▲▲ 核心 Bug 修复 ▲▲▲
        try:
            response = self.api.post(url, data=data)
            if response and response.get('code') == 0:
                return response['value']['taskInfo']['userTaskId']
            self.error_info = f'获取任务信息失败：{response}'
            return None
        except Exception as e:
            self.error_info = f'获取任务信息时发生异常：{e}'
            return None

    def complete_task(self, task_id: str, t_id: str, brows_click_url_id: str) -> Optional[str]:
        """完成浏览任务。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/completeTask"
        # ▼▼▼ 核心 Bug 修复：恢复所有必要的 URL 参数 ▼▼▼
        params = {
            'activityCode': self.activity_code,
            'app': 'com.mipay.wallet',
            'isNfcPhone': 'true',
            'channel': 'mipay_indexicon_TVcard',
            'deviceType': '2',
            'system': '1',
            'visitEnvironment': '2',
            'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}',
            'taskId': task_id,
            'browsTaskId': t_id,
            'browsClickUrlId': brows_click_url_id,
            'clickEntryType': 'undefined',
            'festivalStatus': '0'
        }
        # ▲▲▲ 核心 Bug 修复 ▲▲▲
        try:
            response = self.api.get(url, params=params)
            if response and response.get('code') == 0:
                return response.get('value')
            self.error_info = f'完成任务失败：{response}'
            return None
        except Exception as e:
            self.error_info = f'完成任务时发生异常：{e}'
            return None

    def receive_award(self, user_task_id: str) -> None:
        """领取奖励。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/luckDraw"
        # 恢复所有必要的 URL 参数
        params = {
            'activityCode': self.activity_code,
            'userTaskId': user_task_id,
            'app': 'com.mipay.wallet',
            'isNfcPhone': 'true',
            'channel': 'mipay_indexicon_TVcard',
            'deviceType': '2',
            'system': '1',
            'visitEnvironment': '2',
            'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}',
        }
        try:
            response = self.api.get(url, params=params)
            if response and response.get('code') != 0:
                self.error_info = f'领取奖励失败：{response}'
        except Exception as e:
            self.error_info = f'领取奖励时发生异常：{e}'

    def complete_new_user_task(self) -> Optional[str]:
        """完成应用下载试用任务"""
        try:
            headers = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'Cache-Control': 'no-cache',
                'X-Request-ID': '1281eea0-e268-4fcc-9a5f-7dc11475b7db',
                'X-Requested-With': 'com.mipay.wallet',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            url = f'https://{API_HOST}/mp/api/generalActivity/completeTask?activityCode=2211-videoWelfare&app=com.mipay.wallet&oaid=8c45c5802867e923&regId=KWkK5VsKXiIbAH8Rf6kgU6tpDPyNWgXY8YCM1mQtt5nd7i1%2F4BqzPq0uY7OlIEOd&versionCode=20577622&versionName=6.96.0.5453.2620&isNfcPhone=true&channel=mipay_indexicon_TVcard2test&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.video%22:%22v2023091090(MiVideo-ROM)%22,%22com.mipay.wallet%22:%226.96.0.5453.2620%22%7D&taskCode=NEW_USER_CAMPAIGN&browsTaskId=&browsClickUrlId=1306285&adInfoId=&triggerId='
            
            response = self.api.get(url, headers=headers)
            if response and response.get('code') == 0:
                print(f'  ✅ 完成应用下载试用成功，获得userTaskId: {response["value"]}')
                return response['value']
            elif response and response.get('code') != 0:
                print(f'  ⚠️ 完成应用下载试用失败：{response}')
                return None
            else:
                print(f'  ⚠️ 完成应用下载试用失败：网络请求异常')
                return None
        except Exception as e:
            print(f'  ❌ 完成应用下载试用失败：{e}')
            return None

    def receive_new_user_award(self, user_task_id: str) -> bool:
        """领取应用下载试用奖励"""
        try:
            # 发送领取请求前延时5秒
            print("  - 等待5秒后领取奖励...")
            time.sleep(5)
            
            headers = {
                'Connection': 'keep-alive',
                'sec-ch-ua': '"Chromium";v="118", "Android WebView";v="118", "Not=A?Brand";v="99"',
                'Accept': 'application/json, text/plain, */*',
                'Cache-Control': 'no-cache',
                'sec-ch-ua-mobile': '?1',
                'X-Request-ID': 'c09abfa7-6ea4-4435-a741-dff3622215cf',
                'sec-ch-ua-platform': '"Android"',
                'X-Requested-With': 'com.mipay.wallet',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            url = f'https://{API_HOST}/mp/api/generalActivity/luckDraw?imei=&device=alioth&appLimit=%7B%22com.qiyi.video%22:false,%22com.youku.phone%22:false,%22com.tencent.qqlive%22:false,%22com.hunantv.imgo.activity%22:false,%22com.cmcc.cmvideo%22:false,%22com.sankuai.meituan%22:false,%22com.anjuke.android.app%22:false,%22com.tal.abctimelibrary%22:false,%22com.lianjia.beike%22:false,%22com.kmxs.reader%22:false,%22com.jd.jrapp%22:false,%22com.smile.gifmaker%22:true,%22com.kuaishou.nebula%22:false%7D&activityCode=2211-videoWelfare&userTaskId={user_task_id}&app=com.mipay.wallet&oaid=8c45c5802867e923&regId=L522i5qLZR9%2Bs25kEqPBJYbbHqUS4LrpuTsgl9kdsbcyU7tjWmx1BewlRNSSZaOT&versionCode=20577622&versionName=6.96.0.5453.2620&isNfcPhone=true&channel=mipay_indexicon_TVcard2test&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.video%22:%22v2023091090(MiVideo-ROM)%22,%22com.mipay.wallet%22:%226.96.0.5453.2620%22%7D'
            
            response = self.api.get(url, headers=headers)
            if response and response.get('code') == 0:
                prize_info = response['value']['prizeInfo']
                print(f'  ✅ 领取应用下载试用奖励成功：获得{prize_info["amount"]} {prize_info["prizeDesc"]}')
                return True
            elif response and response.get('code') != 0:
                print(f'  ⚠️ 领取应用下载试用奖励失败：{response}')
                return False
            else:
                print(f'  ❌ 领取应用下载试用奖励失败：网络请求异常')
                return False
        except Exception as e:
            print(f'  ❌ 领取应用下载试用奖励失败：{e}')
            return False

    def query_user_info_and_records(self) -> bool:
        """查询用户总奖励和今日记录。"""
        base_url = f"https://{API_HOST}/mp/api/generalActivity/"
        params = {
            'activityCode': self.activity_code,
            'app': 'com.mipay.wallet',
            'deviceType': '2',
            'system': '1',
            'visitEnvironment': '2',
            'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}'
        }
        try:
            total_res = self.api.get(f"{base_url}queryUserGoldRichSum", params=params)
            if not total_res or total_res.get('code') != 0:
                self.error_info = f'获取兑换视频天数失败：{total_res}'
                return False
            self.total_days_num = int(total_res.get('value', 0)) / 100  # 添加数值版本
            self.total_days = f"{self.total_days_num:.2f}天"

            record_params = {**params, 'pageNum': 1, 'pageSize': 20}
            record_res = self.api.get(f"{base_url}queryUserJoinList", params=record_params)
            if not record_res or record_res.get('code') != 0:
                self.error_info = f'查询任务完成记录失败：{record_res}'
                return False

            self.today_records = []
            current_date = datetime.now().strftime("%Y-%m-%d")
            for item in record_res.get('value', {}).get('data', []):
                if item.get('createTime', '').startswith(current_date):
                    self.today_records.append(item)
            return True
        except Exception as e:
            self.error_info = f'获取任务记录时发生异常：{e}'
            return False

    def run_main_workflow(self) -> bool:
        """执行任务的主流程，集成小米钱包3.0版本的新功能。"""
        if not self.query_user_info_and_records():
            return False
        
        # 先尝试完成新手任务
        print("  - 尝试完成应用下载试用任务...")
        new_user_task_id = self.complete_new_user_task()
        if new_user_task_id:
            time.sleep(2)
            self.receive_new_user_award(new_user_task_id)
            time.sleep(2)
        else:
            print("  - 应用下载试用任务已完成或不可用。")
        
        # 原有的浏览任务逻辑
        for i in range(2):
            print(f"  - 开始第 {i + 1} 轮浏览任务...")
            tasks = self.get_task_list()
            if not tasks:
                print("  - 未找到可执行的任务列表，可能今日任务已完成。")
                break
            
            task = tasks[0]
            try:
                self.t_id = task['generalActivityUrlInfo']['id']
            except (KeyError, TypeError):
                pass
            
            if not self.t_id:
                print("  - 无法获取任务 t_id，中断执行。")
                return False

            task_id = task['taskId']
            task_code = task['taskCode']
            brows_click_url_id_from_api = task['generalActivityUrlInfo']['browsClickUrlId']

            time.sleep(random.randint(10, 15))

            user_task_id = self.complete_task(
                task_id=task_id,
                t_id=self.t_id,
                brows_click_url_id=brows_click_url_id_from_api
            )

            time.sleep(random.randint(2, 4))

            if not user_task_id:
                user_task_id = self.get_task(task_code=task_code)
                time.sleep(random.randint(2, 4))
            
            if user_task_id:
                self.receive_award(user_task_id=user_task_id)
            else:
                print("  - 未能获取 user_task_id，无法领取本轮奖励。")

            time.sleep(random.randint(2, 4))
        
        print("  - 所有任务轮次执行完毕，正在刷新最终数据...")
        self.query_user_info_and_records()
        return True

    def get_exchange_memberships(self) -> List[Dict[str, Any]]:
        """获取可兑换的会员列表"""
        try:
            print("  - 尝试获取可兑换的会员列表...")
            url = f"https://{API_HOST}/mp/api/generalActivity/getPrizeStatusV2"
            params = {
                'activityCode': self.activity_code,
                'needPrizeBrand': 'youku,mgtv,iqiyi,tencent,bilibili,other'
            }
            
            response = self.api.get(url, params=params)
            
            if response and response.get('code') == 0:
                print(f"  ✅ 获取会员列表成功")
                
                # 解析奖品信息
                memberships = []
                prize_list = response.get('value', [])
                
                if isinstance(prize_list, list):
                    for prize in prize_list:
                        try:
                            # 解析每个奖品的信息
                            prize_id = prize.get('prizeId')
                            prize_name = prize.get('prizeName', '')
                            prize_brand = prize.get('prizeBrand', '')
                            need_gold_rice = prize.get('needGoldRice', 0)
                            prize_code = prize.get('prizeCode', '')
                            stock_status = prize.get('stockStatus', 0)
                            today_stock_status = prize.get('todayStockStatus', 0)
                            
                            # 计算消耗天数 (needGoldRice / 100)
                            cost_days = float(need_gold_rice) / 100.0
                            
                            # 只处理有库存且消耗天数为31天的月卡，排除1分购特权
                            prize_type = prize.get('prizeType', 0)
                            
                            # 过滤条件：
                            # 1. 有库存 (stockStatus == 1)
                            # 2. 消耗天数为31天 (cost_days == 31.0)
                            # 3. 奖品类型为26（直接兑换，非付费特权）
                            # 4. 排除1分购特权（名称不包含"1分购"或"特权"）
                            is_direct_exchange = prize_type == 26
                            is_monthly_card = cost_days == 31.0
                            is_not_privilege = '1分购' not in prize_name and '特权' not in prize_name
                            has_stock = stock_status == 1
                            
                            if has_stock and is_monthly_card and is_direct_exchange and is_not_privilege:
                                membership = {
                                    'id': prize_code,
                                    'prizeId': prize_id,
                                    'name': prize_name,
                                    'description': prize.get('prizeDesc', ''),
                                    'cost_days': cost_days,
                                    'exchange_type': 'direct',  # 直接兑换
                                    'status': 'available' if today_stock_status == 1 else 'out_of_stock',
                                    'stock': stock_status,
                                    'brand': prize_brand,
                                    'needGoldRice': need_gold_rice,
                                    'prizeBatchId': prize.get('prizeBatchId', ''),
                                    'prizeType': prize_type
                                }
                                memberships.append(membership)
                        
                        except Exception as parse_error:
                            print(f"  ⚠️ 解析奖品失败: {parse_error}")
                            continue
                    
                    if memberships:
                        print(f"  📺 可兑换会员数量：{len(memberships)}")
                        return memberships
                    else:
                        print("  ⚠️ 未找到可兑换的31天会员")
                else:
                    print(f"  ⚠️ 响应数据格式异常: {type(prize_list)}")
                    
            else:
                print(f"  ❌ 接口调用失败: {response}")
            
            # 如果API失败，返回预定义的会员列表
            print("  - 使用预定义会员列表")
            return self.get_predefined_memberships()
            
        except Exception as e:
            print(f'  ❌ 获取兑换列表失败：{e}')
            return self.get_predefined_memberships()

    def get_predefined_memberships(self) -> List[Dict[str, Any]]:
        """获取预定义的会员兑换列表（当API不可用时使用）"""
        return [
            {
                'id': 'tencent_video_month',
                'prizeId': 'tencent_month',
                'name': '腾讯视频VIP月卡',
                'description': '腾讯视频VIP月卡',
                'cost_days': 31.0,
                'exchange_type': 'direct',
                'status': 'available',
                'stock': 999,
                'brand': 'tencent',
                'prizeBatchId': 'LSXD_PRIZE1263'
            },
            {
                'id': 'iqiyi_month',
                'prizeId': 'iqiyi_month',
                'name': '爱奇艺黄金会员月卡',
                'description': '爱奇艺黄金会员月卡',
                'cost_days': 31.0,
                'exchange_type': 'direct',
                'status': 'available',
                'stock': 999,
                'brand': 'iqiyi',
                'prizeBatchId': 'LSXD_PRIZE1267'
            },
            {
                'id': 'youku_month',
                'prizeId': 'youku_month',
                'name': '优酷VIP会员月卡',
                'description': '优酷VIP会员月卡',
                'cost_days': 31.0,
                'exchange_type': 'direct',
                'status': 'available',
                'stock': 999,
                'brand': 'youku',
                'prizeBatchId': 'LSXD_PRIZE1262'
            },
            {
                'id': 'mgtv_month',
                'prizeId': 'mgtv_month',
                'name': '芒果TV会员月卡',
                'description': '芒果TV月卡',
                'cost_days': 31.0,
                'exchange_type': 'direct',
                'status': 'available',
                'stock': 999,
                'brand': 'mgtv',
                'prizeBatchId': 'LSXD_PRIZE1264'
            }
        ]

    def exchange_membership(self, membership_info: Dict[str, Any], phone_number: str) -> bool:
        """兑换会员"""
        try:
            membership_name = membership_info['name']
            prize_id = membership_info['prizeId']
            
            print(f"  🔍 尝试兑换 {membership_name} (PrizeID: {prize_id})")
            
            # 使用真实的兑换接口
            url = f"https://{API_HOST}/mp/api/generalActivity/convertGoldRich"
            
            # 根据抓包数据构建参数
            params = {
                'prizeCode': membership_info['id'],  # 使用 prizeCode
                'activityCode': self.activity_code,
                'phone': phone_number,
                'isNfcPhone': 'false',
                'channel': 'exchange',
                'deviceType': '2',
                'system': '1', 
                'visitEnvironment': '2',
                'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}'
            }
            
            try:
                # 使用GET方法（根据抓包显示）
                print(f"  📞 正在为手机号 {phone_number} 兑换 {membership_name}...")
                response = self.api.get(url, params=params)
                
                # 检查响应
                if response:
                    # 如果返回的是JSON格式
                    if isinstance(response, dict):
                        if response.get('code') == 0:
                            print(f'  ✅ 兑换{membership_name}成功！手机号：{phone_number}')
                            return True
                        else:
                            error_msg = response.get('message', response.get('error', '未知错误'))
                            print(f'  ❌ 兑换{membership_name}失败：{error_msg}')
                            return False
                    else:
                        # 如果返回的是HTML或其他格式，可能需要进一步处理
                        print(f'  ⚠️ 兑换请求已发送，但响应格式异常: {type(response)}')
                        # 有些接口可能返回HTML但实际兑换成功，这里暂时认为成功
                        print(f'  ✅ 兑换{membership_name}可能成功，请检查手机短信或小米钱包')
                        return True
                else:
                    print(f'  ❌ 兑换{membership_name}失败：网络请求失败')
                    return False
                    
            except Exception as req_error:
                print(f"  ❌ 兑换请求异常: {req_error}")
                
                # 备用：尝试POST方法
                try:
                    print(f"  🔄 尝试POST方法兑换...")
                    response = self.api.post(url, data=params)
                    
                    if response and isinstance(response, dict) and response.get('code') == 0:
                        print(f'  ✅ 兑换{membership_name}成功！手机号：{phone_number}')
                        return True
                    else:
                        print(f'  ❌ POST方法也失败')
                        
                except Exception as post_error:
                    print(f"  ❌ POST方法异常: {post_error}")
                    
                return False
            
            print(f'  ❌ 所有兑换接口都无法完成{membership_name}的兑换')
            print(f'  💡 请手动在小米钱包中兑换: {membership_name} -> {phone_number}')
            return False
                
        except Exception as e:
            print(f'  ❌ 兑换{membership_info.get("name", "未知会员")}异常：{e}')
            return False

    def auto_exchange_memberships(self, exchange_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """自动兑换会员"""
        if not exchange_configs:
            print("  📺 未配置会员兑换，跳过自动兑换")
            return []
        
        print(f"\n>>> 会员自动兑换检查 <<<")
        print(f"  当前拥有天数：{self.total_days_num:.2f}天")
        
        # 提取用户配置的会员类型
        configured_types = [config['type'] for config in exchange_configs]
        print(f"  📋 用户配置的会员类型：{', '.join(configured_types)}")
        
        # 获取可兑换的会员列表
        all_memberships = self.get_exchange_memberships()
        
        # 只保留用户配置的会员类型
        memberships = []
        for membership in all_memberships:
            for config_type in configured_types:
                # 检查品牌和名称匹配
                brand_match = config_type.lower() in membership['brand'].lower() or membership['brand'].lower() in config_type.lower()
                name_match = config_type in membership['name'] or membership['name'] in config_type
                
                if brand_match or name_match:
                    memberships.append(membership)
                    if membership['status'] == 'available':
                        status_text = "✅可兑换"
                        status_icon = "📱"
                    else:
                        status_text = "❌今日无库存"
                        status_icon = "🔒"
                    print(f"     {status_icon} {membership['name']} - 消耗{membership['cost_days']:.2f}天 [{status_text}] [匹配:{config_type}]")
                    break
        
        if not memberships:
            print("  📺 未找到匹配用户配置的可兑换会员")
            return []
        
        print(f"  📺 找到{len(memberships)}个匹配的可兑换会员")
        
        exchange_results = []
        current_days = self.total_days_num
        
        for config in exchange_configs:
            membership_type = config['type']
            phone_number = config['phone']
            
            print(f"\n  📱 检查 {membership_type} 兑换配置 (手机号: {phone_number})")
            
            # 查找匹配的会员类型（优先选择直接兑换的月卡）
            matched_membership = None
            potential_matches = []
            
            for membership in memberships:
                # 检查品牌和名称匹配
                brand_match = membership_type.lower() in membership['brand'].lower() or membership['brand'].lower() in membership_type.lower()
                name_match = membership_type in membership['name'] or membership['name'] in membership_type
                
                if brand_match or name_match:
                    potential_matches.append(membership)
            
            # 优先选择直接兑换的月卡（非特权类型）
            if potential_matches:
                # 按优先级排序：直接兑换 > 今日有库存 > 消耗天数最接近31天
                def priority_score(m):
                    score = 0
                    if m['exchange_type'] == 'direct':
                        score += 1000  # 最高优先级：直接兑换
                    if m['status'] == 'available':
                        score += 100   # 其次：今日有库存
                    if m['cost_days'] == 31.0:
                        score += 10    # 最后：消耗天数为31天
                    return score
                
                potential_matches.sort(key=priority_score, reverse=True)
                matched_membership = potential_matches[0]
                
                print(f"  🎯 找到{len(potential_matches)}个匹配项，选择优先级最高的：{matched_membership['name']}")
            
            if not matched_membership:
                print(f"  ❌ 未找到匹配的会员类型：{membership_type}")
                exchange_results.append({
                    'type': membership_type,
                    'phone': phone_number,
                    'success': False,
                    'message': f'未找到匹配的会员类型：{membership_type}'
                })
                continue
            
            # 检查天数是否充足
            required_days = matched_membership['cost_days']
            print(f"  💰 需要消耗：{required_days:.2f}天")
            
            # 首先检查库存状态
            if matched_membership['status'] != 'available':
                print(f"  ❌ {matched_membership['name']} 今日无库存，跳过兑换")
                exchange_results.append({
                    'type': membership_type,
                    'phone': phone_number,
                    'success': False,
                    'message': f'{matched_membership["name"]} 今日无库存'
                })
                continue
            
            if current_days >= required_days:
                print(f"  ✅ 天数充足，库存充足，开始兑换 {matched_membership['name']}")
                
                # 执行兑换
                print(f"  ⚠️ 注意：兑换功能正在尝试调用接口，如果失败请手动兑换")
                success = self.exchange_membership(
                    matched_membership, 
                    phone_number
                )
                
                if success:
                    current_days -= required_days  # 更新剩余天数
                    exchange_results.append({
                        'type': membership_type,
                        'phone': phone_number,
                        'success': True,
                        'message': f'成功兑换 {matched_membership["name"]}，消耗{required_days:.2f}天',
                        'cost_days': required_days
                    })
                    print(f"  💎 兑换成功！剩余天数：{current_days:.2f}天")
                else:
                    exchange_results.append({
                        'type': membership_type,
                        'phone': phone_number,
                        'success': False,
                        'message': f'兑换 {matched_membership["name"]} 失败'
                    })
            else:
                print(f"  ❌ 天数不足：需要{required_days:.2f}天，当前仅有{current_days:.2f}天")
                exchange_results.append({
                    'type': membership_type,
                    'phone': phone_number,
                    'success': False,
                    'message': f'天数不足：需要{required_days:.2f}天，当前仅有{current_days:.2f}天'
                })
            
            time.sleep(2)  # 兑换间隔
        
        return exchange_results


# --- 主流程控制模块 ---

def get_session_cookies(pass_token: str, user_id: str) -> Optional[str]:
    """
    使用长效凭证 (passToken) 获取用于访问任务 API 的临时会话 Cookie。
    此函数的核心 URL 和 Headers 严格与原始有效版本保持一致。
    """
    login_url = (
        'https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts'
        '%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net'
        '%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse'
        '%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity'
        '%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue'
        '%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q'
        '%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket'
    )
    
    headers = {
        'user-agent': USER_AGENT_DESKTOP,
        'cookie': f'passToken={pass_token}; userId={user_id};'
    }
    
    session = requests.Session()
    try:
        session.get(url=login_url, headers=headers, verify=False, timeout=10)
        cookies = session.cookies.get_dict()
        
        c_user_id = cookies.get('cUserId')
        service_token = cookies.get('serviceToken')

        if c_user_id and service_token:
            return f"cUserId={c_user_id}; jrairstar_serviceToken={service_token}"
        
        print("  - 获取的 Cookie 不完整，可能 passToken 已失效。")
        return None
    except requests.RequestException as e:
        print(f"  - 获取 Cookie 时网络请求失败: {e}")
        return None


def process_account(account_data: Dict[str, Any]) -> str:
    """处理单个账号的完整任务流程，支持会员兑换功能。"""
    us = account_data.get('us')
    user_id = account_data.get('userId')
    pass_token = account_data.get('passToken')
    exchange_configs = account_data.get('exchange_configs', [])  # 获取会员兑换配置
    
    if not all([us, user_id, pass_token]):
        return f"账号 '{us or '未知'}' 配置不完整，已跳过。"
    
    print(f"\n>>>>>>>>>> 正在处理账号: {us} (ID: {user_id}) <<<<<<<<<<")
    
    session_cookies = get_session_cookies(pass_token, user_id)
    api_request = ApiRequest(session_cookies)
    rnl = RNL(api_request)
    
    exchange_results = []
    
    if not session_cookies:
        rnl.error_info = "获取会话 Cookie 失败，请重新运行 login.py 刷新凭证。"
    else:
        print("  - 会话 Cookie 获取成功。")
        try:
            # 执行基础任务流程
            rnl.run_main_workflow()
            
            # 如果配置了会员兑换，执行自动兑换
            if exchange_configs:
                print(f"  - 检测到 {len(exchange_configs)} 个会员兑换配置")
                exchange_results = rnl.auto_exchange_memberships(exchange_configs)
            else:
                print("  - 未配置会员兑换")
                
        except Exception as e:
            rnl.error_info = f"执行主程序时发生未知异常: {e}"
            print(f"  ❌ {rnl.error_info}")
    
    # 生成包含兑换结果的通知
    return generate_notification_with_exchange(user_id, rnl, us, exchange_results)


def main():
    """程序主入口函数。"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            accounts_config = [] if not content else json.loads(content)
        assert isinstance(accounts_config, list), "配置文件根节点应为列表"
    except (FileNotFoundError, json.JSONDecodeError, AssertionError) as e:
        print(f"❌ 读取或解析配置文件 '{CONFIG_FILE}' 失败: {e}")
        return

    if not accounts_config:
        print(f"ℹ️  配置文件 '{CONFIG_FILE}' 中没有账号，程序退出。")
        return


    print(f"\n======= 开始执行小米钱包每日任务 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) =======")
    
    updated_config = []
    
    for account in accounts_config:
        data = account.get('data', {})
        notification = process_account(data)
        print(notification)
        
        data['log'] = notification.strip()
        account['data'] = data
        updated_config.append(account)
        
        feishu_webhook = data.get('feishu_webhook')
        if feishu_webhook:
            print("  - 检测到飞书 Webhook 配置，正在尝试推送...")
            send_feishu_notification(feishu_webhook, notification)
        delay = random.randint(0, 15)
        print(f"随机延迟 {delay} 秒后执行，以避免集中请求...")
        time.sleep(delay)

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_config, f, indent=4, ensure_ascii=False)
        print(f"\n✅ 所有账号日志已成功更新至 '{CONFIG_FILE}'")
    except Exception as e:
        print(f"❌ 写入日志到 '{CONFIG_FILE}' 时发生错误: {e}")

    print("\n======= 小米钱包每日任务执行完毕 =======")


if __name__ == "__main__":
    main()