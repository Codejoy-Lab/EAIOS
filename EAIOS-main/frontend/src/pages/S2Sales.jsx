import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S2Sales = () => {
  return (
    <ScenarioTemplate
      scenarioId="S2"
      title="AI智能销售"
      description="在关键时刻提醒'先找谁、说什么、为什么'，并提供个性化触达草稿与日程建议"
      highlight="主动式"
    >
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">多Agent工作流</h3>
        <div className="space-y-3">
          {[
            '节点1: 线索评分助手',
            '节点2: 流失预警助手',
            '节点3: 下一步建议助手',
            '节点4: 触达文案助手',
            '节点5: 发信/加会助手 (关键节点)'
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

export default S2Sales
