import React from 'react'
import { Link } from 'react-router-dom'

const IntroPage = () => {
  return (
    <div className="space-y-8">
      {/* 标题区 */}
      <div className="text-center py-12">
        <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-500 mb-4">
          EAIOS
        </h1>
        <h2 className="text-3xl font-semibold text-gray-200 mb-6">
          企业级Agent操作系统
        </h2>
        <p className="text-xl text-gray-400 max-w-3xl mx-auto">
          演示企业级、主动式、带记忆管理的多Agent协同平台
        </p>
      </div>

      {/* 核心特性 */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="text-2xl mb-3">🧠</div>
          <h3 className="text-xl font-semibold mb-2 text-primary-400">企业大脑</h3>
          <p className="text-gray-400">
            统一口径、自动想起、有据可查的企业记忆管理系统
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="text-2xl mb-3">⚡</div>
          <h3 className="text-xl font-semibold mb-2 text-accent-400">主动式</h3>
          <p className="text-gray-400">
            AI主动发现问题、提出建议、推进业务流程
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div className="text-2xl mb-3">🔗</div>
          <h3 className="text-xl font-semibold mb-2 text-green-400">多Agent协同</h3>
          <p className="text-gray-400">
            多个智能体协同工作，真实跑通业务流程
          </p>
        </div>
      </div>

      {/* 八大场景 */}
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold text-center mb-6">八大场景演示</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            { path: '/s1-marketing', title: 'S1 AI全域营销', tag: '主动式', desc: '自动营销内容生成与投放建议' },
            { path: '/s2-sales', title: 'S2 AI智能销售', tag: '主动式', desc: '个性化销售跟进与触达' },
            { path: '/s3-customer-service', title: 'S3 AI智能客服', tag: '企业大脑', desc: '对话式客服，带记忆与来源' },
            { path: '/s4-content', title: 'S4 AI内容生产', tag: '企业大脑', desc: '企业风格统一的内容生成' },
            { path: '/s5-process', title: 'S5 AI全流程优化', tag: '主动式', desc: '项目/OKR进度管理与优化' },
            { path: '/s6-analytics', title: 'S6 AI数据分析', tag: '主动式', desc: '自动异常检测与行动建议' },
            { path: '/s7-compliance', title: 'S7 AI风控合规', tag: '企业大脑', desc: '基于企业红线的合同审查' },
            { path: '/s8-decision', title: 'S8 AI决策军师', tag: '企业大脑', desc: 'CEO视角的经营简报' },
          ].map((scenario) => (
            <Link
              key={scenario.path}
              to={scenario.path}
              className="bg-slate-800 hover:bg-slate-750 rounded-lg p-6 border border-slate-700 hover:border-primary-500 transition-all group"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-lg font-semibold text-gray-200 group-hover:text-primary-400 transition-colors">
                  {scenario.title}
                </h4>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  scenario.tag === '主动式'
                    ? 'bg-accent-500/20 text-accent-400'
                    : 'bg-primary-500/20 text-primary-400'
                }`}>
                  {scenario.tag}
                </span>
              </div>
              <p className="text-gray-400 text-sm">{scenario.desc}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* 开始按钮 */}
      <div className="text-center py-8">
        <Link
          to="/s1-marketing"
          className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600 text-white font-semibold rounded-lg shadow-lg transition-all transform hover:scale-105"
        >
          开始演示
          <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </div>
    </div>
  )
}

export default IntroPage
