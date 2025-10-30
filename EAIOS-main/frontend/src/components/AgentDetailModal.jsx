import React from 'react'

/**
 * Agent详情弹窗
 */
const AgentDetailModal = ({ agent, onClose }) => {
  if (!agent) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-slate-800 rounded-lg border border-slate-700 p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{agent.icon}</span>
            <div>
              <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
              <p className="text-sm text-gray-400">{agent.description}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* 当前状态 */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-300 mb-2">当前状态</h4>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  agent.status === 'working'
                    ? 'bg-yellow-400'
                    : agent.status === 'completed'
                    ? 'bg-green-400'
                    : 'bg-gray-400'
                }`}
              />
              <span className="text-sm text-gray-300">{agent.message}</span>
            </div>
          </div>
        </div>

        {/* 输出结果 */}
        {agent.output && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-2">输出结果</h4>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                {JSON.stringify(agent.output, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* 关闭按钮 */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  )
}

export default AgentDetailModal
