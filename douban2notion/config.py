RICH_TEXT = "rich_text"
URL = "url"
RELATION = "relation"
NUMBER = "number"
DATE = "date"
FILES = "files"
STATUS = "status"
TITLE = "title"
SELECT = "select"
MULTI_SELECT = "multi_select"

# 电影数据库属性配置（数据库名必须为"影视"）
movie_properties_type_dict = {
    "名称": TITLE,
    "导演/演讲人": RICH_TEXT,
    "标签": MULTI_SELECT,
    "豆瓣评分/自评": NUMBER,
    "封面": FILES,
    "状态": STATUS,
    "类型": SELECT,
    "上映日期": DATE,
    "看完日期": DATE,
    "豆瓣链接": URL,
}

# 图书数据库属性配置（数据库名必须为"书籍"）
book_properties_type_dict = {
    "名称": TITLE,
    "书籍作者": RICH_TEXT,
    "豆瓣评分": NUMBER,
    "书籍封面": FILES,
    "状态": STATUS,
    "添加日期": DATE,
    "书籍简介": RICH_TEXT,
    "豆瓣链接": URL,
}

# 状态映射
movie_status_mapping = {
    "mark": "计划看",
    "doing": "正在看",
    "done": "已看完",
}

book_status_mapping = {
    "mark": "计划阅读",
    "doing": "正在阅读",
    "done": "已经读完",
}

# 评分映射
rating_mapping = {
    1: 2,
    2: 4,
    3: 6,
    4: 8,
    5: 10,
}

# 电影类型映射
movie_type_mapping = {
    "movie": "电影",
    "tv": "电视剧",
}

TAG_ICON_URL = "https://www.notion.so/icons/tag_gray.svg"
USER_ICON_URL = "https://www.notion.so/icons/user-circle-filled_gray.svg"
BOOK_ICON_URL = "https://www.notion.so/icons/book_gray.svg"
