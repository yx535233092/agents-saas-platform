"""
测试数据库连接和批量处理工具
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# 测试数据库路径配置
# 支持通过环境变量 TEST_DB_PATH 配置，默认为项目根目录下的 db/test.db
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_TEST_DB_PATH = PROJECT_ROOT / "db" / "test.db"
TEST_DB_PATH = os.getenv("TEST_DB_PATH", str(DEFAULT_TEST_DB_PATH))


class TestDatabase:
    """测试数据库连接和操作类"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化测试数据库连接

        Args:
            db_path: 数据库文件路径，如果为 None 则使用环境变量或默认路径
        """
        self.db_path = db_path or TEST_DB_PATH
        self._connection: Optional[sqlite3.Connection] = None

    @contextmanager
    def connect(self):
        """
        数据库连接上下文管理器

        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            # 检查数据库文件是否存在
            db_file = Path(self.db_path)
            if not db_file.exists():
                raise FileNotFoundError(f"测试数据库文件不存在: {self.db_path}")

            # 连接数据库
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # 使用 Row 工厂，返回字典式结果
            logger.info(f"成功连接到测试数据库: {self.db_path}")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"数据库连接错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"连接数据库时发生错误: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("数据库连接已关闭")

    def get_all_data(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有测试数据

        Args:
            limit: 限制返回的记录数，None 表示不限制
            offset: 偏移量，用于分页

        Returns:
            测试数据列表，每条数据为字典格式
        """
        with self.connect() as conn:
            cursor = conn.cursor()

            # 构建查询语句
            query = "SELECT * FROM test"
            params = []

            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params = [limit, offset]
            elif offset > 0:
                query += " OFFSET ?"
                params = [offset]

            try:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                # 转换为字典列表
                result = []
                for row in rows:
                    result.append(dict(row))

                logger.info(f"成功获取 {len(result)} 条测试数据")
                return result
            except sqlite3.Error as e:
                logger.error(f"查询数据时发生错误: {str(e)}")
                raise

    def get_data_count(self) -> int:
        """
        获取测试数据总数

        Returns:
            数据总数
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) as count FROM test")
                result = cursor.fetchone()
                count = result["count"] if result else 0
                logger.info(f"测试数据总数: {count}")
                return count
            except sqlite3.Error as e:
                logger.error(f"获取数据总数时发生错误: {str(e)}")
                raise

    def get_data_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取单条数据

        Args:
            record_id: 记录 ID

        Returns:
            数据字典，如果不存在则返回 None
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM test WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
            except sqlite3.Error as e:
                logger.error(f"根据 ID 查询数据时发生错误: {str(e)}")
                raise

    def batch_process(
        self,
        processor: Callable[[Dict[str, Any]], Any],
        batch_size: int = 10,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        批量处理数据库中的数据

        Args:
            processor: 处理函数，接收一个数据字典，返回处理结果
            batch_size: 每批处理的记录数
            limit: 限制处理的记录数，None 表示处理所有
            offset: 起始偏移量

        Returns:
            处理结果统计
        """
        total_processed = 0
        total_success = 0
        total_failed = 0
        errors = []

        try:
            # 获取要处理的数据
            data_list = self.get_all_data(limit=limit, offset=offset)
            total_count = len(data_list)

            logger.info(f"开始批量处理，共 {total_count} 条数据，批次大小: {batch_size}")

            # 分批处理
            for i in range(0, total_count, batch_size):
                batch = data_list[i : i + batch_size]
                batch_num = (i // batch_size) + 1

                logger.info(f"处理第 {batch_num} 批，共 {len(batch)} 条数据")

                for item in batch:
                    try:
                        result = processor(item)
                        total_success += 1
                        logger.debug(f"成功处理记录 ID {item.get('id')}: {result}")
                    except Exception as e:
                        total_failed += 1
                        error_msg = f"处理记录 ID {item.get('id')} 时出错: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)

                    total_processed += 1

            result = {
                "total_processed": total_processed,
                "total_success": total_success,
                "total_failed": total_failed,
                "errors": errors,
            }

            logger.info(
                f"批量处理完成: 总计 {total_processed}，成功 {total_success}，失败 {total_failed}"
            )
            return result

        except Exception as e:
            logger.error(f"批量处理过程中发生错误: {str(e)}")
            raise

    def test_connection(self) -> Dict[str, Any]:
        """
        测试数据库连接

        Returns:
            连接测试结果
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # 尝试查询表结构
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='test'"
                )
                table_exists = cursor.fetchone() is not None

                if table_exists:
                    # 获取数据总数
                    count = self.get_data_count()
                    return {
                        "connected": True,
                        "db_path": self.db_path,
                        "table_exists": True,
                        "record_count": count,
                        "message": "数据库连接成功",
                    }
                else:
                    return {
                        "connected": True,
                        "db_path": self.db_path,
                        "table_exists": False,
                        "record_count": 0,
                        "message": "数据库连接成功，但表 'test' 不存在",
                    }
        except Exception as e:
            return {
                "connected": False,
                "db_path": self.db_path,
                "table_exists": False,
                "record_count": 0,
                "message": f"数据库连接失败: {str(e)}",
                "error": str(e),
            }


# 创建全局实例
test_db = TestDatabase()

