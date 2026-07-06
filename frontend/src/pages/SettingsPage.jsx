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
import { Alert, Avatar, Button, Card, Col, Modal, Radio, Row, Select, Space, Switch, Tag, message } from 'antd'
import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { graphApi, settingsApi } from '../services/copathApi'

function SettingsPage() {
  const { currentStudent, students, loading: appLoading, error: appError, refresh, switchStudent } = useAppData()
  const studentId = currentStudent?.student_id
  const [theme, setTheme] = useState('light')
  const [switching, setSwitching] = useState(false)
  const { data, loading, error, reload } = useAsyncData(
    () => Promise.all([settingsApi.get(), settingsApi.health()]).then(([settings, health]) => ({ settings, health })),
    [],
  )

  useEffect(() => {
    if (data?.settings.theme) setTheme(data.settings.theme)
  }, [data])

  const currentStudentDetail = students.find((student) => student.student_id === studentId)

  const changeStudent = async (value) => {
    setSwitching(true)
    try {
      const selected = students.find((student) => student.student_id === value)
      await switchStudent(value)
      message.success(`已切换至 ${selected.name}`)
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSwitching(false)
    }
  }

  const resetDemo = () => Modal.confirm({
    title: '确认重置 Demo 数据？',
    content: '当前学习事件和手动路径切换会被恢复为初始化状态。',
    okText: '确认重置',
    okButtonProps: { danger: true },
    cancelText: '取消',
    onOk: async () => {
      try {
        const result = await settingsApi.resetDemo()
        await refresh()
        await reload()
        message.success(result.message)
      } catch (requestError) {
        message.error(requestError.message)
        throw requestError
      }
    },
  })

  const reloadGraph = async () => {
    try {
      const graph = await graphApi.get(studentId)
      message.success(`知识图谱已读取：${graph.nodes.length} 个节点，${graph.edges.length} 条关系`)
    } catch (requestError) {
      message.error(requestError.message)
    }
  }

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentStudentDetail) return <PageState empty emptyDescription="Demo 学生或系统设置为空" />

  const apiHealthy = data.health.status === 'running' && data.health.database === 'connected'

  return (
    <div className="page settings-page">
      <PageHeader title="设置" description="管理当前 Demo 学生并检查真实后端和数据库状态。" extra={<Tag color={apiHealthy ? 'green' : 'red'} icon={<CheckCircleFilled />}>API {data.health.status} · DB {data.health.database}</Tag>} />
      <Row gutter={16}>
        <Col span={12}><Card className="soft-card settings-card" title={<Space><UserOutlined /> 当前演示学生</Space>}><div className="student-switch-preview"><Avatar size={54} icon={<UserOutlined />} /><div><strong>{currentStudent.name}</strong><span>{currentStudent.student_id} · Python 程序设计</span></div><Tag color="blue">当前</Tag></div><div className="setting-field"><label>切换 Demo 学生</label><Select loading={switching} value={studentId} onChange={changeStudent} options={students.map((student) => ({ value: student.student_id, label: `${student.name} · ${student.learning_preference}` }))} /><small>切换成功后，所有页面会重新读取该学生的数据。</small></div><div className="student-traits"><div><span>学习速度</span><strong>{currentStudentDetail.learning_speed}</strong></div><div><span>学习偏好</span><strong>{currentStudentDetail.learning_preference}</strong></div></div></Card></Col>
        <Col span={12}><Card className="soft-card settings-card" title={<Space><RobotOutlined /> 模型配置</Space>}><div className="model-status-card"><span><RobotOutlined /></span><div><small>LLM Provider</small><strong>{data.settings.llm_provider}</strong></div><Tag color={data.health.ai === 'available' ? 'green' : 'default'}>{data.health.ai}</Tag></div><div className="setting-field"><label>Model Name</label><Select value={data.settings.model_name} disabled options={[{ value: data.settings.model_name, label: data.settings.model_name }]} /></div><Alert type="info" showIcon message="API Key 仅由 FastAPI 从 .env 读取，不会发送到前端或写入数据库。" /><div className="api-status-row"><span><ApiOutlined /> AI 配置状态</span><Tag color={data.health.ai === 'available' ? 'green' : 'red'}>{data.health.ai}</Tag><Button size="small" onClick={() => reload().then(() => message.success('健康状态已刷新')).catch((requestError) => message.error(requestError.message))}>重新检测</Button></div></Card></Col>
      </Row>
      <Row gutter={16} className="settings-second-row">
        <Col span={12}><Card className="soft-card settings-card" title={<Space><SunOutlined /> 外观设置</Space>}><div className="setting-field"><label>主题模式</label><Radio.Group value={theme} onChange={(event) => { setTheme(event.target.value); message.info('当前 API 仅提供主题读取，写入将在系统优化阶段支持') }}><Radio.Button value="light"><SunOutlined /> 浅色模式</Radio.Button><Radio.Button value="dark"><MoonOutlined /> 深色模式（可选）</Radio.Button></Radio.Group></div><div className="theme-colors"><label>系统主色</label><div>{['#2563eb', '#10b981', '#8b5cf6', '#f59e0b', '#ef5b6c'].map((color) => <button type="button" aria-label={`颜色 ${color}`} style={{ background: color }} key={color} onClick={() => message.info('当前 API 暂不支持主色写入')} />)}</div></div><div className="toggle-row"><span>紧凑布局<small>本地展示选项</small></span><Switch onChange={() => message.info('布局偏好暂未提供保存接口')} /></div></Card></Col>
        <Col span={12}><Card className="soft-card settings-card" title={<Space><DatabaseOutlined /> Demo 数据管理</Space>}><div className="data-action"><span><ReloadOutlined /></span><div><strong>重置 Demo 数据</strong><p>调用后端重建 database/demo.db。</p></div><Button danger onClick={resetDemo}>重置</Button></div><div className="data-action"><span><CloudSyncOutlined /></span><div><strong>重新加载知识图谱</strong><p>从 FastAPI 重新读取知识点和依赖关系。</p></div><Button onClick={reloadGraph}>重新加载</Button></div><div className="data-action"><span><ExperimentOutlined /></span><div><strong>演示环境</strong><p>当前为 SQLite + Neo4j 双数据库环境。</p></div><Tag color="blue">{data.health.status}</Tag></div></Card></Col>
      </Row>
      <div className="settings-footer-note"><SafetyCertificateOutlined /> 所有写操作均通过 FastAPI Service 层执行。</div>
    </div>
  )
}

export default SettingsPage
