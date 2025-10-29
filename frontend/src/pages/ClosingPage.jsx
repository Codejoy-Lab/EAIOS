import React from 'react'
import { Link } from 'react-router-dom'

const ClosingPage = () => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 标题 */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-500 mb-4">
          感谢观看
        </h1>
        <p className="text-xl text-gray-400">
          EAIOS - 企业级Agent操作系统演示
        </p>
      </div>

      {/* 总结 */}
      <div className="bg-slate-800 rounded-lg p-8 border border-slate-700">
        <h2 className="text-2xl font-semibold mb-6 text-gray-200">核心价值总结</h2>
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🧠</div>
            <div>
              <h3 className="font-semibold text-lg text-primary-400 mb-1">企业大脑</h3>
              <p className="text-gray-400">
                统一口径、自动想起、有据可查。让AI真正理解并遵守企业规则。
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="text-2xl">⚡</div>
            <div>
              <h3 className="font-semibold text-lg text-accent-400 mb-1">主动式</h3>
              <p className="text-gray-400">
                不是被动回答，而是主动发现问题、提出建议、推进业务流程。
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="text-2xl">🔗</div>
            <div>
              <h3 className="font-semibold text-lg text-green-400 mb-1">多Agent协同</h3>
              <p className="text-gray-400">
                真实跑通业务流程，支持关键节点确认，确保企业级可控性。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 已演示场景 */}
      <div className="bg-slate-800 rounded-lg p-8 border border-slate-700">
        <h2 className="text-2xl font-semibold mb-4 text-gray-200">已演示场景</h2>
        <div className="grid grid-cols-2 gap-3">
          {[
            'S1 AI全域营销',
            'S2 AI智能销售',
            'S3 AI智能客服',
            'S4 AI内容生产',
            'S5 AI全流程优化',
            'S6 AI数据分析',
            'S7 AI风控合规',
            'S8 AI决策军师'
          ].map((scenario) => (
            <div key={scenario} className="flex items-center gap-2 text-gray-300">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>{scenario}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 联系方式占位 */}
      <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
        <h2 className="text-2xl font-semibold mb-4 text-gray-200">联系我们</h2>
        <p className="text-gray-400 mb-6">
          如需了解更多或定制企业级Agent解决方案
        </p>
        <div className="flex justify-center gap-4">
          <div className="text-gray-400">
            邮箱: contact@eaios.com
          </div>
          <div className="text-gray-400">
            电话: 400-XXX-XXXX
          </div>
        </div>
      </div>

      {/* 返回首页 */}
      <div className="text-center py-8">
        <Link
          to="/"
          className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600 text-white font-semibold rounded-lg shadow-lg transition-all"
        >
          返回首页
        </Link>
      </div>
    </div>
  )
}

export default ClosingPage
