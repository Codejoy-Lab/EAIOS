import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S1Marketing = () => {
  return (
    <ScenarioTemplate
      scenarioId="S1"
      title="AI全域营销"
      description="异常或到点时，系统自动给出今日投放建议+多平台文案+版位/预算建议，可一键发放或模拟发放"
      highlight="主动式"
    >
      {/* 工作流节点区域 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">多Agent工作流</h3>
        <div className="space-y-3">
          {[
            '节点1: 机会识别助手',
            '节点2: 文案与素材助手',
            '节点3: 依据回溯助手',
            '节点4: 发放助手 (关键节点)'
          ].map((node, idx) => (
            <div key={idx} className="bg-slate-700 rounded p-3 flex items-center justify-between">
              <span className="text-gray-300">{node}</span>
              <span className="px-2 py-1 bg-slate-600 rounded text-xs text-gray-400">就绪</span>
            </div>
          ))}
        </div>
      </div>

      {/* 输出区域 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">输出结果</h3>
        <div className="text-gray-400 text-sm">
          点击"开始演示"后，这里将显示今日投放包、发放日志等结果...
        </div>
      </div>
    </ScenarioTemplate>
  )
}

export default S1Marketing
