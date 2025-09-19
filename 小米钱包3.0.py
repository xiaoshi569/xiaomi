import os
import time
import requests
import urllib3
import platform
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, Union

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Push Plus 配置
PUSH_PLUS_TOKEN = os.environ.get('PUSH_PLUS_TOKEN', '')

# 授权验证配置
LICENSE_KEY = os.environ.get('LICENSE_KEY', '')
AUTH_SERVER_URL = os.environ.get('AUTH_SERVER_URL', 'http://110.41.43.81:5000')

class RnlRequest:
    def __init__(self, cookies: Union[str, dict]):
        self.session = requests.Session()
        self._base_headers = {
            'Host': 'm.jr.airstarfinance.net',
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; AppBundle/com.mipay.wallet; AppVersionName/6.89.1.5275.2323; AppVersionCode/20577595; MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36 XiaoMi/MiuiBrowser/4.3',
        }
        self.update_cookies(cookies)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        headers = {**self._base_headers, **kwargs.pop('headers', {})}
        try:
            resp = self.session.request(
                verify=False,
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                **kwargs
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"[Request Error] {e}")  # 保留基础错误提示（可选）
        except ValueError as e:
            print(f"[JSON Parse Error] {e}")  # 保留基础错误提示（可选）
        return None

    def update_cookies(self, cookies: Union[str, dict]) -> None:
        if cookies:
            if isinstance(cookies, str):
                dict_cookies = self._parse_cookies(cookies)
            else:
                dict_cookies = cookies
            self.session.cookies.update(dict_cookies)
            self._base_headers['Cookie'] = self.dict_cookie_to_string(dict_cookies)

    @staticmethod
    def _parse_cookies(cookies_str: str) -> Dict[str, str]:
        return dict(
            item.strip().split('=', 1)
            for item in cookies_str.split(';')
            if '=' in item
        )

    @staticmethod
    def dict_cookie_to_string(cookie_dict):
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append(f"{key}={value}")
        return "; ".join(cookie_list)

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None,
             json: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('POST', url, data=data, json=json, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class RNL:
    def __init__(self, c):
        self.t_id = None
        self.options = {
            "task_list": True,
            "complete_task": True,
            "receive_award": True,
            "task_item": True,
            "UserJoin": True,
        }
        self.activity_code = '2211-videoWelfare'
        self.rr = RnlRequest(c)

    def get_task_list(self):
        data = {
            'activityCode': self.activity_code,
        }
        try:
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTaskList',
                data=data,
            )
            if response and response['code'] != 0:
                print(response)
                return None
            target_tasks = []
            for task in response['value']['taskInfoList']:
                if '浏览组浏览任务' in task['taskName']:
                    target_tasks.append(task)
            return target_tasks
        except Exception as e:
            print(f'获取任务列表失败：{e}')
            return None

    def get_task(self, task_code):
        try:
            data = {
                'activityCode': self.activity_code,
                'taskCode': task_code,
                'jrairstar_ph': '98lj8puDf9Tu/WwcyMpVyQ==',
            }
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTask',
                data=data,
            )
            if response and response['code'] != 0:
                print(f'获取任务信息失败：{response}')
                return None
            return response['value']['taskInfo']['userTaskId']
        except Exception as e:
            print(f'获取任务信息失败：{e}')
            return None

    def complete_task(self, task_id, t_id, brows_click_urlId):
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/completeTask?activityCode={self.activity_code}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&taskId={task_id}&browsTaskId={t_id}&browsClickUrlId={brows_click_urlId}&clickEntryType=undefined&festivalStatus=0',
            )
            if response and response['code'] != 0:
                print(f'完成任务失败：{response}')
                return None
            return response['value']
        except Exception as e:
            print(f'完成任务失败：{e}')
            return None

    def receive_award(self, user_task_id):
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/luckDraw?imei=&device=manet&appLimit=%7B%22com.qiyi.video%22:false,%22com.youku.phone%22:true,%22com.tencent.qqlive%22:true,%22com.hunantv.imgo.activity%22:true,%22com.cmcc.cmvideo%22:false,%22com.sankuai.meituan%22:true,%22com.anjuke.android.app%22:false,%22com.tal.abctimelibrary%22:false,%22com.lianjia.beike%22:false,%22com.kmxs.reader%22:true,%22com.jd.jrapp%22:false,%22com.smile.gifmaker%22:true,%22com.kuaishou.nebula%22:false%7D&activityCode={self.activity_code}&userTaskId={user_task_id}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D'
            )
            if response and response['code'] != 0:
                print(f'领取奖励失败：{response}')
        except Exception as e:
            print(f'领取奖励失败：{e}')

    def complete_new_user_task(self):
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
            
            url = 'https://m.jr.airstarfinance.net/mp/api/generalActivity/completeTask?activityCode=2211-videoWelfare&app=com.mipay.wallet&oaid=8c45c5802867e923&regId=KWkK5VsKXiIbAH8Rf6kgU6tpDPyNWgXY8YCM1mQtt5nd7i1%2F4BqzPq0uY7OlIEOd&versionCode=20577622&versionName=6.96.0.5453.2620&isNfcPhone=true&channel=mipay_indexicon_TVcard2test&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.video%22:%22v2023091090(MiVideo-ROM)%22,%22com.mipay.wallet%22:%226.96.0.5453.2620%22%7D&taskCode=NEW_USER_CAMPAIGN&browsTaskId=&browsClickUrlId=1306285&adInfoId=&triggerId='
            
            response = self.rr.get(url, headers=headers)
            if response and response['code'] != 0:
                print(f'完成应用下载试用失败：{response}')
                return None
            print(f'完成应用下载试用成功，获得userTaskId: {response["value"]}')
            return response['value']
        except Exception as e:
            print(f'完成应用下载试用失败：{e}')
            return None

    def receive_new_user_award(self, user_task_id):
        """领取应用下载试用奖励"""
        try:
            # 发送领取请求前延时5秒
            print("等待5秒后领取奖励...")
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
            
            url = f'https://m.jr.airstarfinance.net/mp/api/generalActivity/luckDraw?imei=&device=alioth&appLimit=%7B%22com.qiyi.video%22:false,%22com.youku.phone%22:false,%22com.tencent.qqlive%22:false,%22com.hunantv.imgo.activity%22:false,%22com.cmcc.cmvideo%22:false,%22com.sankuai.meituan%22:false,%22com.anjuke.android.app%22:false,%22com.tal.abctimelibrary%22:false,%22com.lianjia.beike%22:false,%22com.kmxs.reader%22:false,%22com.jd.jrapp%22:false,%22com.smile.gifmaker%22:true,%22com.kuaishou.nebula%22:false%7D&activityCode=2211-videoWelfare&userTaskId={user_task_id}&app=com.mipay.wallet&oaid=8c45c5802867e923&regId=L522i5qLZR9%2Bs25kEqPBJYbbHqUS4LrpuTsgl9kdsbcyU7tjWmx1BewlRNSSZaOT&versionCode=20577622&versionName=6.96.0.5453.2620&isNfcPhone=true&channel=mipay_indexicon_TVcard2test&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.video%22:%22v2023091090(MiVideo-ROM)%22,%22com.mipay.wallet%22:%226.96.0.5453.2620%22%7D'
            
            response = self.rr.get(url, headers=headers)
            if response and response['code'] != 0:
                print(f'领取应用下载试用务奖励失败：{response}')
                return False
            
            prize_info = response['value']['prizeInfo']
            print(f'领取应用下载试用奖励成功：获得{prize_info["amount"]} {prize_info["prizeDesc"]}')
            return True
        except Exception as e:
            print(f'领取应用下载试用奖励失败：{e}')
            return False

    def queryUserJoinListAndQueryUserGoldRichSum(self):
        try:
            total_res = self.rr.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserGoldRichSum?app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}&activityCode=2211-videoWelfare')
            if not total_res or total_res['code'] != 0:
                print(f'获取兑换视频天数失败：{total_res}')
                return None
            total_days = f"{int(total_res['value']) / 100:.2f}天" if total_res else "未知"
            total_days_num = int(total_res['value']) / 100 if total_res else 0

            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserJoinList?&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&activityCode={self.activity_code}&pageNum=1&pageSize=20',
            )
            if not response or response['code'] != 0:
                print(f'查询任务完成记录失败：{response}')
                return None

            history_list = response['value']['data']
            current_date = datetime.now().strftime("%Y-%m-%d")
            print(f"当前用户兑换视频天数：{total_days}")
            print(f"------------ {current_date} 当天任务记录 ------------")

            today_records = []
            for a in history_list:
                record_time = a['createTime']
                record_date = record_time[:10]
                if record_date == current_date:
                    days = int(a['value']) / 100
                    record_info = f"{record_time} 领到视频会员，+{days:.2f}天"
                    print(record_info)
                    today_records.append({
                        'time': record_time,
                        'days': days,
                        'info': record_info
                    })

            # 返回详细数据
            return {
                'total_days': total_days,
                'total_days_num': total_days_num,  # 添加数值版本的天数
                'current_date': current_date,
                'today_records': today_records,
                'total_records_count': len(today_records)
            }
        except Exception as e:
            print(f'获取任务记录失败：{e}')
            return None

    def get_exchange_memberships(self):
        """获取可兑换的会员列表"""
        try:
            # 使用真实的奖品状态接口
            print("🔍 尝试真实接口: getPrizeStatusV2")
            url = 'https://m.jr.airstarfinance.net/mp/api/generalActivity/getPrizeStatusV2'
            params = {
                'activityCode': self.activity_code,
                'needPrizeBrand': 'youku,mgtv,iqiyi,tencent,bilibili,other'
            }
            
            response = self.rr.get(url, params=params)
            
            if response and response.get('code') == 0:
                print(f"✅ 接口调用成功: getPrizeStatusV2")
                
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
                            print(f"   ⚠️ 解析奖品失败: {parse_error}")
                            continue
                    
                    if memberships:
                        print(f"📺 可兑换会员数量：{len(memberships)}")
                        return memberships
                    else:
                        print("⚠️ 未找到可兑换的31天会员")
                else:
                    print(f"⚠️ 响应数据格式异常: {type(prize_list)}")
                    
            else:
                print(f"❌ 接口调用失败: {response}")
            
            # 如果真实接口失败，尝试其他可能的接口
            print("🔍 尝试其他可能的兑换接口...")
            fallback_urls = [
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getExchangeList',
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryPrizeList',
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getPrizeList'
            ]
            
            base_params = {
                'activityCode': self.activity_code,
                'app': 'com.mipay.wallet',
                'deviceType': '2',
                'system': '1',
                'visitEnvironment': '2'
            }
            
            for fallback_url in fallback_urls:
                try:
                    print(f"🔍 尝试备用接口: {fallback_url}")
                    response = self.rr.get(fallback_url, params=base_params)
                    
                    if response and response.get('code') == 0:
                        print(f"✅ 备用接口调用成功: {fallback_url}")
                        # 这里可以根据实际响应格式解析数据
                        # 现在先返回空，如果有数据再补充解析逻辑
                        break
                        
                except Exception as e:
                    print(f"❌ 备用接口异常: {e}")
                    continue
            
            print("❌ 所有接口都无法获取数据，使用预定义列表")
            return []
            
        except Exception as e:
            print(f'获取兑换列表失败：{e}')
            return []

    def _parse_cost_days(self, item):
        """解析消耗天数的通用方法"""
        try:
            # 尝试多种可能的字段名
            for field in ['costValue', 'cost', 'price', 'needDays', 'days']:
                if field in item and item[field] is not None:
                    value = item[field]
                    if isinstance(value, str):
                        # 尝试提取数字
                        import re
                        numbers = re.findall(r'\d+', value)
                        if numbers:
                            return int(numbers[0]) / 100
                    elif isinstance(value, (int, float)):
                        return float(value) / 100
            
            # 如果没有找到，尝试从描述中提取
            desc = item.get('description', item.get('desc', ''))
            if desc:
                import re
                # 寻找类似 "30天" 或 "消耗30天" 的模式
                days_match = re.search(r'(\d+)天', desc)
                if days_match:
                    return float(days_match.group(1))
                    
                # 寻找类似 "3000" 的数字（可能是积分）
                number_match = re.search(r'(\d+)', desc)
                if number_match:
                    return float(number_match.group(1)) / 100
            
            # 默认返回31天（一个月会员的常见消耗）
            return 31.0
            
        except Exception as e:
            print(f"⚠️ 解析消耗天数失败: {e}")
            return 31.0

    def exchange_membership(self, membership_info, phone_number):
        """兑换会员"""
        try:
            membership_name = membership_info['name']
            prize_id = membership_info['prizeId']
            prize_batch_id = membership_info.get('prizeBatchId', '')
            
            print(f"🔍 尝试兑换 {membership_name} (PrizeID: {prize_id})")
            
            # 使用真实的兑换接口
            print(f"🔍 使用真实兑换接口: convertGoldRich")
            url = 'https://m.jr.airstarfinance.net/mp/api/generalActivity/convertGoldRich'
            
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
                print(f"📞 正在为手机号 {phone_number} 兑换 {membership_name}...")
                response = self.rr.get(url, params=params)
                
                # 检查响应
                if response:
                    # 如果返回的是JSON格式
                    if isinstance(response, dict):
                        if response.get('code') == 0:
                            print(f'✅ 兑换{membership_name}成功！手机号：{phone_number}')
                            return True
                        else:
                            error_msg = response.get('message', response.get('error', '未知错误'))
                            print(f'❌ 兑换{membership_name}失败：{error_msg}')
                            return False
                    else:
                        # 如果返回的是HTML或其他格式，可能需要进一步处理
                        print(f'⚠️ 兑换请求已发送，但响应格式异常: {type(response)}')
                        # 有些接口可能返回HTML但实际兑换成功，这里暂时认为成功
                        print(f'✅ 兑换{membership_name}可能成功，请检查手机短信或小米钱包')
                        return True
                else:
                    print(f'❌ 兑换{membership_name}失败：网络请求失败')
                    return False
                    
            except Exception as req_error:
                print(f"❌ 兑换请求异常: {req_error}")
                
                # 备用：尝试POST方法
                try:
                    print(f"🔄 尝试POST方法兑换...")
                    response = self.rr.post(url, data=params)
                    
                    if response and isinstance(response, dict) and response.get('code') == 0:
                        print(f'✅ 兑换{membership_name}成功！手机号：{phone_number}')
                        return True
                    else:
                        print(f'❌ POST方法也失败')
                        
                except Exception as post_error:
                    print(f"❌ POST方法异常: {post_error}")
                    
                return False
            
            print(f'❌ 所有兑换接口都无法完成{membership_name}的兑换')
            print(f'💡 请手动在小米钱包中兑换: {membership_name} -> {phone_number}')
            return False
                
        except Exception as e:
            print(f'❌ 兑换{membership_info.get("name", "未知会员")}异常：{e}')
            return False

    def get_predefined_memberships(self):
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

    def auto_exchange_memberships(self, exchange_configs, current_days):
        """自动兑换会员"""
        if not exchange_configs:
            print("📺 未配置会员兑换，跳过自动兑换")
            return []
        
        print(f"\n>>> 会员自动兑换检查 <<<")
        print(f"当前拥有天数：{current_days:.2f}天")
        
        # 提取用户配置的会员类型
        configured_types = [config['type'] for config in exchange_configs]
        print(f"📋 用户配置的会员类型：{', '.join(configured_types)}")
        
        # 获取可兑换的会员列表
        all_memberships = self.get_exchange_memberships()
        if not all_memberships:
            print("📺 API获取兑换列表失败，使用预定义会员列表")
            all_memberships = self.get_predefined_memberships()
        
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
                    print(f"   {status_icon} {membership['name']} - 消耗{membership['cost_days']:.2f}天 [{status_text}] [匹配:{config_type}]")
                    break
        
        if not memberships:
            print("📺 未找到匹配用户配置的可兑换会员")
            return []
        
        print(f"📺 找到{len(memberships)}个匹配的可兑换会员")
        
        exchange_results = []
        
        for config in exchange_configs:
            membership_type = config['type']
            phone_number = config['phone']
            
            print(f"\n📱 检查 {membership_type} 兑换配置 (手机号: {phone_number})")
            
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
                
                print(f"🎯 找到{len(potential_matches)}个匹配项，选择优先级最高的：{matched_membership['name']}")
            
            if not matched_membership:
                print(f"❌ 未找到匹配的会员类型：{membership_type}")
                exchange_results.append({
                    'type': membership_type,
                    'phone': phone_number,
                    'success': False,
                    'message': f'未找到匹配的会员类型：{membership_type}'
                })
                continue
            
            # 检查天数是否充足
            required_days = matched_membership['cost_days']
            print(f"💰 需要消耗：{required_days:.2f}天")
            
            # 首先检查库存状态
            if matched_membership['status'] != 'available':
                print(f"❌ {matched_membership['name']} 今日无库存，跳过兑换")
                exchange_results.append({
                    'type': membership_type,
                    'phone': phone_number,
                    'success': False,
                    'message': f'{matched_membership["name"]} 今日无库存'
                })
                continue
            
            if current_days >= required_days:
                print(f"✅ 天数充足，库存充足，开始兑换 {matched_membership['name']}")
                
                # 执行兑换
                print(f"⚠️ 注意：兑换功能正在尝试调用接口，如果失败请手动兑换")
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
                    print(f"💎 兑换成功！剩余天数：{current_days:.2f}天")
                else:
                    exchange_results.append({
                        'type': membership_type,
                        'phone': phone_number,
                        'success': False,
                        'message': f'兑换 {matched_membership["name"]} 失败'
                    })
            else:
                print(f"❌ 天数不足：需要{required_days:.2f}天，当前仅有{current_days:.2f}天")
                exchange_results.append({
                    'type': membership_type,
                    'phone': phone_number,
                    'success': False,
                    'message': f'天数不足：需要{required_days:.2f}天，当前仅有{current_days:.2f}天'
                })
            
            time.sleep(2)  # 兑换间隔
        
        return exchange_results

    def main(self, exchange_configs=None):
        # 获取执行前的数据
        initial_data = self.queryUserJoinListAndQueryUserGoldRichSum()
        if not initial_data:
            return {'success': False, 'error': '获取初始数据失败'}
        
        # 先尝试完成新手任务
        print("\n>>> 应用下载试用任务 <<<")
        new_user_task_id = self.complete_new_user_task()
        if new_user_task_id:
            time.sleep(2)
            self.receive_new_user_award(new_user_task_id)
            time.sleep(2)
        
        # 原有的浏览任务逻辑
        for i in range(2):
            # 获取任务列表
            tasks = self.get_task_list()
            if not tasks:
                print("未找到浏览任务，跳过")
                continue
                
            task = tasks[0]
            try:
                t_id = task['generalActivityUrlInfo']['id']
                self.t_id = t_id
            except:
                t_id = self.t_id
            task_id = task['taskId']
            task_code = task['taskCode']
            brows_click_url_id = task['generalActivityUrlInfo']['browsClickUrlId']

            time.sleep(13)

            # 完成任务
            user_task_id = self.complete_task(
                t_id=t_id,
                task_id=task_id,
                brows_click_urlId=brows_click_url_id,
            )

            time.sleep(2)

            # 获取任务数据
            if not user_task_id:
                user_task_id = self.get_task(task_code=task_code)
                time.sleep(2)

            # 领取奖励
            self.receive_award(
                user_task_id=user_task_id
            )

            time.sleep(2)
        
        # 获取执行后的数据
        final_data = self.queryUserJoinListAndQueryUserGoldRichSum()
        if not final_data:
            return {'success': False, 'error': '获取最终数据失败'}
        
        # 执行会员自动兑换
        exchange_results = []
        if exchange_configs:
            current_days = final_data.get('total_days_num', 0)
            exchange_results = self.auto_exchange_memberships(exchange_configs, current_days)
        
        return {
            'success': True,
            'total_days': final_data['total_days'],
            'current_date': final_data['current_date'],
            'today_records': final_data['today_records'],
            'total_records_count': final_data['total_records_count'],
            'exchange_results': exchange_results  # 添加兑换结果
        }


