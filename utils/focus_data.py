"""
专注数据模型
定义专注会话的数据结构和管理
"""
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class FocusAnalysisResult:
    """单次专注分析结果"""
    timestamp: float
    screenshot_path: str
    visual_description: str
    is_focused: bool
    feedback_message: str
    recommended_emoji: str
    analysis_duration: float  # 分析耗时


@dataclass
class FocusSession:
    """专注会话数据"""
    # 基本信息
    goal: str
    planned_duration: int  # 计划时长（分钟）
    start_time: float
    end_time: Optional[float] = None
    
    # 状态信息
    is_active: bool = True
    is_paused: bool = False
    pause_start_time: Optional[float] = None
    total_pause_duration: float = 0.0
    
    # 分析结果
    analysis_results: List[FocusAnalysisResult] = field(default_factory=list)
    
    # 统计信息
    total_focused_time: float = 0.0
    total_distracted_time: float = 0.0
    
    def get_elapsed_time(self) -> float:
        """获取已经过的时间（秒）"""
        if self.end_time:
            return self.end_time - self.start_time
        else:
            current_time = time.time()
            if self.is_paused and self.pause_start_time:
                return current_time - self.start_time - self.total_pause_duration
            else:
                return current_time - self.start_time
    
    def get_remaining_time(self) -> float:
        """获取剩余时间（秒）"""
        planned_seconds = self.planned_duration * 60
        elapsed = self.get_elapsed_time()
        return max(0, planned_seconds - elapsed)
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.get_remaining_time() <= 0
    
    def add_analysis_result(self, result: FocusAnalysisResult):
        """添加分析结果"""
        self.analysis_results.append(result)
        self._update_statistics()
    
    def _update_statistics(self):
        """更新统计信息"""
        if not self.analysis_results:
            return
        
        # 计算专注时间和分心时间（简化计算，假设每次分析代表10秒）
        analysis_interval = 10  # 秒
        focused_count = sum(1 for r in self.analysis_results if r.is_focused)
        
        self.total_focused_time = focused_count * analysis_interval
        self.total_distracted_time = (len(self.analysis_results) - focused_count) * analysis_interval
    
    def pause(self):
        """暂停专注"""
        if not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time.time()
    
    def resume(self):
        """恢复专注"""
        if self.is_paused and self.pause_start_time:
            self.total_pause_duration += time.time() - self.pause_start_time
            self.is_paused = False
            self.pause_start_time = None
    
    def complete(self):
        """完成专注会话"""
        if self.is_paused:
            self.resume()
        self.is_active = False
        self.end_time = time.time()
    
    def get_summary(self) -> Dict:
        """获取会话摘要"""
        elapsed_minutes = self.get_elapsed_time() / 60
        
        return {
            "goal": self.goal,
            "planned_duration": self.planned_duration,
            "actual_duration": elapsed_minutes,
            "completion_rate": min(100, (elapsed_minutes / self.planned_duration) * 100),
            "focused_time": self.total_focused_time / 60,
            "distracted_time": self.total_distracted_time / 60,
            "analysis_count": len(self.analysis_results),
            "started_at": datetime.fromtimestamp(self.start_time).strftime("%H:%M:%S"),
            "ended_at": datetime.fromtimestamp(self.end_time).strftime("%H:%M:%S") if self.end_time else None
        }


class FocusSessionManager:
    """专注会话管理器"""
    
    def __init__(self):
        self.current_session: Optional[FocusSession] = None
        self.session_history: List[FocusSession] = []
    
    def start_session(self, goal: str, duration_minutes: int) -> FocusSession:
        """开始新的专注会话"""
        if self.current_session and self.current_session.is_active:
            self.end_current_session()
        
        self.current_session = FocusSession(
            goal=goal,
            planned_duration=duration_minutes,
            start_time=time.time()
        )
        
        return self.current_session
    
    def end_current_session(self):
        """结束当前会话"""
        if self.current_session:
            self.current_session.complete()
            self.session_history.append(self.current_session)
            self.current_session = None
    
    def pause_current_session(self):
        """暂停当前会话"""
        if self.current_session:
            self.current_session.pause()
    
    def resume_current_session(self):
        """恢复当前会话"""
        if self.current_session:
            self.current_session.resume()
    
    def get_current_session(self) -> Optional[FocusSession]:
        """获取当前会话"""
        return self.current_session
    
    def is_session_active(self) -> bool:
        """是否有活跃的会话"""
        return self.current_session is not None and self.current_session.is_active