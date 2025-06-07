# 豆瓣数据同步到Notion

这个项目专门用于从豆瓣获取电影和书籍数据，并导入到指定的Notion数据库中。

## 功能特点

- 🎬 支持豆瓣电影数据同步到Notion"影视"数据库
- 📚 支持豆瓣书籍数据同步到Notion"书籍"数据库
- 🔄 智能增量同步，避免重复数据
- ⚡ 自动验证数据库结构
- 🎨 自动设置封面图标

## 数据库结构要求

### 电影数据库（必须命名为"影视"）

需要包含以下属性：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 名称 | 标题类型 | 电影标题 |
| 导演/演讲人 | 文本类型 | 导演姓名 |
| 标签 | 多选类型 | 电影分类/类型 |
| 豆瓣评分/自评 | 数字类型 | 豆瓣评分（1-10） |
| 封面 | 文件类型 | 电影海报 |
| 状态 | 状态类型 | **必须包含选项：计划看、正在看、已看完** |
| 类型 | 选择类型 | 影视类型（电影/电视剧） |
| 上映日期 | 日期类型 | 最早时间的上映日期（只读取并导入第一个上映日期） |
| 看完日期 | 日期类型 | 观看完成日期 |
| 豆瓣链接 | 链接类型 | 豆瓣页面链接 |

### 书籍数据库（必须命名为"书籍"）

需要包含以下属性：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 名称 | 标题类型 | 书籍标题 |
| 书籍作者 | 文本类型 | 作者姓名 |
| 豆瓣评分 | 数字类型 | 豆瓣评分（1-10） |
| 书籍封面 | 文件类型 | 书籍封面图 |
| 状态 | 状态类型 | **必须包含选项：计划阅读、正在阅读、已经读完** |
| 读完日期 | 日期类型 | 阅读完成日期 |
| 书籍简介 | 文本类型 | 书籍简介 |
| 豆瓣链接 | 链接类型 | 豆瓣页面链接 |

### ⚠️ 重要配置说明

#### 状态属性配置

**电影数据库的"状态"属性必须包含以下三个选项：**
- `计划看`
- `正在看`
- `已看完`

**书籍数据库的"状态"属性必须包含以下三个选项：**
- `计划阅读`
- `正在阅读`
- `已经读完`

**配置步骤：**
1. 点击状态列的下拉箭头
2. 选择"编辑属性" 
3. 在状态选项中添加上述对应选项
4. 保存设置

#### 类型属性配置

**电影数据库的"类型"属性应包含以下选项：**
- `电影`
- `电视剧`

**配置步骤：**
1. 点击类型列的下拉箭头
2. 选择"编辑属性"
3. 添加上述选项
4. 保存设置

## 使用GitHub Actions自动同步（推荐）

项目已配置GitHub Actions工作流，可以实现自动定时同步，无需本地运行。

### 🔧 GitHub Actions配置步骤

#### 1. Fork或Clone项目到你的GitHub仓库

#### 2. 设置GitHub Repository Secrets

在你的GitHub仓库中设置以下机密变量：

1. 进入你的GitHub仓库页面
2. 点击 `Settings` 选项卡
3. 在左侧菜单中点击 `Secrets and variables` → `Actions`
4. 点击 `New repository secret` 添加以下机密：

| 机密名称 | 说明 | 必需 |
|---------|------|------|
| `NOTION_TOKEN` | Notion集成令牌 | ✅ |
| `DOUBAN_NAME` | 豆瓣用户名 | ✅ |
| `MOVIE_DATABASE_ID` | 电影数据库ID | ✅ |
| `BOOK_DATABASE_ID` | 书籍数据库ID | ✅ |
| `AUTH_TOKEN` | 豆瓣认证令牌（可选） | ❌ |

#### 3. 获取所需的机密值