def get_device_id():
    """
    获取设备唯一标识
    """
    try:
        # 获取主机名和机器类型组合作为设备标识
        info = platform.node() + platform.machine() + platform.system()
        # 生成MD5哈希并取前16位作为设备ID
        device_id = hashlib.md5(info.encode()).hexdigest()[:16]
        return device_id
    except Exception as e:
        print(f"❌ 获取设备ID失败：{e}")
        # 使用备用方案
        return hashlib.md5("backup_device_id".encode()).hexdigest()[:16]

def verify_license():
    """
    验证授权码
    """
    if not LICENSE_KEY:
        print("❌ 未配置授权码 (LICENSE_KEY)")
        return False
    
    device_id = get_device_id()
    print(f"🔑 设备ID: {device_id}")
    print(f"🔐 正在验证授权码...")
    
    try:
        url = f"{AUTH_SERVER_URL}/verify"
        data = {
            "key": LICENSE_KEY,
            "device_id": device_id
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('valid', False):
            print(f"✅ 授权验证成功: {result.get('message', '验证通过')}")
            return True
        else:
            print(f"❌ 授权验证失败: {result.get('message', '验证失败')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 授权验证超时，请检查网络连接")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到授权服务器，请检查服务器地址")
        return False
    except Exception as e:
        print(f"❌ 授权验证异常：{e}")
        return False

def send_pushplus_notification(title, content):
    """
    发送Push Plus通知
    """
    if not PUSH_PLUS_TOKEN:
        return False
    
    try:
        url = "http://www.pushplus.plus/send"
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "txt"
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            print(f"📧 Push Plus通知发送成功")
            return True
        else:
            print(f"❌ Push Plus通知发送失败：{result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ Push Plus通知发送异常：{e}")
        return False

def parse_accounts_from_env():
    """
    从环境变量解析账号信息
    格式：账号名#passToken=xxx;userId=xxx;腾讯视频#18819397965;爱奇艺#13812345678  多账号用&分隔
    环境变量名：XIAOMI_ACCOUNTS
    """
    env_var = os.environ.get('XIAOMI_ACCOUNTS', '')
    if not env_var:
        print("❌ 未找到环境变量 XIAOMI_ACCOUNTS")
        return []
    
    accounts = []
    for account_str in env_var.split('&'):
        account_str = account_str.strip()
        if not account_str:
            continue
            
        try:
            # 分离账号名和配置信息
            if '#' in account_str:
                parts = account_str.split('#')
                account_name = parts[0].strip()
                config_part = '#'.join(parts[1:])
            else:
                account_name = f"账号{len(accounts)+1}"
                config_part = account_str
            
            # 解析passToken、userId和会员兑换配置
            config_dict = {}
            exchange_configs = []
            
            for item in config_part.split(';'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    config_dict[key.strip()] = value.strip()
                elif '#' in item:
                    # 解析会员兑换配置，格式：腾讯视频#18819397965
                    membership_type, phone = item.split('#', 1)
                    exchange_configs.append({
                        'type': membership_type.strip(),
                        'phone': phone.strip()
                    })
            
            if 'passToken' in config_dict and 'userId' in config_dict:
                account_info = {
                    'name': account_name,
                    'passToken': config_dict['passToken'],
                    'userId': config_dict['userId'],
                    'exchange_configs': exchange_configs
                }
                accounts.append(account_info)
                print(f"✅ 成功解析账号：{account_name}")
                if exchange_configs:
                    for config in exchange_configs:
                        print(f"   📱 会员兑换配置：{config['type']} -> {config['phone']}")
            else:
                print(f"❌ 账号配置格式错误：{account_str}")
                
        except Exception as e:
            print(f"❌ 解析账号配置失败：{account_str}，错误：{e}")
    
    return accounts

def get_xiaomi_cookies(pass_token, user_id):
    session = requests.Session()
    login_url = 'https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'cookie': f'passToken={pass_token}; userId={user_id};'
    }

    try:
        session.get(url=login_url, headers=headers, verify=False)
        cookies = session.cookies.get_dict()
        return f"cUserId={cookies.get('cUserId')};jrairstar_serviceToken={cookies.get('serviceToken')}"
    except Exception as e:
        print(f"获取Cookie失败: {e}")
        return None

if __name__ == "__main__":
    print("🚀 小米钱包3.0脚本启动")
    print("📖 环境变量格式：")
    print("   XIAOMI_ACCOUNTS=账号名#passToken=xxx;userId=xxx;腾讯视频#18819397965;爱奇艺#13812345678&账号名2#passToken=xxx;userId=xxx")
    print("   LICENSE_KEY=你的授权码，必填")
    print("💡 会员兑换说明：在账号配置中添加 '会员类型#手机号' 格式的配置即可自动兑换（当天数≥31天时自动兑换）")
    print("⚠️ 兑换功能提示：由于小米钱包接口可能变化，兑换功能会尝试多个接口，如果自动兑换失败，请手动兑换")
    if PUSH_PLUS_TOKEN:
        print("📧 已配置Push Plus通知")
    else:
        print("📧 未配置Push Plus通知")
    print("=" * 60)
    
    # 授权验证 - 必须验证成功才能继续
    print("🔐 开始授权验证...")
    if not verify_license():
        error_msg = "❌ 授权验证失败，脚本退出"
        print(error_msg)
        send_pushplus_notification("小米钱包脚本授权失败", f"<p>{error_msg}</p><p>请检查授权码配置或联系管理员</p>")
        exit(1)
    
    print("✅ 授权验证通过，继续执行脚本...")
    print("=" * 60)
    
    # 从环境变量获取账号配置
    accounts = parse_accounts_from_env()
    
    if not accounts:
        error_msg = "❌ 未找到有效的账号配置，请检查环境变量 XIAOMI_ACCOUNTS"
        print(error_msg)
        send_pushplus_notification("小米钱包脚本执行失败", f"<p>{error_msg}</p><p>请检查环境变量配置</p>")
        exit(1)
    
    print(f"📊 共解析到 {len(accounts)} 个账号配置")
    
    # 获取Cookie
    cookie_list = []
    for account in accounts:
        print(f"\n>>>>>>>>>> 正在处理账号 {account['name']} (ID: {account['userId']}) <<<<<<<<<<")
        new_cookie = get_xiaomi_cookies(account['passToken'], account['userId'])
        if new_cookie:
            cookie_list.append({
                'cookie': new_cookie,
                'name': account['name'],
                'userId': account['userId'],
                'exchange_configs': account.get('exchange_configs', [])  # 添加兑换配置
            })
            print(f"✅ 账号 {account['name']} Cookie获取成功")
        else:
            print(f"❌ 账号 {account['name']} Cookie获取失败，请检查配置")

    print(f"\n>>>>>>>>>> 共获取到 {len(cookie_list)} 个有效Cookie <<<<<<<<<<")
    
    if not cookie_list:
        error_msg = "❌ 没有获取到任何有效的Cookie，脚本退出"
        print(error_msg)
        send_pushplus_notification("小米钱包脚本执行失败", f"<p>{error_msg}</p><p>请检查账号配置</p>")
        exit(1)

    # 执行任务
    account_results = []
    
    for index, account_info in enumerate(cookie_list):
        print(f"\n--------- 开始执行第{index+1}个账号：{account_info['name']} ---------")
        try:
            # 传递兑换配置给main方法
            result = RNL(account_info['cookie']).main(account_info.get('exchange_configs', []))
            if result and result.get('success'):
                account_results.append({
                    'name': account_info['name'],
                    'userId': account_info['userId'],
                    'status': 'success',
                    'total_days': result.get('total_days', '未知'),
                    'current_date': result.get('current_date', ''),
                    'today_records': result.get('today_records', []),
                    'total_records_count': result.get('total_records_count', 0),
                    'exchange_results': result.get('exchange_results', [])  # 添加兑换结果
                })
                print(f"✅ 账号 {account_info['name']} 执行完成")
            else:
                error_msg = result.get('error', '执行失败') if result else '执行失败'
                account_results.append({
                    'name': account_info['name'],
                    'userId': account_info['userId'],
                    'status': 'failed',
                    'error': error_msg
                })
                print(f"❌ 账号 {account_info['name']} 执行失败: {error_msg}")
        except Exception as e:
            account_results.append({
                'name': account_info['name'],
                'userId': account_info['userId'],
                'status': 'failed',
                'error': str(e)
            })
            print(f"❌ 账号 {account_info['name']} 执行异常: {str(e)}")
        print(f"--------- 第{index+1}个账号执行结束 ---------")
    
    # 汇总结果
    total_accounts = len(account_results)
    success_results = [r for r in account_results if r['status'] == 'success']
    failed_results = [r for r in account_results if r['status'] == 'failed']
    success_count = len(success_results)
    failed_count = len(failed_results)
    
    result_summary = f"\n🎉 所有账号处理完成！\n📊 执行结果统计：\n✅ 成功：{success_count}个\n❌ 失败：{failed_count}个\n📝 总计：{total_accounts}个"
    print(result_summary)
    
    # 发送Push Plus通知
    if PUSH_PLUS_TOKEN:
        notification_content = f"📊 小米钱包脚本执行结果\n"
        notification_content += f"总账号数：{total_accounts}个\n"
        notification_content += f"✅ 成功：{success_count}个\n"
        notification_content += f"❌ 失败：{failed_count}个\n"
        notification_content += f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        notification_content += "=" * 40 + "\n\n"
        
        # 添加成功账号的详细信息
        for result in success_results:
            notification_content += f"✅ {result['name']} (ID: {result['userId']})\n"
            notification_content += f"当前兑换视频天数：{result['total_days']}\n"
            notification_content += f"---------- {result['current_date']} 当天任务记录 ----------\n"
            
            if result['today_records']:
                for record in result['today_records']:
                    notification_content += f"{record['info']}\n"
            else:
                notification_content += "今日暂无任务记录\n"
            
            # 添加会员兑换结果
            exchange_results = result.get('exchange_results', [])
            if exchange_results:
                notification_content += f"---------- 会员兑换结果 ----------\n"
                for exchange in exchange_results:
                    if exchange['success']:
                        notification_content += f"✅ {exchange['type']} -> {exchange['phone']}: {exchange['message']}\n"
                    else:
                        notification_content += f"❌ {exchange['type']} -> {exchange['phone']}: {exchange['message']}\n"
            else:
                notification_content += "---------- 无会员兑换配置 ----------\n"
            
            notification_content += "\n"
        
        # 添加失败账号信息
        if failed_results:
            notification_content += "❌ 失败账号\n"
            for result in failed_results:
                notification_content += f"{result['name']}: {result.get('error', '未知错误')}\n"
        
        title = f"小米钱包脚本完成 ({success_count}/{total_accounts})"
        send_pushplus_notification(title, notification_content)
