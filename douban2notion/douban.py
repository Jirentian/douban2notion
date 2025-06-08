import argparse
import json
import os
import re
import pendulum
from retrying import retry
import requests

from douban2notion.notion_helper import NotionHelper
from douban2notion.config import (
    movie_properties_type_dict, 
    book_properties_type_dict,
    movie_status_mapping,
    book_status_mapping,
    rating_mapping,
    movie_type_mapping
)
from douban2notion.utils import get_properties, get_property_value, get_icon, extract_database_id, tz
from dotenv import load_dotenv

load_dotenv()

# 豆瓣API配置
DOUBAN_API_HOST = os.getenv("DOUBAN_API_HOST", "frodo.douban.com")
DOUBAN_API_KEY = os.getenv("DOUBAN_API_KEY", "0ac44ae016490db2204ce0a042db2916")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

headers = {
    "host": DOUBAN_API_HOST,
    "authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001023) NetType/WIFI Language/zh_CN",
    "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
}


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def fetch_subjects(user, type_, status):
    """从豆瓣获取用户的电影或书籍数据"""
    if not AUTH_TOKEN:
        print("警告: AUTH_TOKEN 未设置，可能会导致请求失败")
    
    offset = 0
    page = 0
    url = f"https://{DOUBAN_API_HOST}/api/v2/user/{user}/interests"
    total = 0
    results = []
    
    while True:
        params = {
            "type": type_,
            "count": 50,
            "status": status,
            "start": offset,
            "apiKey": DOUBAN_API_KEY,
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.ok:
            response_data = response.json()
            interests = response_data.get("interests", [])
            if len(interests) == 0:
                break
            results.extend(interests)
            page += 1
            offset = page * 50
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            print(f"请求URL: {url}")
            print(f"请求参数: {params}")
            print(f"请求头: {headers}")
            break
    
    if results:
        print(f"获取 {type_} ({status}) {len(results)} 条记录")
    
    return results


def sync_movies(douban_name, notion_helper):
    """同步电影数据到Notion"""
    print("开始同步电影数据...")
    
    # 验证数据库结构
    movie_db_name = notion_helper.get_database_name(notion_helper.movie_database_id)
    if movie_db_name != "影视":
        print(f"警告: 电影数据库名称为 '{movie_db_name}'，建议改为 '影视'")
    
    notion_helper.verify_database_structure(notion_helper.movie_database_id, movie_properties_type_dict)
    
    # 获取现有Notion数据
    notion_movies = notion_helper.query_all(database_id=notion_helper.movie_database_id)
    notion_movie_dict = {}
    
    for page in notion_movies:
        movie_data = {}
        for key, value in page.get("properties", {}).items():
            movie_data[key] = get_property_value(value)
        
        douban_link = movie_data.get("豆瓣链接")
        if douban_link:
            notion_movie_dict[douban_link] = {
                "data": movie_data,
                "page_id": page.get("id")
            }
    
    print(f"Notion中现有 {len(notion_movie_dict)} 部电影")
    
    # 获取豆瓣数据
    douban_movies = []
    for status in movie_status_mapping.keys():
        douban_movies.extend(fetch_subjects(douban_name, "movie", status))
    
    print(f"豆瓣中共有 {len(douban_movies)} 部电影")
    
    # 处理每部电影
    for result in douban_movies:
        if not result:
            continue
            
        subject = result.get("subject", {})
        movie = {}
        
        # 基本信息
        movie["名称"] = subject.get("title", "")
        movie["豆瓣链接"] = subject.get("url", "")
        movie["状态"] = movie_status_mapping.get(result.get("status"), "")
        
        # 看完日期
        create_time = result.get("create_time")
        if create_time:
            create_time = pendulum.parse(create_time, tz=tz)
            movie["看完日期"] = create_time.int_timestamp
        
        # 评分
        rating_data = result.get("rating")
        if rating_data:
            rating_value = rating_data.get("value")
            if rating_value and rating_value > 0:
                movie["豆瓣评分/自评"] = rating_mapping.get(rating_value, rating_value)
        
        # 导演
        if subject.get("directors"):
            directors = [d.get("name", "") for d in subject.get("directors", [])]
            movie["导演/演讲人"] = ", ".join(directors)
        
        # 分类
        if subject.get("genres"):
            movie["标签"] = subject.get("genres")
        
        # 类型
        subject_type = subject.get("type", "")
        movie["类型"] = movie_type_mapping.get(subject_type, subject_type)
        
        # 上映日期
        pubdates = subject.get("pubdate", [])
        if pubdates and len(pubdates) > 0:
            # 取第一个上映日期
            first_pubdate = pubdates[0]
            # 提取日期部分（去除地点信息）
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', first_pubdate)
            if date_match:
                movie["上映日期"] = date_match.group(1)
            else:
                # 如果只有年份，尝试提取年份
                year_match = re.search(r'(\d{4})', first_pubdate)
                if year_match:
                    movie["上映日期"] = f"{year_match.group(1)}-01-01"
                else:
                    movie["上映日期"] = ""
        else:
            # 尝试从year字段获取年份
            year = subject.get("year")
            if year:
                movie["上映日期"] = f"{year}-01-01"
            else:
                movie["上映日期"] = ""
        
        # 封面
        if subject.get("pic", {}).get("normal"):
            cover_url = subject.get("pic", {}).get("normal")
            if not cover_url.endswith('.webp'):
                cover_url = cover_url.rsplit('.', 1)[0] + '.webp'
            movie["封面"] = cover_url
        
        # 检查是否需要更新或创建
        douban_link = movie.get("豆瓣链接")
        if douban_link in notion_movie_dict:
            # 检查是否需要更新
            existing_data = notion_movie_dict[douban_link]["data"]
            needs_update = False
            
            for key, new_value in movie.items():
                existing_value = existing_data.get(key)
                if key == "看完日期":
                    # 对于日期类型，需要特殊处理
                    if isinstance(new_value, int) and existing_value:
                        existing_timestamp = pendulum.parse(existing_value, tz=tz).int_timestamp
                        if existing_timestamp != new_value:
                            needs_update = True
                            break
                elif existing_value != new_value:
                    needs_update = True
                    break
            
            if needs_update:
                print(f"更新电影: {movie['名称']}")
                properties = get_properties(movie, movie_properties_type_dict)
                notion_helper.update_page(
                    page_id=notion_movie_dict[douban_link]["page_id"],
                    properties=properties
                )
            else:
                print(f"跳过电影: {movie['名称']}")
        else:
            # 创建新记录
            print(f"添加电影: {movie['名称']}")
            properties = get_properties(movie, movie_properties_type_dict)
            parent = {
                "database_id": notion_helper.movie_database_id,
                "type": "database_id",
            }
            
            icon = None
            if movie.get("封面"):
                icon = get_icon(movie["封面"])
                
            notion_helper.create_page(
                parent=parent, 
                properties=properties, 
                icon=icon
            )


def sync_books(douban_name, notion_helper):
    """同步书籍数据到Notion"""
    print("开始同步书籍数据...")
    
    # 验证数据库结构
    book_db_name = notion_helper.get_database_name(notion_helper.book_database_id)
    if book_db_name != "书籍":
        print(f"警告: 书籍数据库名称为 '{book_db_name}'，建议改为 '书籍'")
    
    notion_helper.verify_database_structure(notion_helper.book_database_id, book_properties_type_dict)
    
    # 获取现有Notion数据
    notion_books = notion_helper.query_all(database_id=notion_helper.book_database_id)
    notion_book_dict = {}
    
    for page in notion_books:
        book_data = {}
        for key, value in page.get("properties", {}).items():
            book_data[key] = get_property_value(value)
        
        douban_link = book_data.get("豆瓣链接")
        if douban_link:
            notion_book_dict[douban_link] = {
                "data": book_data,
                "page_id": page.get("id")
            }
    
    print(f"Notion中现有 {len(notion_book_dict)} 本书籍")
    
    # 获取豆瓣数据
    douban_books = []
    for status in book_status_mapping.keys():
        douban_books.extend(fetch_subjects(douban_name, "book", status))
    
    print(f"豆瓣中共有 {len(douban_books)} 本书籍")
    
    # 处理每本书籍
    for result in douban_books:
        if not result:
            continue
            
        subject = result.get("subject", {})
        book = {}
        
        # 基本信息
        book["名称"] = subject.get("title", "")
        book["豆瓣链接"] = subject.get("url", "")
        book["状态"] = book_status_mapping.get(result.get("status"), "")
        
        # 添加日期
        create_time = result.get("create_time")
        if create_time:
            create_time = pendulum.parse(create_time, tz=tz)
            book["添加日期"] = create_time.int_timestamp
        
        # 评分
        rating_data = result.get("rating")
        if rating_data:
            rating_value = rating_data.get("value")
            if rating_value and rating_value > 0:
                book["豆瓣评分"] = rating_mapping.get(rating_value, rating_value)
        
        # 作者
        if subject.get("author"):
            authors = [a for a in subject.get("author", [])]
            book["书籍作者"] = ", ".join(authors)
        
        # 简介
        intro_text = subject.get("intro", "")
        if len(intro_text) > 2000:
            book["书籍简介"] = intro_text[:1997] + "..."
        else:
            book["书籍简介"] = intro_text
        
        # 封面
        if subject.get("pic", {}).get("large"):
            book["书籍封面"] = subject.get("pic", {}).get("large")
        
        # 检查是否需要更新或创建
        douban_link = book.get("豆瓣链接")
        if douban_link in notion_book_dict:
            # 检查是否需要更新
            existing_data = notion_book_dict[douban_link]["data"]
            needs_update = False
            
            for key, new_value in book.items():
                existing_value = existing_data.get(key)
                if key == "添加日期":
                    # 对于日期类型，需要特殊处理
                    if isinstance(new_value, int) and existing_value:
                        existing_timestamp = pendulum.parse(existing_value, tz=tz).int_timestamp
                        if existing_timestamp != new_value:
                            needs_update = True
                            break
                elif existing_value != new_value:
                    needs_update = True
                    break
            
            if needs_update:
                print(f"更新书籍: {book['名称']}")
                properties = get_properties(book, book_properties_type_dict)
                notion_helper.update_page(
                    page_id=notion_book_dict[douban_link]["page_id"],
                    properties=properties
                )
            else:
                print(f"跳过书籍: {book['名称']}")
        else:
            # 创建新记录
            print(f"添加书籍: {book['名称']}")
            properties = get_properties(book, book_properties_type_dict)
            parent = {
                "database_id": notion_helper.book_database_id,
                "type": "database_id",
            }
            
            icon = None
            if book.get("书籍封面"):
                icon = get_icon(book["书籍封面"])
                
            notion_helper.create_page(
                parent=parent, 
                properties=properties, 
                icon=icon
            )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="同步豆瓣数据到Notion")
    parser.add_argument("--movie-db", required=True, help="电影数据库URL或ID")
    parser.add_argument("--book-db", required=True, help="书籍数据库URL或ID")
    parser.add_argument("--douban-user", help="豆瓣用户名（默认从环境变量DOUBAN_NAME获取）")
    parser.add_argument("--type", choices=["movie", "book", "both"], default="both", help="同步类型")
    
    args = parser.parse_args()
    
    # 提取数据库ID
    try:
        movie_db_id = extract_database_id(args.movie_db)
        book_db_id = extract_database_id(args.book_db)
    except Exception as e:
        print(f"错误: {e}")
        return
    
    # 获取豆瓣用户名
    douban_user = args.douban_user or os.getenv("DOUBAN_NAME")
    if not douban_user:
        print("错误: 请提供豆瓣用户名（通过 --douban-user 参数或 DOUBAN_NAME 环境变量）")
        return
    
    # 初始化NotionHelper
    try:
        notion_helper = NotionHelper(movie_db_id, book_db_id)
    except Exception as e:
        print(f"初始化Notion连接失败: {e}")
        return
    
    print(f"开始同步豆瓣用户 '{douban_user}' 的数据...")
    
    # 执行同步
    if args.type in ["movie", "both"]:
        try:
            sync_movies(douban_user, notion_helper)
            print("电影数据同步完成!")
        except Exception as e:
            print(f"电影数据同步失败: {e}")
    
    if args.type in ["book", "both"]:
        try:
            sync_books(douban_user, notion_helper)
            print("书籍数据同步完成!")
        except Exception as e:
            print(f"书籍数据同步失败: {e}")
    
    print("数据同步完成!")


if __name__ == "__main__":
    main()