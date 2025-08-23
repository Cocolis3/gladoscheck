# 配置说明

## 1. Cookies 获取方法

### 方法一：浏览器开发者工具
1. 打开浏览器，访问 https://glados.network/console
2. 登录你的账号
3. 按 F12 打开开发者工具
4. 切换到 "Network"（网络）标签页
5. 刷新页面或点击任意按钮
6. 在请求列表中选择任意一个请求
7. 在右侧的 "Headers"（请求头）中找到 "Cookie" 字段
8. 复制其中的 `koa:sess` 和 `koa:sess.sig` 的值

### 方法二：浏览器控制台
1. 登录 GLaDOS 后，按 F12 打开开发者工具
2. 切换到 "Console"（控制台）标签页
3. 输入以下代码并回车：
```javascript
document.cookie.split(';').filter(c => c.includes('koa:sess'))
```
4. 从输出结果中提取 `koa:sess` 和 `koa:sess.sig` 的值

## 2. GitHub Secrets 配置

在 GitHub 仓库中设置以下 Secrets：

### COOKIES（必需）
格式为 JSON 字符串，支持多账号：
```json
[
  {
    "name": "主账号",
    "koa_sess": "你的koa:sess值",
    "koa_sess_sig": "你的koa:sess.sig值"
  },
  {
    "name": "副账号",
    "koa_sess": "另一个koa:sess值", 
    "koa_sess_sig": "另一个koa:sess.sig值"
  }
]
```

### SERVERCHAN_KEY（可选）
用于微信推送通知的 Server酱 Key。

获取方法：
1. 访问 https://sct.ftqq.com/
2. 微信扫码登录
3. 点击"发送消息"，获取 SendKey
4. 将 SendKey 设置为 SERVERCHAN_KEY 的值

## 3. 本地测试

### 安装依赖
```bash
pip install -r requirements.txt
```

### 创建本地配置
复制 `cookies.example.json` 为 `cookies.json`，并填入你的真实 cookies 信息：
```bash
cp cookies.example.json cookies.json
```

### 运行测试
```bash
python test_local.py
```

## 4. 运行时间配置

默认每天北京时间 9:00 AM 运行。如需修改，编辑 `.github/workflows/checkin.yml` 文件中的 cron 表达式：

```yaml
schedule:
  # 0 1 * * * 表示每天 UTC 1:00（北京时间 9:00）
  - cron: '0 1 * * *'
```

常用时间对照：
- 北京时间 8:00  → UTC 0:00  → `'0 0 * * *'`
- 北京时间 9:00  → UTC 1:00  → `'0 1 * * *'`
- 北京时间 10:00 → UTC 2:00  → `'0 2 * * *'`
- 北京时间 12:00 → UTC 4:00  → `'0 4 * * *'`
- 北京时间 20:00 → UTC 12:00 → `'0 12 * * *'`

## 5. 常见问题

### Q: 签到失败，提示 cookies 过期
A: 重新获取 cookies 并更新 GitHub Secrets 中的 COOKIES 配置

### Q: 微信通知没有收到
A: 检查 SERVERCHAN_KEY 是否正确配置，并确保 Server酱 服务正常

### Q: GitHub Actions 没有自动运行
A: 检查是否启用了 Actions，并确保仓库不是 fork 的私有仓库

### Q: 如何查看运行日志
A: 在 GitHub 仓库的 Actions 页面可以查看详细的运行日志

## 6. 安全提醒

- 不要在公开场所分享你的 cookies 信息
- 定期更新 cookies（建议每月更新一次）
- 如果发现异常登录，立即修改密码并重新获取 cookies
