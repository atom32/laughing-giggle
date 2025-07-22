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

## ⚙️ 配置管理

应用使用基于 INI 文件的配置系统，支持环境特定的配置覆盖和自动默认配置生成。

### 配置文件结构

- **默认配置文件**：`config/settings.ini`
- **自动创建**：如果配置文件不存在，系统会自动创建包含默认值的配置文件
- **环境覆盖**：支持 development、production、testing 环境特定配置

### 配置选项说明

#### 基础应用配置
- `secret_key` - Flask 应用密钥（生产环境必须修改）
- `database_uri` - 数据库连接字符串
- `debug` - 调试模式开关
- `host` - 服务器监听地址
- `port` - 服务器监听端口

#### 游戏平衡配置
- `starting_coins` - 新用户初始金币数量
- `starting_wheat/corn/carrots` - 新用户初始作物种子数量
- `starting_farm_size` - 新用户初始农场地块数量
- `max_level` - 游戏最大等级限制
- `experience_per_level` - 每级升级所需经验值

#### 国际化配置
- `default_language` - 默认界面语言（en/es/fr）
- `available_languages` - 支持的语言列表（逗号分隔）

### 示例配置文件

```ini
[DEFAULT]
# 安全配置
secret_key = your-secret-key-here
database_uri = sqlite:///instance/farm.db

# 服务器配置
debug = false
host = 127.0.0.1
port = 5000

# 游戏初始资源
starting_coins = 100
starting_wheat = 10
starting_corn = 5
starting_carrots = 3
starting_farm_size = 6

# 游戏平衡
max_level = 100
experience_per_level = 1000

# 国际化
default_language = en
available_languages = en,es,fr

[development]
debug = true
database_uri = sqlite:///instance/farm_dev.db

[production]
debug = false
secret_key = CHANGE-THIS-IN-PRODUCTION
database_uri = sqlite:///instance/farm_prod.db

[testing]
database_uri = sqlite:///:memory:
starting_coins = 10000
```

### 环境配置

通过环境变量或启动参数指定运行环境：

```bash
# 开发环境（默认）
python app.py

# 生产环境
FLASK_ENV=production python app.py

# 测试环境
FLASK_ENV=testing python app.py

# 使用自定义配置文件
python -c "from app import create_app; app = create_app(config_file='custom.ini'); app.run()"
```

### 安全注意事项

1. **生产环境密钥**：必须修改 `secret_key` 为随机强密码
2. **数据库安全**：生产环境建议使用 PostgreSQL 等专业数据库
3. **配置文件权限**：确保配置文件不被未授权访问
4. **环境变量**：敏感配置可通过环境变量覆盖

## 🌐 多语言支持

应用内置完整的国际化（i18n）系统，支持多语言界面和用户语言偏好管理。

### 支持的语言

- **English (en)** - 英语（默认）
- **Español (es)** - 西班牙语
- **Français (fr)** - 法语

### 语言检测优先级

1. URL 参数 `?lang=<language_code>`
2. 用户数据库中保存的语言偏好
3. 会话中存储的语言偏好
4. 浏览器 Accept-Language 头部
5. 系统默认语言

### 语言切换方式

#### 用户界面切换
- 点击页面右上角的语言选择器
- 登录用户的选择会保存到数据库
- 访客用户的选择保存到会话中

#### 程序化切换
```bash
# 直接访问语言切换端点
curl http://localhost:5000/set_language/es

# 在用户资料页面更新
POST /profile
Content-Type: application/x-www-form-urlencoded
language=fr
```

### 翻译文件管理

#### 提取可翻译字符串
```bash
python -m babel.messages.frontend extract -F babel.cfg -k _l -o messages.pot .
```

#### 初始化新语言翻译
```bash
python -m babel.messages.frontend init -i messages.pot -d translations -l <language_code>
```

#### 更新现有翻译
```bash
python -m babel.messages.frontend update -i messages.pot -d translations
```

#### 编译翻译文件
```bash
python -m babel.messages.frontend compile -d translations
```

### 翻译文件结构

```
translations/
├── es/
│   └── LC_MESSAGES/
│       ├── messages.po  # 西班牙语翻译源文件
│       └── messages.mo  # 编译后的二进制文件
├── fr/
│   └── LC_MESSAGES/
│       ├── messages.po  # 法语翻译源文件
│       └── messages.mo  # 编译后的二进制文件
└── messages.pot         # 翻译模板文件
```

### 添加新语言支持

1. 在 `config/i18n.py` 中添加语言到 `SUPPORTED_LANGUAGES`
2. 初始化翻译文件：`python -m babel.messages.frontend init -i messages.pot -d translations -l <new_lang>`
3. 翻译 `translations/<new_lang>/LC_MESSAGES/messages.po` 文件
4. 编译翻译：`python -m babel.messages.frontend compile -d translations`
5. 更新配置文件中的 `available_languages` 列表

## 🧪 测试系统

项目包含完整的测试套件，覆盖配置管理、国际化功能和集成测试。

### 运行测试

```bash
# 运行所有测试
python -m unittest discover

# 运行特定测试模块
python -m unittest test_config.py      # 配置管理测试
python -m unittest test_i18n.py        # 国际化功能测试
python -m unittest test_integration.py # 集成测试

# 单独运行测试文件
python test_config.py
python test_i18n.py
python test_integration.py
```

### 测试覆盖范围

#### 配置管理测试 (`test_config.py`)
- INI 文件加载和解析
- 环境检测和配置覆盖
- 默认值回退机制
- 配置验证和错误处理
- 数据类型转换

#### 国际化测试 (`test_i18n.py`)
- 语言检测和偏好处理
- 翻译加载和回退机制
- 语言切换和会话管理
- 浏览器语言检测
- 翻译文件状态检查

#### 集成测试 (`test_integration.py`)
- 端到端语言切换流程
- 用户注册和登录语言偏好
- 模板渲染多语言支持
- 配置系统集成测试

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

