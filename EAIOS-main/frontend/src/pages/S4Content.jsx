import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S4Content = () => {
  return (
    <ScenarioTemplate
      scenarioId="S4"
      title="AI内容生产"
      description="在组织风格、统一口径与合规约束下，批量生成多平台内容"
      highlight="企业大脑"
    >
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">多Agent工作流</h3>
        <div className="space-y-3">
          {[
            '节点1: 方向与素材清单助手',
            '节点2: 多平台文案助手',
            '节点3: 合规提示助手 (关键节点)',
            '节点4: 最终定稿/提交助手'
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

export default S4Content
