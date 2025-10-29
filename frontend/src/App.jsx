import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'

// 导入10个页面
import IntroPage from './pages/IntroPage'
import S1Marketing from './pages/S1Marketing'
import S2Sales from './pages/S2Sales'
import S3CustomerService from './pages/S3CustomerService'
import S4Content from './pages/S4Content'
import S5Process from './pages/S5Process'
import S6Analytics from './pages/S6Analytics'
import S7Compliance from './pages/S7Compliance'
import S8Decision from './pages/S8Decision'
import ClosingPage from './pages/ClosingPage'
import MemoryManagement from './pages/MemoryManagement'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          {/* Page 1: 介绍页 */}
          <Route index element={<IntroPage />} />

          {/* Pages 2-9: 八大场景 */}
          <Route path="s1-marketing" element={<S1Marketing />} />
          <Route path="s2-sales" element={<S2Sales />} />
          <Route path="s3-customer-service" element={<S3CustomerService />} />
          <Route path="s4-content" element={<S4Content />} />
          <Route path="s5-process" element={<S5Process />} />
          <Route path="s6-analytics" element={<S6Analytics />} />
          <Route path="s7-compliance" element={<S7Compliance />} />
          <Route path="s8-decision" element={<S8Decision />} />

          {/* Page 10: 结尾页 */}
          <Route path="closing" element={<ClosingPage />} />

          {/* 记忆管理页面（额外功能页） */}
          <Route path="memory" element={<MemoryManagement />} />

          {/* 默认重定向 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
