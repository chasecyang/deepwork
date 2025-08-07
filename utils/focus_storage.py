"""
专注数据存储模块
使用SQLite数据库持久化存储专注会话和AI分析结果
"""
import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .focus_data import FocusSession, FocusAnalysisResult
from .common import PathUtils

logger = logging.getLogger(__name__)


class FocusDataStorage:
    """专注数据存储类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据存储
        
        Args:
            db_path: 数据库文件路径，默认为项目根目录下的focus_data.db
        """
        if db_path is None:
            project_root = PathUtils.get_project_root()
            db_path = project_root / "focus_data.db"
        
        self.db_path = str(db_path)
        self._init_database()
        logger.info(f"专注数据存储初始化完成: {self.db_path}")
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建专注会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS focus_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    planned_duration INTEGER NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    is_paused BOOLEAN NOT NULL DEFAULT 0,
                    total_pause_duration REAL NOT NULL DEFAULT 0,
                    total_focused_time REAL NOT NULL DEFAULT 0,
                    total_distracted_time REAL NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建AI分析结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS focus_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    screenshot_path TEXT,
                    visual_description TEXT,
                    is_focused BOOLEAN NOT NULL,
                    feedback_message TEXT,
                    recommended_emoji TEXT,
                    analysis_duration REAL NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES focus_sessions (id)
                )
            ''')
            
            # 创建索引提高查询效率
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time 
                ON focus_sessions (start_time)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_analysis_session_id 
                ON focus_analysis_results (session_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_analysis_timestamp 
                ON focus_analysis_results (timestamp)
            ''')
            
            conn.commit()
            logger.debug("数据库表结构初始化完成")
    
    def save_session(self, session: FocusSession) -> int:
        """
        保存专注会话到数据库
        
        Args:
            session: 专注会话对象
            
        Returns:
            int: 会话ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO focus_sessions 
                (goal, planned_duration, start_time, end_time, is_active, 
                 is_paused, total_pause_duration, total_focused_time, total_distracted_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.goal,
                session.planned_duration,
                session.start_time,
                session.end_time,
                session.is_active,
                session.is_paused,
                session.total_pause_duration,
                session.total_focused_time,
                session.total_distracted_time
            ))
            
            session_id = cursor.lastrowid
            conn.commit()
            
            logger.debug(f"保存专注会话成功，ID: {session_id}")
            return session_id
    
    def update_session(self, session_id: int, session: FocusSession):
        """
        更新专注会话
        
        Args:
            session_id: 会话ID
            session: 专注会话对象
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE focus_sessions 
                SET goal=?, planned_duration=?, start_time=?, end_time=?, 
                    is_active=?, is_paused=?, total_pause_duration=?, 
                    total_focused_time=?, total_distracted_time=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                session.goal,
                session.planned_duration,
                session.start_time,
                session.end_time,
                session.is_active,
                session.is_paused,
                session.total_pause_duration,
                session.total_focused_time,
                session.total_distracted_time,
                session_id
            ))
            
            conn.commit()
            logger.debug(f"更新专注会话成功，ID: {session_id}")
    
    def save_analysis_result(self, session_id: int, result: FocusAnalysisResult) -> int:
        """
        保存AI分析结果
        
        Args:
            session_id: 关联的会话ID
            result: AI分析结果对象
            
        Returns:
            int: 分析结果ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO focus_analysis_results 
                (session_id, timestamp, screenshot_path, visual_description, 
                 is_focused, feedback_message, recommended_emoji, analysis_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                result.timestamp,
                result.screenshot_path,
                result.visual_description,
                result.is_focused,
                result.feedback_message,
                result.recommended_emoji,
                result.analysis_duration
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            
            logger.debug(f"保存AI分析结果成功，ID: {result_id}")
            return result_id
    
    def get_session_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        获取专注会话历史
        
        Args:
            limit: 返回条数限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 会话历史列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, goal, planned_duration, start_time, end_time, 
                       is_active, total_focused_time, total_distracted_time,
                       (SELECT COUNT(*) FROM focus_analysis_results WHERE session_id = focus_sessions.id) as analysis_count
                FROM focus_sessions 
                ORDER BY start_time DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            sessions = []
            for row in cursor.fetchall():
                session_data = {
                    'id': row[0],
                    'goal': row[1],
                    'planned_duration': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'is_active': bool(row[5]),
                    'total_focused_time': row[6],
                    'total_distracted_time': row[7],
                    'analysis_count': row[8],
                    'actual_duration': (row[4] - row[3]) / 60 if row[4] else 0,
                    'completion_rate': min(100, ((row[4] - row[3]) / 60) / row[2] * 100) if row[4] else 0,
                    'started_at': datetime.fromtimestamp(row[3]).strftime("%Y-%m-%d %H:%M:%S"),
                    'ended_at': datetime.fromtimestamp(row[4]).strftime("%Y-%m-%d %H:%M:%S") if row[4] else None
                }
                sessions.append(session_data)
            
            return sessions
    
    def get_session_details(self, session_id: int) -> Optional[Dict]:
        """
        获取会话详细信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict]: 会话详情
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取会话基本信息
            cursor.execute('''
                SELECT id, goal, planned_duration, start_time, end_time, 
                       is_active, total_focused_time, total_distracted_time
                FROM focus_sessions 
                WHERE id = ?
            ''', (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            # 获取分析结果
            cursor.execute('''
                SELECT timestamp, is_focused, feedback_message, recommended_emoji, analysis_duration
                FROM focus_analysis_results 
                WHERE session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))
            
            analysis_results = []
            for row in cursor.fetchall():
                analysis_results.append({
                    'timestamp': row[0],
                    'is_focused': bool(row[1]),
                    'feedback_message': row[2],
                    'recommended_emoji': row[3],
                    'analysis_duration': row[4],
                    'time_str': datetime.fromtimestamp(row[0]).strftime("%H:%M:%S")
                })
            
            # 构建详细信息
            session_data = {
                'id': session_row[0],
                'goal': session_row[1],
                'planned_duration': session_row[2],
                'start_time': session_row[3],
                'end_time': session_row[4],
                'is_active': bool(session_row[5]),
                'total_focused_time': session_row[6],
                'total_distracted_time': session_row[7],
                'analysis_results': analysis_results,
                'actual_duration': (session_row[4] - session_row[3]) / 60 if session_row[4] else 0,
                'completion_rate': min(100, ((session_row[4] - session_row[3]) / 60) / session_row[2] * 100) if session_row[4] else 0,
                'started_at': datetime.fromtimestamp(session_row[3]).strftime("%Y-%m-%d %H:%M:%S"),
                'ended_at': datetime.fromtimestamp(session_row[4]).strftime("%Y-%m-%d %H:%M:%S") if session_row[4] else None
            }
            
            return session_data
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        获取统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            Dict: 统计信息
        """
        since_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 总会话数
            cursor.execute('''
                SELECT COUNT(*) FROM focus_sessions 
                WHERE start_time >= ?
            ''', (since_timestamp,))
            total_sessions = cursor.fetchone()[0]
            
            # 完成的会话数
            cursor.execute('''
                SELECT COUNT(*) FROM focus_sessions 
                WHERE start_time >= ? AND end_time IS NOT NULL
            ''', (since_timestamp,))
            completed_sessions = cursor.fetchone()[0]
            
            # 总专注时间
            cursor.execute('''
                SELECT SUM(total_focused_time) FROM focus_sessions 
                WHERE start_time >= ?
            ''', (since_timestamp,))
            total_focused_time = cursor.fetchone()[0] or 0
            
            # 总分心时间
            cursor.execute('''
                SELECT SUM(total_distracted_time) FROM focus_sessions 
                WHERE start_time >= ?
            ''', (since_timestamp,))
            total_distracted_time = cursor.fetchone()[0] or 0
            
            # 平均专注时长
            cursor.execute('''
                SELECT AVG(end_time - start_time) FROM focus_sessions 
                WHERE start_time >= ? AND end_time IS NOT NULL
            ''', (since_timestamp,))
            avg_session_duration = cursor.fetchone()[0] or 0
            
            # 最常见的目标
            cursor.execute('''
                SELECT goal, COUNT(*) as count FROM focus_sessions 
                WHERE start_time >= ?
                GROUP BY goal 
                ORDER BY count DESC 
                LIMIT 5
            ''', (since_timestamp,))
            top_goals = cursor.fetchall()
            
            return {
                'period_days': days,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                'total_focused_time_minutes': total_focused_time / 60,
                'total_distracted_time_minutes': total_distracted_time / 60,
                'avg_session_duration_minutes': avg_session_duration / 60 if avg_session_duration else 0,
                'focus_efficiency': (total_focused_time / (total_focused_time + total_distracted_time) * 100) if (total_focused_time + total_distracted_time) > 0 else 0,
                'top_goals': [(goal, count) for goal, count in top_goals]
            }
    
    def delete_session(self, session_id: int):
        """
        删除会话及其相关分析结果
        
        Args:
            session_id: 会话ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 删除分析结果
            cursor.execute('DELETE FROM focus_analysis_results WHERE session_id = ?', (session_id,))
            
            # 删除会话
            cursor.execute('DELETE FROM focus_sessions WHERE id = ?', (session_id,))
            
            conn.commit()
            logger.info(f"删除会话及相关数据成功，ID: {session_id}")
    
    def cleanup_old_data(self, days: int = 90):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        cutoff_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取要删除的会话ID
            cursor.execute('SELECT id FROM focus_sessions WHERE start_time < ?', (cutoff_timestamp,))
            old_session_ids = [row[0] for row in cursor.fetchall()]
            
            if old_session_ids:
                # 删除旧的分析结果
                cursor.execute(f'DELETE FROM focus_analysis_results WHERE session_id IN ({",".join("?" * len(old_session_ids))})', old_session_ids)
                
                # 删除旧的会话
                cursor.execute('DELETE FROM focus_sessions WHERE start_time < ?', (cutoff_timestamp,))
                
                conn.commit()
                logger.info(f"清理了 {len(old_session_ids)} 个旧会话的数据")


# 全局存储实例
_focus_storage = None


def get_focus_storage() -> FocusDataStorage:
    """
    获取专注数据存储实例（单例模式）
    
    Returns:
        FocusDataStorage: 存储实例
    """
    global _focus_storage
    if _focus_storage is None:
        _focus_storage = FocusDataStorage()
    return _focus_storage
