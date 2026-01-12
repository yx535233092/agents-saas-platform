"""
测试数据加载器
从测试数据库加载测试文档数据
"""
import sqlite3
import random
from pathlib import Path
from typing import List, Dict, Optional
from config import TEST_CONFIG


class TestDataLoader:
    """测试数据加载器"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or TEST_CONFIG["test_db_path"]
        self._data_cache: List[Dict] = []
    
    def load_test_data(self) -> List[Dict]:
        """从数据库加载测试数据"""
        if self._data_cache:
            return self._data_cache
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"测试数据库不存在: {self.db_path}")
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT 文件名, 摘要, 全文 FROM test")
            rows = cursor.fetchall()
            
            self._data_cache = [
                {
                    "doc_title": row["文件名"],
                    "doc_content": row["全文"] or row["摘要"],  # 优先使用全文，没有则用摘要
                    "summary": row["摘要"],
                }
                for row in rows
            ]
            
            print(f"✅ 成功加载 {len(self._data_cache)} 条测试数据")
            return self._data_cache
        finally:
            conn.close()
    
    def get_random_data(self) -> Dict:
        """随机获取一条测试数据"""
        if not self._data_cache:
            self.load_test_data()
        return random.choice(self._data_cache)
    
    def get_data_by_index(self, index: int) -> Dict:
        """根据索引获取测试数据（支持循环）"""
        if not self._data_cache:
            self.load_test_data()
        return self._data_cache[index % len(self._data_cache)]
    
    def get_all_data(self) -> List[Dict]:
        """获取所有测试数据"""
        if not self._data_cache:
            self.load_test_data()
        return self._data_cache.copy()


if __name__ == "__main__":
    # 测试数据加载
    loader = TestDataLoader()
    data = loader.load_test_data()
    print(f"\n测试数据示例（第一条）：")
    print(f"文件名: {data[0]['doc_title']}")
    print(f"内容长度: {len(data[0]['doc_content'])} 字符")
    print(f"摘要: {data[0]['summary'][:100]}...")

