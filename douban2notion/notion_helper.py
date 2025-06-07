import logging
import os
import re

from notion_client import Client
from retrying import retry

from douban2notion.utils import get_icon, get_title


class NotionHelper:
    def __init__(self, movie_database_id, book_database_id):
        """
        初始化NotionHelper
        
        Args:
            movie_database_id: 电影数据库ID
            book_database_id: 书籍数据库ID
        """
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise Exception("请设置NOTION_TOKEN环境变量")
            
        self.client = Client(auth=notion_token, log_level=logging.ERROR)
        self.movie_database_id = movie_database_id
        self.book_database_id = book_database_id
        self.__cache = {}

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def create_page(self, parent, properties, icon=None):
        """创建页面"""
        return self.client.pages.create(
            parent=parent, properties=properties, icon=icon
        )

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def update_page(self, page_id, properties):
        """更新页面"""
        return self.client.pages.update(page_id=page_id, properties=properties)

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def query_all(self, database_id):
        """查询数据库所有数据"""
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = self.client.databases.query(
                database_id=database_id,
                start_cursor=start_cursor,
                page_size=100
            )
            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
            
        return results

    def verify_database_structure(self, database_id, expected_properties):
        """验证数据库结构是否符合要求"""
        try:
            database = self.client.databases.retrieve(database_id=database_id)
            database_properties = database.get("properties", {})
            
            missing_properties = []
            for prop_name, prop_type in expected_properties.items():
                if prop_name not in database_properties:
                    missing_properties.append(prop_name)
                else:
                    actual_type = database_properties[prop_name].get("type")
                    if actual_type != prop_type:
                        print(f"警告: 属性 '{prop_name}' 类型不匹配，期望: {prop_type}, 实际: {actual_type}")
            
            if missing_properties:
                raise Exception(f"数据库缺少必需的属性: {', '.join(missing_properties)}")
                
            return True
            
        except Exception as e:
            raise Exception(f"验证数据库结构时出错: {str(e)}")

    def get_database_name(self, database_id):
        """获取数据库名称"""
        try:
            database = self.client.databases.retrieve(database_id=database_id)
            title_list = database.get("title", [])
            if title_list:
                return title_list[0].get("text", {}).get("content", "")
            return ""
        except Exception as e:
            print(f"获取数据库名称失败: {str(e)}")
            return ""
