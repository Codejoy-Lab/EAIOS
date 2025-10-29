import React from 'react'

/**
 * 聊天消息组件 - 参考ChatGPT/Claude设计
 * @param {string} role - 'agent' | 'user' | 'system'
 * @param {string} content - 消息内容
 * @param {string} agentName - Agent名称（可选）
 * @param {string} icon - Agent图标（可选）
 * @param {boolean} streaming - 是否正在流式输出
 */
const ChatMessage = ({ role, content, agentName, icon, streaming }) => {
  // 自动检测是否正在流式输出（如果内容为空或最后一条Agent消息）
  const isStreaming = streaming || (role === 'agent' && content === '')
  const isAgent = role === 'agent'
  const isSystem = role === 'system'

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-slate-800/50 text-gray-500 text-xs px-3 py-1.5 rounded border border-slate-700/50">
          {content}
        </div>
      </div>
    )
  }

  return (
    <div className={`group flex gap-3 px-4 py-4 hover:bg-slate-800/30 transition-colors ${!isAgent ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className="flex-shrink-0">
        {isAgent ? (
          <div className="w-7 h-7 rounded-sm bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white text-base shadow-sm">
            {icon || '🤖'}
          </div>
        ) : (
          <div className="w-7 h-7 rounded-sm bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white text-base shadow-sm">
            👤
          </div>
        )}
      </div>

      {/* 消息内容 */}
      <div className={`flex flex-col gap-1 flex-1 min-w-0 ${!isAgent ? 'items-end' : ''}`}>
        {agentName && (
          <span className="text-xs font-medium text-gray-400">{agentName}</span>
        )}
        <div className={`text-[15px] leading-relaxed ${isAgent ? 'text-gray-200' : 'text-gray-200'}`}>
          <div className="whitespace-pre-wrap break-words">
            {content || (isStreaming && '正在思考...')}
          </div>
          {isStreaming && content && (
            <span className="inline-block w-0.5 h-5 bg-emerald-500 ml-0.5 animate-pulse align-middle">│</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
