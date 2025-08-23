#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地测试脚本 - 用于在本地环境测试签到功能
使用方法: python test_local.py
"""

import json
import os
from checkin import GLaDOSCheckin, format_traffic


def test_checkin():
    """本地测试签到功能"""
    
    # 从文件读取cookies配置
    config_file = 'cookies.json'
    if not os.path.exists(config_file):
        print(f"错误：配置文件 {config_file} 不存在")
        print("请创建配置文件，参考 cookies.example.json")
        return
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            cookies_list = json.load(f)
    except json.JSONDecodeError:
        print("错误：配置文件格式不正确")
        return
    except Exception as e:
        print(f"错误：读取配置文件失败 - {e}")
        return
    
    print("🚀 开始本地测试...")
    print(f"📋 共找到 {len(cookies_list)} 个账号\n")
    
    for i, account in enumerate(cookies_list):
        print(f"{'='*60}")
        print(f"🔍 测试账号 {i+1}: {account.get('name', f'账号{i+1}')}")
        print(f"{'='*60}")
        
        glados = GLaDOSCheckin()
        
        # 检查cookies信息
        koa_sess = account.get('koa_sess')
        koa_sess_sig = account.get('koa_sess_sig')
        
        if not koa_sess or not koa_sess_sig:
            print("❌ cookies信息不完整")
            continue
            
        glados.set_cookies(koa_sess, koa_sess_sig)
        
        # 获取用户状态
        print("📊 获取账号状态...")
        status = glados.get_status()
        
        if not status:
            print("❌ 无法获取账号状态，cookies可能已过期")
            continue
            
        print(f"📧 邮箱: {status['email']}")
        print(f"📅 剩余天数: {status['days']}")
        print(f"📈 已用流量: {format_traffic(status['used'])}")
        print(f"📦 总流量: {format_traffic(status['total'])}")
        
        # 询问是否执行签到
        user_input = input("\n🤔 是否执行签到？(y/N): ").strip().lower()
        
        if user_input in ['y', 'yes']:
            print("\n🎯 开始签到...")
            result = glados.checkin()
            
            if result.get('code') == 0:
                points = result.get('points', 0)
                message = result.get('message', '签到成功')
                if points > 0:
                    message += f"，获得 {points} 积分"
                print(f"✅ 签到成功: {message}")
                
                # 获取签到后的状态
                import time
                time.sleep(2)
                new_status = glados.get_status()
                if new_status:
                    print(f"📅 签到后剩余天数: {new_status['days']}")
                    
            elif result.get('code') == 1 and 'repeat' in result.get('message', '').lower():
                print(f"ℹ️ 今日已签到: {result.get('message', '今日已签到')}")
                
            else:
                print(f"❌ 签到失败: {result.get('message', '未知错误')}")
        else:
            print("⏭️  跳过签到")
            
        print()
    
    print("🎉 本地测试完成!")


if __name__ == "__main__":
    test_checkin()
