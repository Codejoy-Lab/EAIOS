import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S7Compliance = () => {
  return (
    <ScenarioTemplate
      scenarioId="S7"
      title="AI风控合规"
      description="依据组织自有红线与历史谈判经验，对新合同做风险分级、条款对照与建议改写"
      highlight="企业大脑"
    >
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">多Agent工作流</h3>
        <div className="space-y-3">
          {[
            '节点1: 条款对照助手',
            '节点2: 风险分级助手',
            '节点3: 建议改写助手',
            '节点4: 审批提醒/阻断助手 (关键节点)'
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

export default S7Compliance
