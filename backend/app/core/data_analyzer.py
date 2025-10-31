"""
Data Analyzer - S6数据分析核心
负责收集、分析各场景数据，生成分析报告
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path


class DataAnalyzer:
    """S6数据分析器 - 企业数据中台"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # 各场景metrics文件路径
        self.metrics_files = {
            "s3_customer_service": self.data_dir / "s3_metrics.json",
            "s1_marketing": self.data_dir / "s1_metrics.json",
            "s2_sales": self.data_dir / "s2_metrics.json",
            "s4_content": self.data_dir / "s4_metrics.json",
            "s5_process": self.data_dir / "s5_metrics.json",
            "s7_compliance": self.data_dir / "s7_metrics.json"
        }

        # 分析报告存储路径
        self.report_file = self.data_dir / "s6_analysis_report.json"

    def collect_metrics(self, scenario: str, metrics: Dict):
        """
        收集场景metrics数据

        Args:
            scenario: 场景名称（如 s3_customer_service）
            metrics: 指标数据
        """
        file_path = self.metrics_files.get(scenario)
        if not file_path:
            print(f"⚠️  未知场景: {scenario}")
            return

        # 加载现有数据
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"history": []}

        # 添加时间戳
        metrics["timestamp"] = datetime.now().isoformat()

        # 追加新数据
        data["history"].append(metrics)

        # 保留最近100条记录
        if len(data["history"]) > 100:
            data["history"] = data["history"][-100:]

        # 保存
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ S6收集metrics: {scenario}")

    def load_scenario_metrics(self, scenario: str) -> Optional[Dict]:
        """加载场景metrics"""
        file_path = self.metrics_files.get(scenario)
        if not file_path or not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_s3_customer_service(self) -> Dict:
        """分析S3客服数据"""
        data = self.load_scenario_metrics("s3_customer_service")

        if not data or not data.get("history"):
            return {
                "scenario": "s3_customer_service",
                "status": "no_data",
                "message": "暂无客服数据"
            }

        # 获取最新数据
        latest = data["history"][-1]

        # 计算趋势（最近5条记录）
        recent = data["history"][-5:]
        satisfaction_trend = [r.get("satisfaction_rate", 0) for r in recent]
        avg_satisfaction = sum(satisfaction_trend) / len(satisfaction_trend)

        # 异常检测
        alerts = []
        if latest.get("complaint_rate", 0) > 0.1:
            alerts.append({
                "level": "high",
                "message": f"投诉率过高: {latest.get('complaint_rate', 0) * 100:.1f}%"
            })

        if latest.get("satisfaction_rate", 1) < 0.8:
            alerts.append({
                "level": "medium",
                "message": f"满意度偏低: {latest.get('satisfaction_rate', 0) * 100:.1f}%"
            })

        return {
            "scenario": "s3_customer_service",
            "status": "ok",
            "key_metrics": {
                "total_consultations": latest.get("total_consultations", 0),
                "satisfaction_rate": latest.get("satisfaction_rate", 0),
                "complaint_rate": latest.get("complaint_rate", 0),
                "avg_response_time": latest.get("avg_response_time", 0)
            },
            "trends": {
                "satisfaction_avg": avg_satisfaction,
                "satisfaction_change": satisfaction_trend[-1] - satisfaction_trend[0] if len(satisfaction_trend) > 1 else 0
            },
            "alerts": alerts,
            "updated_at": latest.get("timestamp")
        }

    def analyze_all_scenarios(self) -> Dict:
        """分析所有场景数据，生成综合报告"""
        report = {
            "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "scenarios": {}
        }

        # 分析S3客服
        report["scenarios"]["s3_customer_service"] = self.analyze_s3_customer_service()

        # TODO: 分析其他场景（S1, S2, S4, S5, S7）
        # 目前先实现S3，其他场景可以后续添加

        # 生成总体洞察
        report["insights"] = self._generate_insights(report["scenarios"])

        # 保存报告
        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ S6生成分析报告: {report['report_id']}")

        return report

    def _generate_insights(self, scenarios: Dict) -> List[Dict]:
        """生成跨场景洞察"""
        insights = []

        # S3客服洞察
        s3 = scenarios.get("s3_customer_service", {})
        if s3.get("status") == "ok":
            alerts = s3.get("alerts", [])
            if alerts:
                insights.append({
                    "type": "alert",
                    "source": "s3_customer_service",
                    "message": f"客服场景发现{len(alerts)}个异常",
                    "details": alerts
                })

            # 满意度趋势
            trend_change = s3.get("trends", {}).get("satisfaction_change", 0)
            if trend_change > 0.05:
                insights.append({
                    "type": "positive",
                    "source": "s3_customer_service",
                    "message": "客服满意度持续上升",
                    "details": {"change": trend_change}
                })
            elif trend_change < -0.05:
                insights.append({
                    "type": "negative",
                    "source": "s3_customer_service",
                    "message": "客服满意度出现下滑",
                    "details": {"change": trend_change}
                })

        return insights

    def get_latest_report(self) -> Optional[Dict]:
        """获取最新分析报告"""
        if not self.report_file.exists():
            # 如果没有报告，生成一个
            return self.analyze_all_scenarios()

        with open(self.report_file, "r", encoding="utf-8") as f:
            report = json.load(f)

        # 检查报告是否过期（超过5分钟）
        generated_at = datetime.fromisoformat(report["generated_at"])
        if datetime.now() - generated_at > timedelta(minutes=5):
            # 重新生成报告
            return self.analyze_all_scenarios()

        return report

    def get_scenario_summary(self, scenario: str) -> Dict:
        """获取单个场景摘要"""
        report = self.get_latest_report()
        return report["scenarios"].get(scenario, {
            "scenario": scenario,
            "status": "no_data",
            "message": "暂无数据"
        })


# 单例
_data_analyzer_instance = None


def get_data_analyzer() -> DataAnalyzer:
    """获取数据分析器单例"""
    global _data_analyzer_instance
    if _data_analyzer_instance is None:
        _data_analyzer_instance = DataAnalyzer()
    return _data_analyzer_instance
