import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S6Analytics = () => {
  return (
    <ScenarioTemplate
      scenarioId="S6"
      title="AI数据分析"
      description="指标异常或晨报到点时，自动输出'哪里异常—可能原因—建议动作'"
      highlight="主动式"
    >
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">多Agent工作流</h3>
        <div className="space-y-3">
          {[
            '节点1: 异常检测助手',
            '节点2: 归因助手',
            '节点3: 改进建议助手 (关键节点)',
            '节点4: 推送助手'
          ].map((node, idx) => (
            <div key={idx} className="bg-slate-700 rounded p-3 flex items-center justify-between">
              <span className="text-gray-300">{node}</span>
              <span className="px-2 py-1 bg-slate-600 rounded text-xs text-gray-400">就绪</span>
            </div>
          ))}
        </div>
      </div>
    </ScenarioTemplate>
  )
}

export default S6Analytics
