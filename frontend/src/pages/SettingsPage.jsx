import {
  ApiOutlined,
  CheckCircleFilled,
  CloudSyncOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  MoonOutlined,
  ReloadOutlined,
  RobotOutlined,
  SafetyCertificateOutlined,
  SunOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Alert, Avatar, Button, Card, Col, Radio, Row, Select, Space, Switch, Tag, message } from 'antd'
import { useState } from 'react'

import PageHeader from '../components/PageHeader'
import { mockStudents } from '../services/mockData'

function SettingsPage() {
  const [studentId, setStudentId] = useState('S001')
  const [theme, setTheme] = useState('light')

  const currentStudent = mockStudents.find((student) => student.student_id === studentId)

  return (
    <div className="page settings-page">
      <PageHeader title="设置" description="管理 Demo 学生、模型展示、主题和本地演示数据。" extra={<Tag color="green" icon={<CheckCircleFilled />}>API 状态正常 · Mock</Tag>} />

      <Row gutter={16}>
        <Col span={12}>
          <Card className="soft-card settings-card" title={<Space><UserOutlined /> 当前演示学生</Space>}>
            <div className="student-switch-preview">
              <Avatar size={54} icon={<UserOutlined />} />
              <div><strong>{currentStudent.name}</strong><span>{currentStudent.student_id} · Python 基础课程</span></div>
              <Tag color="blue">当前</Tag>
            </div>
            <div className="setting-field">
              <label>切换 Demo 学生</label>
              <Select value={studentId} onChange={(value) => { setStudentId(value); message.success(`已切换至 ${mockStudents.find((item) => item.student_id === value).name}（Mock）`) }} options={mockStudents.map((student) => ({ value: student.student_id, label: `${student.name} · ${student.learning_preference}` }))} />
              <small>切换后，所有页面将在联调阶段重新加载该学生的数据。</small>
            </div>
            <div className="student-traits">
              <div><span>学习速度</span><strong>{currentStudent.learning_speed}</strong></div>
              <div><span>学习偏好</span><strong>{currentStudent.learning_preference}</strong></div>
            </div>
          </Card>
        </Col>

        <Col span={12}>
          <Card className="soft-card settings-card" title={<Space><RobotOutlined /> 模型配置</Space>}>
            <div className="model-status-card">
              <span><RobotOutlined /></span>
              <div><small>LLM Provider</small><strong>OpenAI Compatible API</strong></div>
              <Tag>Milestone 7 启用</Tag>
            </div>
            <div className="setting-field"><label>Model Name</label><Select defaultValue="gpt-4.1-mini" disabled options={[{ value: 'gpt-4.1-mini', label: 'gpt-4.1-mini' }]} /></div>
            <Alert type="info" showIcon message="前端不会显示或保存 API Key；密钥仅由后端环境变量管理。" />
            <div className="api-status-row"><span><ApiOutlined /> API 状态检测</span><Tag color="green">Database connected</Tag><Button size="small" onClick={() => message.success('健康检查通过（Mock）')}>重新检测</Button></div>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} className="settings-second-row">
        <Col span={12}>
          <Card className="soft-card settings-card" title={<Space><SunOutlined /> 外观设置</Space>}>
            <div className="setting-field">
              <label>主题模式</label>
              <Radio.Group value={theme} onChange={(event) => { setTheme(event.target.value); message.info('主题切换将在系统优化阶段启用') }}>
                <Radio.Button value="light"><SunOutlined /> 浅色模式</Radio.Button>
                <Radio.Button value="dark"><MoonOutlined /> 深色模式（可选）</Radio.Button>
              </Radio.Group>
            </div>
            <div className="theme-colors"><label>系统主色</label><div>{['#2563eb', '#10b981', '#8b5cf6', '#f59e0b', '#ef5b6c'].map((color) => <button type="button" aria-label={`颜色 ${color}`} style={{ background: color }} key={color} onClick={() => message.info('主色预览仅作占位')} />)}</div></div>
            <div className="toggle-row"><span>紧凑布局<small>减少卡片间距，显示更多内容</small></span><Switch /></div>
          </Card>
        </Col>

        <Col span={12}>
          <Card className="soft-card settings-card" title={<Space><DatabaseOutlined /> Demo 数据管理</Space>}>
            <div className="data-action">
              <span><ReloadOutlined /></span><div><strong>重置 Demo 数据</strong><p>恢复 Tom、Alice、Bob 以及默认学习记录。</p></div><Button danger onClick={() => message.warning('重置请求将在 Milestone 5 调用后端')}>重置</Button>
            </div>
            <div className="data-action">
              <span><CloudSyncOutlined /></span><div><strong>重新加载知识图谱</strong><p>重新读取本地知识点和依赖关系。</p></div><Button onClick={() => message.success('知识图谱已重新加载（Mock）')}>重新加载</Button>
            </div>
            <div className="data-action">
              <span><ExperimentOutlined /></span><div><strong>演示环境</strong><p>当前为本地 SQLite 原型环境。</p></div><Tag color="blue">Development</Tag>
            </div>
          </Card>
        </Col>
      </Row>

      <div className="settings-footer-note"><SafetyCertificateOutlined /> 所有操作仅作用于本地 Demo 环境，不包含登录认证或云端同步。</div>
    </div>
  )
}

export default SettingsPage
