"""
数据库连接工具类
支持多种数据库类型的连接和测试
"""

import sqlite3
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2 import pool

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 未安装，PostgreSQL 支持不可用")

try:
    import pymysql

    PYMySQL_AVAILABLE = True
except ImportError:
    PYMySQL_AVAILABLE = False
    logger.warning("pymysql 未安装，MySQL 支持不可用")

try:
    import pyodbc

    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    logger.warning("pyodbc 未安装，MSSQL 支持不可用")


class DatabaseConnector:
    """数据库连接器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据库连接器

        Args:
            config: 数据库配置字典，包含 db_type, host, port, database, username, password 等
        """
        self.config = config
        self.db_type = config.get("db_type", "sqlite").lower()

    def build_connection_string(self) -> str:
        """
        构建数据库连接字符串

        Returns:
            连接字符串
        """
        # 如果已经提供了完整的连接字符串，直接使用
        if self.config.get("connection_string"):
            return self.config["connection_string"]

        db_type = self.db_type

        if db_type == "sqlite":
            # SQLite 连接字符串
            database = self.config.get("database") or self.config.get(
                "connection_string"
            )
            if not database:
                raise ValueError("SQLite 需要提供 database 或 connection_string")
            return database

        elif db_type == "postgresql":
            # PostgreSQL 连接字符串
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 5432)
            database = self.config.get("database")
            username = self.config.get("username")
            password = self.config.get("password", "")

            if not database:
                raise ValueError("PostgreSQL 需要提供 database")

            # 构建连接字符串
            conn_str = f"postgresql://"
            if username:
                conn_str += username
                if password:
                    conn_str += f":{password}"
                conn_str += "@"
            conn_str += f"{host}:{port}/{database}"

            # 添加额外参数
            extra_params = self.config.get("extra_params", {})
            if extra_params:
                params = "&".join([f"{k}={v}" for k, v in extra_params.items()])
                conn_str += f"?{params}"

            return conn_str

        elif db_type == "mysql":
            # MySQL 连接字符串
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 3306)
            database = self.config.get("database")
            username = self.config.get("username", "root")
            password = self.config.get("password", "")

            if not database:
                raise ValueError("MySQL 需要提供 database")

            # MySQL 连接字符串格式
            conn_str = f"mysql+pymysql://"
            if username:
                conn_str += username
                if password:
                    conn_str += f":{password}"
                conn_str += "@"
            conn_str += f"{host}:{port}/{database}"

            # 添加额外参数
            extra_params = self.config.get("extra_params", {})
            if extra_params:
                params = "&".join([f"{k}={v}" for k, v in extra_params.items()])
                conn_str += f"?{params}"

            return conn_str

        elif db_type == "mssql":
            # MSSQL 连接字符串
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 1433)
            database = self.config.get("database")
            username = self.config.get("username")
            password = self.config.get("password", "")

            if not database:
                raise ValueError("MSSQL 需要提供 database")

            # MSSQL 连接字符串格式
            conn_str = f"mssql+pyodbc://"
            if username:
                conn_str += username
                if password:
                    conn_str += f":{password}"
                conn_str += "@"
            conn_str += f"{host}:{port}/{database}"

            # 添加额外参数
            extra_params = self.config.get("extra_params", {})
            if extra_params:
                params = ";".join([f"{k}={v}" for k, v in extra_params.items()])
                conn_str += f"?{params}"

            return conn_str

        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def test_connection(self) -> Dict[str, Any]:
        """
        测试数据库连接

        Returns:
            测试结果字典，包含 success, message, details
        """
        try:
            db_type = self.db_type

            if db_type == "sqlite":
                return self._test_sqlite()
            elif db_type == "postgresql":
                return self._test_postgresql()
            elif db_type == "mysql":
                return self._test_mysql()
            elif db_type == "mssql":
                return self._test_mssql()
            else:
                return {
                    "success": False,
                    "message": f"不支持的数据库类型: {db_type}",
                    "details": None,
                }

        except Exception as e:
            logger.error(f"测试数据库连接时发生错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_sqlite(self) -> Dict[str, Any]:
        """测试 SQLite 连接"""
        try:
            database = self.config.get("database") or self.config.get(
                "connection_string"
            )
            if not database:
                return {
                    "success": False,
                    "message": "SQLite 需要提供 database 或 connection_string",
                    "details": None,
                }

            conn = sqlite3.connect(database, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return {
                "success": True,
                "message": "SQLite 连接成功",
                "details": {"database": database, "version": sqlite3.sqlite_version},
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"SQLite 连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_postgresql(self) -> Dict[str, Any]:
        """测试 PostgreSQL 连接"""
        if not PSYCOPG2_AVAILABLE:
            return {
                "success": False,
                "message": "psycopg2 未安装，无法连接 PostgreSQL",
                "details": {"error": "psycopg2 not installed"},
            }

        try:
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 5432)
            database = self.config.get("database")
            username = self.config.get("username")
            password = self.config.get("password", "")

            if not database:
                return {
                    "success": False,
                    "message": "PostgreSQL 需要提供 database",
                    "details": None,
                }

            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return {
                "success": True,
                "message": "PostgreSQL 连接成功",
                "details": {
                    "host": host,
                    "port": port,
                    "database": db_name,
                    "version": version,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"PostgreSQL 连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_mysql(self) -> Dict[str, Any]:
        """测试 MySQL 连接"""
        if not PYMySQL_AVAILABLE:
            return {
                "success": False,
                "message": "pymysql 未安装，无法连接 MySQL",
                "details": {"error": "pymysql not installed"},
            }

        try:
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 3306)
            database = self.config.get("database")
            username = self.config.get("username", "root")
            password = self.config.get("password", "")

            if not database:
                return {
                    "success": False,
                    "message": "MySQL 需要提供 database",
                    "details": None,
                }

            conn = pymysql.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return {
                "success": True,
                "message": "MySQL 连接成功",
                "details": {
                    "host": host,
                    "port": port,
                    "database": db_name,
                    "version": version,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"MySQL 连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    def _test_mssql(self) -> Dict[str, Any]:
        """测试 MSSQL 连接"""
        if not PYODBC_AVAILABLE:
            return {
                "success": False,
                "message": "pyodbc 未安装，无法连接 MSSQL",
                "details": {"error": "pyodbc not installed"},
            }

        try:
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 1433)
            database = self.config.get("database")
            username = self.config.get("username")
            password = self.config.get("password", "")

            if not database:
                return {
                    "success": False,
                    "message": "MSSQL 需要提供 database",
                    "details": None,
                }

            # 构建 ODBC 连接字符串
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            conn_str += f"SERVER={host},{port};"
            conn_str += f"DATABASE={database};"
            if username:
                conn_str += f"UID={username};"
                if password:
                    conn_str += f"PWD={password};"
            else:
                conn_str += "Trusted_Connection=yes;"

            conn = pyodbc.connect(conn_str, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return {
                "success": True,
                "message": "MSSQL 连接成功",
                "details": {
                    "host": host,
                    "port": port,
                    "database": db_name,
                    "version": version[:100] if version else None,  # 限制版本长度
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"MSSQL 连接失败: {str(e)}",
                "details": {"error": str(e)},
            }

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器

        Yields:
            数据库连接对象
        """
        conn = None
        try:
            db_type = self.db_type

            if db_type == "sqlite":
                database = self.config.get("database") or self.config.get(
                    "connection_string"
                )
                if not database:
                    raise ValueError("SQLite 需要提供 database 或 connection_string")
                conn = sqlite3.connect(database, timeout=10)
                conn.row_factory = sqlite3.Row
                yield conn
            elif db_type == "postgresql":
                if not PSYCOPG2_AVAILABLE:
                    raise ImportError("psycopg2 未安装，无法连接 PostgreSQL")
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 5432)
                database = self.config.get("database")
                username = self.config.get("username")
                password = self.config.get("password", "")
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    connect_timeout=10,
                )
                yield conn
            elif db_type == "mysql":
                if not PYMySQL_AVAILABLE:
                    raise ImportError("pymysql 未安装，无法连接 MySQL")
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 3306)
                database = self.config.get("database")
                username = self.config.get("username", "root")
                password = self.config.get("password", "")
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    connect_timeout=10,
                )
                yield conn
            elif db_type == "mssql":
                if not PYODBC_AVAILABLE:
                    raise ImportError("pyodbc 未安装，无法连接 MSSQL")
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 1433)
                database = self.config.get("database")
                username = self.config.get("username")
                password = self.config.get("password", "")
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                conn_str += f"SERVER={host},{port};"
                conn_str += f"DATABASE={database};"
                if username:
                    conn_str += f"UID={username};"
                    if password:
                        conn_str += f"PWD={password};"
                else:
                    conn_str += "Trusted_Connection=yes;"
                conn = pyodbc.connect(conn_str, timeout=10)
                yield conn
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
        finally:
            if conn:
                conn.close()

    def query_data(
        self,
        table_name: str = "test",
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        查询数据库数据

        Args:
            table_name: 表名，默认为 "test"
            columns: 要查询的列，None 表示查询所有列
            limit: 限制返回的记录数
            offset: 偏移量

        Returns:
            数据列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 构建查询语句
            if columns:
                cols = ", ".join(columns)
            else:
                cols = "*"

            query = f"SELECT {cols} FROM {table_name}"
            params = []

            if limit is not None:
                if self.db_type == "postgresql" or self.db_type == "mysql":
                    query += " LIMIT %s OFFSET %s"
                elif self.db_type == "mssql":
                    query += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                else:  # sqlite
                    query += " LIMIT ? OFFSET ?"
                params = [limit, offset] if self.db_type != "mssql" else [offset, limit]
            elif offset > 0:
                if self.db_type == "postgresql" or self.db_type == "mysql":
                    query += " OFFSET %s"
                elif self.db_type == "mssql":
                    query += " OFFSET ? ROWS"
                else:  # sqlite
                    query += " OFFSET ?"
                params = [offset]

            try:
                if self.db_type == "postgresql" or self.db_type == "mysql":
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, params)

                rows = cursor.fetchall()

                # 转换为字典列表
                result = []
                for row in rows:
                    if self.db_type == "sqlite":
                        result.append(dict(row))
                    elif self.db_type == "postgresql":
                        result.append(
                            {col[0]: row[i] for i, col in enumerate(cursor.description)}
                        )
                    elif self.db_type == "mysql":
                        result.append(
                            {col[0]: row[i] for i, col in enumerate(cursor.description)}
                        )
                    elif self.db_type == "mssql":
                        result.append(
                            {col[0]: row[i] for i, col in enumerate(cursor.description)}
                        )

                logger.info(f"成功查询 {len(result)} 条数据")
                return result
            except Exception as e:
                logger.error(f"查询数据时发生错误: {str(e)}")
                raise

    def get_data_count(self, table_name: str = "test") -> int:
        """
        获取数据总数

        Args:
            table_name: 表名

        Returns:
            数据总数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                if self.db_type == "sqlite":
                    result = cursor.fetchone()
                    return result["count"] if result else 0
                else:
                    result = cursor.fetchone()
                    return result[0] if result else 0
            except Exception as e:
                logger.error(f"获取数据总数时发生错误: {str(e)}")
                raise
