import React from 'react'
import ScenarioTemplate from '../components/ScenarioTemplate'

const S3CustomerService = () => {
  return (
    <ScenarioTemplate
      scenarioId="S3"
      title="AI智能客服"
      description="面向终端用户的对话式客服：能认人识事、给可执行选项并能举证"
      highlight="企业大脑"
    >
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">对话式交互</h3>

        {/* 聊天界面占位 */}
        <div className="bg-slate-700 rounded-lg p-4 h-64 mb-4 overflow-y-auto">
          <div className="text-gray-400 text-sm text-center py-8">
            点击"开始演示"后，这里将显示客服对话...
          </div>
        </div>

        {/* 输入框占位 */}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="输入消息..."
            className="flex-1 bg-slate-600 border border-slate-500 rounded px-4 py-2 text-gray-200"
            disabled
          />
          <button className="px-6 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors" disabled>
            发送
          </button>
        </div>
      </div>
    </ScenarioTemplate>
  )
}

export default S3CustomerService
