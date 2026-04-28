import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './History.css'

interface Report {
  id: number
  title: string
  date: string
  time: string
  category: string
  version: string
  summary: string
}

export default function History() {
  const navigate = useNavigate()
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 调用后端API获取简报列表
    fetch('/api/reports?page=1&size=50')
      .then(res => res.json())
      .then(data => {
        if (data.code === 200 && data.data) {
          // 转换后端数据为前端格式
          const formattedReports: Report[] = data.data.records?.map((report: any) => {
            // 将 UTC 时间转换为北京时间 (UTC+8)
            const createdAt = report.createdAt ? new Date(report.createdAt) : new Date()
            const beijingTime = new Date(createdAt.getTime() + 8 * 60 * 60 * 1000)
            const dateStr = beijingTime.toISOString().split('T')[0]
            const timeStr = beijingTime.toTimeString().slice(0, 5)
            
            return {
              id: report.id,
              title: report.title || 'AI 领域每日简报',
              date: dateStr,
              time: timeStr,
              category: 'AI',
              version: `v1.0.${report.id}`,
              summary: report.summary || '点击查看详细简报内容'
            }
          }) || []
          setReports(formattedReports)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('获取简报列表失败:', err)
        setLoading(false)
      })
  }, [])

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'AI': '#00d4aa',
      'Tech': '#7c4dff',
      'Science': '#ff6b6b',
      'Business': '#ffd93d'
    }
    return colors[category] || '#00d4aa'
  }

  const getTimeIcon = (time: string) => {
    const hour = parseInt(time.split(':')[0])
    return hour < 12 ? '🌅' : '🌙'
  }

  if (loading) {
    return (
      <div className="history-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <div className="header-info">
          <h2>📋 历史简报</h2>
          <p className="header-desc">查看所有已生成的 AI 简报</p>
        </div>
        <div className="header-stats">
          <div className="stat-badge">
            <span className="stat-number">{reports.length}</span>
            <span className="stat-label">总计</span>
          </div>
        </div>
      </div>

      <div className="reports-list">
        {reports.map(report => (
          <div key={report.id} className="report-card" onClick={() => navigate(`/report/${report.id}`)}>
            <div className="report-icon">
              {getTimeIcon(report.time)}
            </div>
            <div className="report-content">
              <div className="report-meta">
                <span className="report-category" style={{ borderColor: getCategoryColor(report.category) }}>
                  {report.category}
                </span>
                <span className="report-version">{report.version}</span>
              </div>
              <h3 className="report-title">{report.title}</h3>
              <p className="report-summary">{report.summary}</p>
              <div className="report-footer">
                <span className="report-date">{report.date}</span>
                <span className="report-time">{report.time}</span>
              </div>
            </div>
            <div className="report-arrow">
              →
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
