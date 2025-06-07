import os
import re
import pendulum

# 时区设置
tz = "Asia/Shanghai"


def get_property_value(property_item):
    """从Notion属性中提取值"""
    property_type = property_item.get("type")
    property_value = property_item.get(property_type)
    
    if property_type == "title":
        if property_value and len(property_value) > 0:
            return property_value[0].get("text", {}).get("content", "")
    elif property_type == "rich_text":
        if property_value and len(property_value) > 0:
            return property_value[0].get("text", {}).get("content", "")
    elif property_type == "url":
        return property_value
    elif property_type == "select":
        if property_value:
            return property_value.get("name", "")
    elif property_type == "multi_select":
        if property_value:
            return [item.get("name", "") for item in property_value]
    elif property_type == "status":
        if property_value:
            return property_value.get("name", "")
    elif property_type == "date":
        if property_value:
            return property_value.get("start")
    elif property_type == "number":
        return property_value
    elif property_type == "files":
        if property_value and len(property_value) > 0:
            return property_value[0].get("external", {}).get("url", "")
    
    return ""


def get_title(text):
    """创建标题属性"""
    return {
        "title": [
            {
                "type": "text",
                "text": {
                    "content": text
                }
            }
        ]
    }


def get_rich_text(text):
    """创建富文本属性"""
    if not text:
        return {"rich_text": []}
    return {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": str(text)
                }
            }
        ]
    }


def get_url(url):
    """创建URL属性"""
    return {"url": url}


def get_select(name):
    """创建选择属性"""
    if not name:
        return None
    return {
        "select": {
            "name": name
        }
    }


def get_multi_select(names):
    """创建多选属性"""
    if not names:
        return {"multi_select": []}
    return {
        "multi_select": [
            {"name": name} for name in names if name
        ]
    }


def get_status(status):
    """创建状态属性"""
    if not status:
        return None
    return {
        "status": {
            "name": status
        }
    }


def get_date(date):
    """创建日期属性"""
    if not date:
        return None
    return {
        "date": {
            "start": date
        }
    }


def get_number(number):
    """创建数字属性"""
    if number is None:
        return None
    return {
        "number": number
    }


def get_files(url):
    """创建文件属性"""
    if not url:
        return {"files": []}
    return {
        "files": [
            {
                "type": "external",
                "name": "Cover",
                "external": {
                    "url": url
                }
            }
        ]
    }


def get_icon(url):
    """创建图标"""
    if not url:
        return None
    return {
        "type": "external",
        "external": {
            "url": url
        }
    }


def get_properties(item, properties_type_dict):
    """根据属性类型字典创建属性"""
    properties = {}
    
    for key, property_type in properties_type_dict.items():
        value = item.get(key)
        if value is None:
            continue
            
        if property_type == "title":
            properties[key] = get_title(value)
        elif property_type == "rich_text":
            properties[key] = get_rich_text(value)
        elif property_type == "url":
            properties[key] = get_url(value)
        elif property_type == "select":
            prop = get_select(value)
            if prop:
                properties[key] = prop
        elif property_type == "multi_select":
            properties[key] = get_multi_select(value)
        elif property_type == "status":
            prop = get_status(value)
            if prop:
                properties[key] = prop
        elif property_type == "date":
            if isinstance(value, int):
                # Unix时间戳转换为ISO格式
                date_obj = pendulum.from_timestamp(value, tz=tz)
                iso_date = date_obj.format("YYYY-MM-DD")
                prop = get_date(iso_date)
            else:
                prop = get_date(value)
            if prop:
                properties[key] = prop
        elif property_type == "number":
            prop = get_number(value)
            if prop:
                properties[key] = prop
        elif property_type == "files":
            properties[key] = get_files(value)
    
    return properties


def extract_database_id(notion_url):
    """从Notion URL中提取数据库ID"""
    match = re.search(
        r"([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
        notion_url,
    )
    if match:
        return match.group(0)
    else:
        raise Exception(f"无法从URL中提取数据库ID，请检查URL是否正确: {notion_url}")
