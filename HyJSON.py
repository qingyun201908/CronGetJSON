import json
import mysql.connector
from mysql.connector import Error

def load_config():
    """返回数据库配置"""
    return {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'test'
    }

def read_json_file(file_path):
    """从文件中读取JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 如果JSON是单个对象，转换为列表
            if isinstance(data, dict):
                return [data]
            return data
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到")
        exit(1)
    except json.JSONDecodeError:
        print("错误：JSON格式无效")
        exit(1)

def save_to_mysql(data):
    """将数据保存到MySQL数据库"""
    db_config = load_config()
    
    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）- 包含所有字段
        create_table_query = """
        CREATE TABLE IF NOT EXISTS posts (
            id INT PRIMARY KEY,
            date VARCHAR(50),
            text TEXT NOT NULL,
            views INT,
            forwards INT,
            media_type VARCHAR(50),
            images JSON,       # 修改为 JSON 类型
            url VARCHAR(255),
            original_name VARCHAR(255),
            size INT,
            thumb VARCHAR(255), # 新增缩略图字段
            media_group_id VARCHAR(100),
            reply JSON         # 修改为 JSON 类型
        )
        """
        cursor.execute(create_table_query)
        
        # 准备插入或更新数据
        insert_query = """
        INSERT INTO posts (
            id, date, text, views, forwards, media_type, 
            images, url, original_name, size, thumb, media_group_id, reply  # 添加thumb字段
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  # 13个占位符

        ON DUPLICATE KEY UPDATE 
            date = VALUES(date),
            text = VALUES(text),
            views = VALUES(views),
            forwards = VALUES(forwards),
            media_type = VALUES(media_type),
            images = VALUES(images),
            url = VALUES(url),
            original_name = VALUES(original_name),
            size = VALUES(size),
            thumb = VALUES(thumb),  # 添加thumb更新
            media_group_id = VALUES(media_group_id),
            reply = VALUES(reply)
        """
        
        # 收集要插入的数据
        records = []
        for item in data:
            images = json.dumps(item['images']) if 'images' in item else None
            reply = json.dumps(item['reply']) if 'reply' in item else None
            
            record = (
                item['id'],
                item.get('date'),
                item.get('text', ''),
                item.get('views'),
                item.get('forwards'),
                item.get('media_type'),
                images,  # 序列化的 JSON
                item.get('url'),
                item.get('original_name'),
                int(item.get('size', 0)),  # 字符串转整数
                item.get('thumb'),         # 新增字段
                item.get('media_group_id'),
                reply     # 序列化的 JSON
            )
            records.append(record)        

        
        # 批量插入数据
        cursor.executemany(insert_query, records)
        conn.commit()
        
        print(f"成功保存 {len(records)} 条记录到数据库")
        
    except Error as e:
        print("数据库错误:", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # 配置文件路径
    json_file = 'a.json'
    
    # 读取JSON数据
    json_data = read_json_file(json_file)
    
    # 保存到MySQL
    save_to_mysql(json_data)