"""
Scenarios API
场景执行接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.state import get_app_state
from app.core.agent import get_orchestrator

router = APIRouter()


class StartScenarioRequest(BaseModel):
    """启动场景请求"""
    scenario_id: str  # S1-S8
    input_data: Dict[str, Any]
    mode: str = "demo"  # demo/real


@router.get("/list")
async def list_scenarios():
    """
    获取所有场景列表

    返回8个场景的基本信息
    """
    scenarios = [
        {
            "id": "S1",
            "name": "AI全域营销",
            "description": "主动式营销内容生成与投放建议",
            "highlight": "主动式"
        },
        {
            "id": "S2",
            "name": "AI智能销售",
            "description": "个性化销售跟进与触达建议",
            "highlight": "主动式"
        },
        {
            "id": "S3",
            "name": "AI智能客服",
            "description": "对话式客服，带记忆与来源证明",
            "highlight": "企业大脑"
        },
        {
            "id": "S4",
            "name": "AI内容生产",
            "description": "企业风格统一的内容生成",
            "highlight": "企业大脑"
        },
        {
            "id": "S5",
            "name": "AI全流程优化",
            "description": "项目/OKR进度管理与优化建议",
            "highlight": "主动式"
        },
        {
            "id": "S6",
            "name": "AI数据分析",
            "description": "自动异常检测与行动建议",
            "highlight": "主动式"
        },
        {
            "id": "S7",
            "name": "AI风控合规",
            "description": "基于企业红线的合同审查",
            "highlight": "企业大脑"
        },
        {
            "id": "S8",
            "name": "AI决策军师",
            "description": "CEO视角的经营简报与行动建议",
            "highlight": "企业大脑"
        }
    ]

    return {
        "success": True,
        "scenarios": scenarios,
        "count": len(scenarios)
    }


@router.get("/{scenario_id}")
async def get_scenario_info(scenario_id: str):
    """
    获取单个场景的详细信息

    包括场景描述、节点配置等
    """
    # TODO: 这里将来返回场景的节点配置、数据需求等
    return {
        "success": True,
        "scenario_id": scenario_id,
        "nodes": [],  # 将来填充节点信息
        "data_sources": []  # 将来填充数据源信息
    }


@router.post("/{scenario_id}/start")
async def start_scenario(scenario_id: str, request: StartScenarioRequest):
    """
    启动场景执行

    注意：实际的场景执行应该通过WebSocket进行，以支持实时状态推送
    这个接口主要用于快速测试
    """
    memory_mgr = get_app_state().memory_manager
    llm_client = get_app_state().llm_client

    if not memory_mgr or not llm_client:
        raise HTTPException(status_code=500, detail="系统未初始化")

    # 获取场景编排器
    orchestrator = get_orchestrator(scenario_id, memory_mgr, llm_client)

    if not orchestrator:
        raise HTTPException(
            status_code=404,
            detail=f"场景 {scenario_id} 未实现或不存在"
        )

    # 执行场景（同步版本，实际应用应该用WebSocket）
    try:
        result = await orchestrator.run(request.input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{scenario_id}/validate")
async def validate_scenario_input(scenario_id: str, input_data: Dict[str, Any]):
    """
    验证场景输入数据

    用于在启动前检查输入数据是否完整
    """
    # TODO: 实现输入验证逻辑
    return {
        "success": True,
        "valid": True,
        "message": "输入数据有效"
    }
