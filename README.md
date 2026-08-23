# 纹承堂 · 中国传统纹样数字图书馆

一个基于 **Django + Django REST Framework** 的中国传统纹样数字化展示与检索平台。以「让传统纹样被看见、被检索、被使用」为目标，将散落的传统纹样进行结构化整理，提供分类浏览、朝代时间线、关键词搜索、设计素材与社区问答五大功能，是一个完整的全栈 Web 项目。

## ✨ 核心功能（5 大模块）

| 模块 | 功能 |
|---|---|
| 🏷️ 纹样分类 | 按纹样类型（动物 / 植物 / 几何 / 文字等）结构化浏览 |
| 📅 朝代时间线 | 按历史朝代脉络展示纹样演变 |
| 🔍 关键词搜索 | 关键词检索 + 多维组合过滤，快速定位目标纹样 |
| 🎨 设计素材 | 高清 / 缩略图两级图片库，供设计取用 |
| 💬 社区问答 | 用户注册登录后参与讨论交流 |

## 🛠 技术栈

- **后端**：Django + Django REST Framework（DRF）
- **数据库**：MySQL
- **前端**：Django 模板渲染 + AJAX + 静态资源管理
- **多应用架构**：`patterns` / `accounts` / `design` / `search` / `community` 五个 app 解耦

## 🎯 技术亮点

1. **多应用拆分** —— 5 个 Django app 按业务域解耦，体现后端工程化组织能力
2. **自定义用户认证** —— 自定义认证后端（邮箱 / 用户名登录）+ 验证码注册登录
3. **RESTful API** —— DRF 序列化器 + 分页过滤，接口规范清晰
4. **多维度检索** —— 关键词搜索 + 纹样分类 + 朝代时间线组合查询

## 🚀 快速开始

### 环境要求

- Python 3.x
- MySQL 8.x
- Django 及依赖（见 `requirements.txt`，如缺失请 `pip install django djangorestframework mysqlclient`）

### 启动步骤

```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE chinese_pattern_library CHARACTER SET utf8mb4;"

# 2. 配置数据库连接（settings.py 中 DATABASES）
# 3. 执行迁移
python manage.py migrate

# 4. 创建管理员
python manage.py createsuperuser

# 5. 启动开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000 查看首页。

## 📸 界面预览

<!-- 在此插入首页、纹样分类、朝代时间线、纹样详情等界面截图 -->
*（截图见本仓库 `docs/screenshots/` 目录）*

## 📁 项目结构

```
chinese_pattern_library/
├── accounts/      # 用户认证（自定义后端 + 验证码注册登录）
├── patterns/      # 纹样数据与分类
├── design/        # 设计素材
├── search/        # 关键词搜索
├── community/     # 社区问答
├── templates/     # 页面模板（index / pattern-detail / dynasty-time 等）
├── media/         # 纹样图片库（高清 / 缩略图两级）
└── static/        # 静态资源
```