**Notion Token 获取：**
- 访问 [Notion Developers](https://www.notion.so/my-integrations)
- 创建新的集成
- 复制 `Internal Integration Token`
- 在数据库页面中添加集成权限

**数据库ID 获取：**
```
数据库URL: https://www.notion.so/workspace/123abc456def?v=789ghi
数据库ID: 
复制文本：207503e0 1234 5678 9101 dcbd03fd7abf
修改格式：207503e0-1234-5678-9101-dcbd03fd7abf
```

**豆瓣用户名：**
- 你的豆瓣个人主页用户名，如：`https://www.douban.com/people/username/` 中的 `username`

**AUTH_TOKEN（可选）：**
- 通过浏览器开发者工具抓包获取
- 可提高豆瓣API访问成功率

#### 4. 启用GitHub Actions

1. 进入仓库的 `Actions` 选项卡
2. 如果是第一次使用，需要启用Actions
3. 找到 `豆瓣数据同步到Notion` 工作流

#### 5. 运行方式

**自动运行：**
- 每天北京时间0点自动执行
- 默认同步电影和书籍数据

**手动运行：**
1. 进入 `Actions` 选项卡
2. 选择 `豆瓣数据同步到Notion` 工作流
3. 点击 `Run workflow`
4. 选择同步类型（both/movie/book）
5. 点击 `Run workflow` 确认

### 📋 GitHub Actions优势

- 🕐 **定时自动同步**：每天自动更新，无需手动操作
- 🔒 **安全性**：敏感信息存储在GitHub Secrets中
- 📊 **执行日志**：可查看每次同步的详细日志
- 🎯 **灵活控制**：支持手动触发和选择同步类型
- 💰 **免费使用**：GitHub Actions对公共仓库免费

## 本地手动使用

如果你prefer本地运行，也可以按以下方式配置：

### 环境配置

1. 创建 `.env` 文件：

```bash
# 复制环境变量模板文件
cp .env.example .env

# 或手动创建 .env 文件，内容如下：
# Notion配置
NOTION_TOKEN=your_notion_token

# 豆瓣配置
DOUBAN_NAME=your_douban_username
AUTH_TOKEN=your_douban_auth_token

# 可选配置
DOUBAN_API_HOST=frodo.douban.com
DOUBAN_API_KEY=0ac44ae016490db2204ce0a042db2916
```

2. 获取Notion Token：
   - 访问 [Notion Developers](https://www.notion.so/my-integrations)
   - 创建新的集成
   - 复制Internal Integration Token
   - 在数据库页面中添加集成权限

3. 获取豆瓣认证信息：
   - 豆瓣用户名：你的豆瓣个人主页用户名
   - AUTH_TOKEN：需要通过抓包获取（可选，用于提高访问成功率）

### 安装和使用

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行同步：

```bash
# 同步电影和书籍（需要提供两个数据库的URL或ID）
python -m douban2notion --movie-db "你的电影数据库URL" --book-db "你的书籍数据库URL"

# 只同步电影
python -m douban2notion --movie-db "你的电影数据库URL" --book-db "你的书籍数据库URL" --type movie

# 只同步书籍  
python -m douban2notion --movie-db "你的电影数据库URL" --book-db "你的书籍数据库URL" --type book

# 指定豆瓣用户名
python -m douban2notion --movie-db "你的电影数据库URL" --book-db "你的书籍数据库URL" --douban-user "豆瓣用户名"
```

## 参数说明

- `--movie-db`：电影数据库的Notion URL或数据库ID（必需）
- `--book-db`：书籍数据库的Notion URL或数据库ID（必需）
- `--douban-user`：豆瓣用户名（可选，默认从环境变量DOUBAN_NAME获取）
- `--type`：同步类型，可选值：movie、book、both（默认both）

## 数据库URL示例

Notion数据库URL通常格式为：
```
https://www.notion.so/workspace/database_id?v=view_id
```

程序会自动从URL中提取数据库ID。

## 注意事项

1. **数据库命名**：电影数据库必须命名为"影视"，书籍数据库必须命名为"书籍"
2. **属性类型**：必须严格按照要求设置数据库属性类型
3. **权限设置**：确保Notion集成有访问数据库的权限
4. **增量同步**：程序会智能识别已存在的数据，避免重复导入
5. **评分转换**：豆瓣5星评分会转换为10分制

## 常见问题

**Q: 数据库结构验证失败怎么办？**
A: 请检查数据库的属性名称和类型是否与要求完全一致。

**Q: 获取豆瓣数据失败？**
A: 请确认豆瓣用户名正确，并尝试配置AUTH_TOKEN。

**Q: 封面图片无法显示？**
A: 豆瓣图片可能有防盗链，这是正常现象。

## 开发

如果需要修改或扩展功能，主要文件说明：

- `douban2notion/douban.py`：豆瓣数据获取和同步逻辑
- `douban2notion/notion_helper.py`：Notion API封装
- `douban2notion/config.py`：配置文件，包含数据库结构定义
- `douban2notion/utils.py`：工具函数

## 许可证

MIT License