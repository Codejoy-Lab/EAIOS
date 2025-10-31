"""
S6 Analytics API
S6数据分析场景API - 企业数据中台
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
from app.core.data_analyzer import get_data_analyzer

router = APIRouter()


class MetricsSubmission(BaseModel):
    """Metrics提交请求"""
    scenario: str
    metrics: Dict


@router.post("/collect")
async def collect_metrics(req: MetricsSubmission):
    """
    收集场景metrics数据

    各场景主动上报metrics到S6
    """
    analyzer = get_data_analyzer()

    try:
        analyzer.collect_metrics(req.scenario, req.metrics)
        return {
            "success": True,
            "message": f"S6已收集{req.scenario}的metrics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/latest")
async def get_latest_report():
    """
    获取最新综合分析报告

    S8决策军师调用此接口获取分析报告
    """
    analyzer = get_data_analyzer()

    try:
        report = analyzer.get_latest_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/scenario/{scenario}")
async def get_scenario_report(scenario: str):
    """
    获取单个场景分析摘要

    Args:
        scenario: 场景名称（如 s3_customer_service）
    """
    analyzer = get_data_analyzer()

    try:
        summary = analyzer.get_scenario_summary(scenario)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/trigger")
async def trigger_analysis():
    """
    手动触发全场景分析

    立即生成最新的分析报告
    """
    analyzer = get_data_analyzer()

    try:
        report = analyzer.analyze_all_scenarios()
        return {
            "success": True,
            "report_id": report["report_id"],
            "message": "分析报告已生成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights():
    """
    获取跨场景洞察

    提取关键发现和异常
    """
    analyzer = get_data_analyzer()

    try:
        report = analyzer.get_latest_report()
        return {
            "insights": report.get("insights", []),
            "generated_at": report.get("generated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
