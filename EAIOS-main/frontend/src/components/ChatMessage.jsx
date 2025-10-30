import React from 'react'

/**
 * 聊天消息组件 - 参考ChatGPT/Claude设计
 * @param {string} role - 'agent' | 'user' | 'system' | 'tool'
 * @param {string} content - 消息内容
 * @param {string} agentName - Agent名称（可选）
 * @param {string} icon - Agent图标（可选）
 * @param {boolean} streaming - 是否正在流式输出
 * @param {object} toolCall - 工具调用信息（可选）
 * @param {object} buttons - 交互式按钮（可选）
 * @param {function} onButtonClick - 按钮点击回调（可选）
 */
const ChatMessage = ({ role, content, agentName, icon, streaming, toolCall, buttons, onButtonClick }) => {
  // 自动检测是否正在流式输出（如果内容为空或最后一条Agent消息）
  const isStreaming = streaming || (role === 'agent' && content === '')
  const isAgent = role === 'agent'
  const isSystem = role === 'system'
  const isTool = role === 'tool'

  // 工具调用消息
  if (isTool && toolCall) {
    return (
      <div className="flex justify-center my-3 animate-fade-in">
        <div className="glass border border-brand-500/30 rounded-xl px-4 py-3 max-w-2xl">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-6 h-6 rounded-lg bg-brand-500/20 flex items-center justify-center">
              🛠️
            </div>
            <span className="text-sm font-semibold text-brand-400">
              {toolCall.status === 'calling' && '正在调用工具...'}
              {toolCall.status === 'success' && '工具调用成功'}
              {toolCall.status === 'error' && '工具调用失败'}
            </span>
          </div>
          <div className="text-sm text-text-secondary ml-9">
            <div className="mb-1">
              <span className="text-text-tertiary">工具名称: </span>
              <span className="text-brand-400 font-mono">{toolCall.name}</span>
            </div>
            {toolCall.result && (
              <div className="mt-2 p-2 bg-bg-elevated rounded-lg">
                <span className="text-text-tertiary">结果: </span>
                <span className="text-text-primary">
                  {(() => {
                    // 提取MCP返回的文本内容
                    if (toolCall.result.content && Array.isArray(toolCall.result.content)) {
                      const textContent = toolCall.result.content
                        .filter(item => item.type === 'text')
                        .map(item => item.text)
                        .join(' ')
                        .trim()
                      return textContent || '任务已成功创建'
                    }
                    return '执行成功'
                  })()}
                </span>
              </div>
            )}
            {toolCall.error && (
              <div className="mt-2 p-2 bg-error/10 border border-error/20 rounded-lg text-error">
                {toolCall.error}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (isSystem) {
    return (
      <div className="flex justify-center my-3 animate-fade-in">
        <div className="glass text-text-tertiary text-xs px-3 py-1.5 rounded-full border border-border-subtle">
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

        {/* 交互式按钮 */}
        {buttons && buttons.buttons && buttons.buttons.length > 0 && (
          <div className="flex gap-2 mt-3 animate-fade-in">
            {buttons.buttons.map((button, idx) => (
              <button
                key={idx}
                onClick={() => onButtonClick && onButtonClick(button.value)}
                className="px-4 py-2 bg-brand-500/10 hover:bg-brand-500/20 text-brand-400 border border-brand-500/30 hover:border-brand-500/50 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105"
              >
                {button.text}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
