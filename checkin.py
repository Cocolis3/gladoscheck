#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import time
import requests
from datetime import datetime, timezone, timedelta


class GLaDOSCheckin:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://glados.rocks',
            'Referer': 'https://glados.rocks/console/checkin',
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
    def set_cookies(self, koa_sess, koa_sess_sig):
        """设置cookies"""
        # 直接设置cookie字符串，模拟浏览器行为
        cookie_string = f'koa:sess={koa_sess}; koa:sess.sig={koa_sess_sig}'
        self.session.headers.update({
            'Cookie': cookie_string
        })
        
        # 同时使用requests的cookie jar（备用）
        cookies = {
            'koa:sess': koa_sess,
            'koa:sess.sig': koa_sess_sig
        }
        self.session.cookies.update(cookies)
        
        print(f"设置cookies: koa:sess={koa_sess[:20]}...")
        print(f"设置cookies: koa:sess.sig={koa_sess_sig[:20]}...")
        
    def get_user_info(self):
        """获取用户信息"""
        try:
            url = 'https://glados.rocks/api/user/status'
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {})
                else:
                    print(f"获取用户信息失败: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"获取用户信息失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"获取用户信息异常: {str(e)}")
            return None
            
    def checkin(self):
        """执行签到"""
        try:
            url = 'https://glados.rocks/api/user/checkin'
            # 设置正确的Content-Type
            headers = {
                'Content-Type': 'application/json',
            }
            # 发送正确的payload
            payload = {"token": "glados.one"}
            
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"签到状态码: {response.status_code}")
            print(f"签到响应内容前200字符: {response.text[:200]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"签到JSON响应: {data}")
                    return data
                except ValueError as e:
                    print(f"签到JSON解析错误: {e}")
                    print(f"签到完整响应: {response.text}")
                    return {'code': -1, 'message': f'响应格式错误: {str(e)}'}
            else:
                print(f"签到HTTP错误: {response.status_code}")
                print(f"签到错误响应: {response.text}")
                return {'code': -1, 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"签到请求异常: {str(e)}")
            return {'code': -1, 'message': f'请求异常: {str(e)}'}
            
    def get_status(self):
        """获取账号状态"""
        try:
            url = 'https://glados.rocks/api/user/status'
            response = self.session.get(url, timeout=30)
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容前200字符: {response.text[:200]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON响应: {data}")
                    if data.get('code') == 0:
                        user_data = data.get('data', {})
                        return {
                            'email': user_data.get('email', 'Unknown'),
                            'days': user_data.get('leftDays', 'Unknown'),
                            'used': user_data.get('usedTraffic', 'Unknown'),
                            'total': user_data.get('totalTraffic', 'Unknown')
                        }
                    else:
                        print(f"API返回错误: {data.get('message', 'Unknown error')}")
                except ValueError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"完整响应内容: {response.text}")
            else:
                print(f"HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"获取状态异常: {str(e)}")
            return None


def send_notification(title, message, serverchan_key=None):
    """发送微信通知"""
    if not serverchan_key:
        return
        
    try:
        url = f'https://sctapi.ftqq.com/{serverchan_key}.send'
        data = {
            'title': title,
            'desp': message
        }
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                print("微信通知发送成功")
            else:
                print(f"微信通知发送失败: {result.get('message')}")
        else:
            print(f"微信通知发送失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"发送微信通知异常: {str(e)}")


def format_traffic(traffic_bytes):
    """格式化流量显示"""
    if not traffic_bytes or traffic_bytes == 'Unknown':
        return 'Unknown'
        
    try:
        traffic = float(traffic_bytes)
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while traffic >= 1024 and unit_index < len(units) - 1:
            traffic /= 1024
            unit_index += 1
            
        return f"{traffic:.2f} {units[unit_index]}"
    except:
        return str(traffic_bytes)


def main():
    # 获取环境变量
    cookies_env = os.getenv('COOKIES')
    serverchan_key = os.getenv('SERVERCHAN_KEY')
    
    if not cookies_env:
        print("错误：未设置 COOKIES 环境变量")
        return
        
    try:
        cookies_list = json.loads(cookies_env)
    except json.JSONDecodeError:
        print("错误：COOKIES 格式不正确，应为JSON格式")
        return
        
    results = []
    
    # 遍历所有账号
    for i, account in enumerate(cookies_list):
        print(f"\n{'='*50}")
        print(f"处理账号 {i+1}: {account.get('name', f'账号{i+1}')}")
        print(f"{'='*50}")
        
        glados = GLaDOSCheckin()
        
        # 设置cookies
        koa_sess = account.get('koa_sess')
        koa_sess_sig = account.get('koa_sess_sig')
        
        if not koa_sess or not koa_sess_sig:
            print("错误：cookies信息不完整")
            results.append({
                'name': account.get('name', f'账号{i+1}'),
                'status': '失败',
                'message': 'cookies信息不完整'
            })
            continue
            
        glados.set_cookies(koa_sess, koa_sess_sig)
        
        # 获取账号状态
        status = glados.get_status()
        if not status:
            print("错误：无法获取账号状态，可能cookies已过期")
            results.append({
                'name': account.get('name', f'账号{i+1}'),
                'status': '失败',
                'message': 'cookies可能已过期'
            })
            continue
            
        print(f"邮箱: {status['email']}")
        print(f"剩余天数: {status['days']}")
        print(f"已用流量: {format_traffic(status['used'])}")
        print(f"总流量: {format_traffic(status['total'])}")
        
        # 执行签到
        print("\n开始签到...")
        checkin_result = glados.checkin()
        
        if checkin_result.get('code') == 0:
            print("✅ 签到成功!")
            message = checkin_result.get('message', '签到成功')
            points = checkin_result.get('points', 0)
            if points > 0:
                message += f"，获得 {points} 积分"
            
            # 获取签到后的状态
            time.sleep(2)
            new_status = glados.get_status()
            if new_status:
                print(f"签到后剩余天数: {new_status['days']}")
                
            results.append({
                'name': account.get('name', f'账号{i+1}'),
                'email': status['email'],
                'status': '成功',
                'message': message,
                'days': new_status['days'] if new_status else status['days']
            })
            
        elif checkin_result.get('code') == 1 and 'repeat' in checkin_result.get('message', '').lower():
            print("ℹ️ 今日已签到!")
            message = checkin_result.get('message', '今日已签到')
            
            results.append({
                'name': account.get('name', f'账号{i+1}'),
                'email': status['email'],
                'status': '已签到',
                'message': message,
                'days': status['days']
            })
            
        else:
            error_msg = checkin_result.get('message', '未知错误')
            print(f"❌ 签到失败: {error_msg}")
            
            results.append({
                'name': account.get('name', f'账号{i+1}'),
                'email': status['email'],
                'status': '失败',
                'message': error_msg,
                'days': status['days']
            })
            
        time.sleep(3)  # 避免请求过于频繁
    
    # 生成总结报告
    print(f"\n{'='*50}")
    print("签到总结")
    print(f"{'='*50}")
    
    success_count = len([r for r in results if r['status'] == '成功'])
    total_count = len(results)
    
    print(f"总账号数: {total_count}")
    print(f"成功签到: {success_count}")
    print(f"失败签到: {total_count - success_count}")
    
    # 构建通知消息
    notification_title = f"GLaDOS签到报告 ({success_count}/{total_count})"
    notification_message = f"## 签到时间\n{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')} (北京时间)\n\n"
    notification_message += f"## 签到结果\n"
    notification_message += f"- 总账号数: {total_count}\n"
    notification_message += f"- 成功: {success_count}\n"
    notification_message += f"- 失败: {total_count - success_count}\n\n"
    
    notification_message += "## 详细信息\n"
    for result in results:
        status_icon = "✅" if result['status'] == '成功' else "❌"
        notification_message += f"{status_icon} **{result['name']}**\n"
        notification_message += f"   - 邮箱: {result.get('email', 'Unknown')}\n"
        notification_message += f"   - 状态: {result['status']}\n"
        notification_message += f"   - 剩余: {result.get('days', 'Unknown')} 天\n"
        notification_message += f"   - 信息: {result['message']}\n\n"
    
    # 发送微信通知
    if serverchan_key:
        send_notification(notification_title, notification_message, serverchan_key)
    
    print("\n任务完成!")


if __name__ == "__main__":
    main()
