import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S5Process = () => {
  return (
    <ScenarioTemplate
      scenarioId="S5"
      title="AI全流程优化"
      description="每天自动收集进度、识别阻塞、提出排程建议并生成明日优先事项"
      highlight="主动式"
    >
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">多Agent工作流</h3>
        <div className="space-y-3">
          {[
            '节点1: 进度收集助手',
            '节点2: 风险/阻塞识别助手',
            '节点3: 排程建议助手 (关键节点)',
            '节点4: 日报/明日优先助手'
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

export default S5Process
