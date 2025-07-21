# Frontier Eden

一个基于 Flask 的种田类网页策略游戏，灵感源自经典的《OGame》，主打慢节奏资源建设、科技发展与多语言支持的玩法体验。

repo名字是GitHub建议下随手起的，以后会改掉。

## 🎮 游戏简介

> 你将作为一名星际拓荒者，从一个小型殖民地开始，不断发展你的资源系统、研究科技、扩展人口，并最终建成一个高效运转的太空农业文明。

与传统 OGame 的战斗与掠夺不同，**laughing-giggle 更注重“种田”式的内政建设**，适合偏好长期经营、资源调度、策略布局的玩家。

## 🧩 核心玩法特色

- 🌍 **资源系统**：矿物、能量、水源、人口，生产与消费动态变化
- 🧪 **科技树**：解锁更高级的建筑与单位，提高资源效率
- 🏗️ **建筑建设**：多种可升级建筑，每种都有独特作用
- 🌐 **多语言支持**：内置 Flask-Babel 国际化系统
- 🧠 **慢节奏发展**：无需频繁上线操作，适合挂机式玩法

## 🛠️ 技术架构

| 模块         | 技术                     |
|--------------|--------------------------|
| 后端框架     | Flask                    |
| 国际化       | Flask-Babel              |
| 数据库       | SQLite（可拓展为 PostgreSQL）|
| 前端模板     | Jinja2 + HTML/CSS        |
| 单元测试     | pytest                   |

## 🗂️ 目录结构

```

laughing-giggle/
├── app.py                          # 应用入口
├── routes.py                       # 游戏路由与视图逻辑
├── models.py                       # 游戏数据模型（用户、资源、建筑）
├── utils.py                        # 工具函数（资源更新、时间调度等）
├── babel.cfg                       # 国际化配置
├── migrate\_add\_language\_preference.py  # 添加语言偏好字段
├── templates/                      # 前端 HTML 模板
├── static/                         # 静态文件（CSS/JS）
├── instance/                       # SQLite 数据文件或本地配置
├── test\_routes.py                  # 测试游戏路由
├── test\_language\_preference.py     # 测试语言偏好逻辑
└── requirements.txt               # Python 依赖包

````

## 🚀 快速开始

### 环境依赖

- Python 3.9+
- Flask
- Flask-Babel

### 安装步骤

```bash
git clone https://github.com/atom32/laughing-giggle.git
cd laughing-giggle
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
````

### 初始化数据库

```bash
python migrate_add_language_preference.py
```

或在 `app.py` 中加入自动创建逻辑。

### 启动开发服务器

```bash
python app.py
```

浏览器访问：`http://localhost:5000`

### 切换语言

支持多语言 UI（中文 / English），点击界面右上角语言切换即可保存用户偏好。

### 运行测试

```bash
pytest
```

## 📌 后续开发方向

* 🌎 多殖民地支持（多个星球）
* ⏱ 资源产量调度优化为计划任务（APScheduler 或 Celery）
* 📱 移动端适配
* 🔐 用户登录系统、排行榜系统
* 📊 游戏状态可视化（图表展示资源产量等）

## 🤝 参与贡献

欢迎提交 PR 或 Issue：

* 添加新的建筑种类 / 科技树节点
* 丰富前端交互体验
* 优化国际化翻译
* 编写更多测试用例

## 📄 许可证

MIT License

