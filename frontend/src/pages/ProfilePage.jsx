import {
  AimOutlined,
  BulbOutlined,
  ClockCircleOutlined,
  CompassOutlined,
  RiseOutlined,
  ThunderboltOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Avatar, Card, Col, Empty, Progress, Row, Space, Tag } from 'antd'
import { useMemo } from 'react'

import EChart from '../components/EChart'
import MetricCard from '../components/MetricCard'
import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { learningApi, profileApi } from '../services/copathApi'

const speedLabels = { slow: '较慢', medium: '中等', fast: '较快' }
const preferenceLabels = { basic: '基础型', example: '案例型', fast: '快速型' }
const stateLabels = { confused: '存在困惑', ready_to_advance: '可进阶', needs_example: '需要案例', focused: '专注' }

function ProfilePage() {
  const { currentStudent, currentPath, loading: appLoading, error: appError, refresh } = useAppData()
  const studentId = currentStudent?.student_id
  const { data, loading, error, reload } = useAsyncData(
    () => studentId
      ? Promise.all([profileApi.get(studentId), profileApi.getMastery(studentId), learningApi.listEvents(studentId)]).then(([profile, mastery, events]) => ({ profile, mastery, events }))
      : Promise.resolve(null),
    [studentId],
  )

  const averageMastery = data?.mastery.length ? Math.round(data.mastery.reduce((total, item) => total + item.mastery, 0) / data.mastery.length * 100) : 0
  const speedScore = { slow: 45, medium: 70, fast: 92 }[data?.profile.learning_speed] || 0

  const radarOption = useMemo(() => ({
    radar: { radius: '67%', indicator: [{ name: '知识掌握', max: 100 }, { name: '学习信心', max: 100 }, { name: '事件完成', max: 100 }, { name: '学习速度', max: 100 }, { name: '路径进度', max: 100 }], splitArea: { areaStyle: { color: ['#fbfdff', '#f5f8fc'] } }, axisName: { color: '#68768d', fontSize: 10 }, splitLine: { lineStyle: { color: '#dbe3ef' } }, axisLine: { lineStyle: { color: '#dbe3ef' } } },
    series: [{ type: 'radar', data: [{ value: [averageMastery, Math.round((data?.profile.confidence || 0) * 100), Math.min(100, (data?.events.length || 0) * 12), speedScore, currentPath ? Math.round(currentPath.nodes.filter((node) => node.status === 'completed').length / currentPath.nodes.length * 100) : 0], areaStyle: { color: 'rgba(37,99,235,.22)' }, lineStyle: { color: '#2563eb', width: 2 }, itemStyle: { color: '#2563eb' } }] }],
  }), [averageMastery, data, speedScore, currentPath])

  const masteryOption = useMemo(() => ({
    grid: { left: 75, right: 20, top: 5, bottom: 5 }, xAxis: { type: 'value', max: 100, show: false }, yAxis: { type: 'category', inverse: true, data: data?.mastery.map((item) => item.name) || [], axisTick: { show: false }, axisLine: { show: false }, axisLabel: { color: '#516079', fontSize: 11 } },
    series: [{ type: 'bar', data: data?.mastery.map((item) => Math.round(item.mastery * 100)) || [], barWidth: 8, showBackground: true, backgroundStyle: { color: '#eef2f7', borderRadius: 8 }, itemStyle: { color: (params) => params.value < 40 ? '#f59e0b' : '#2563eb', borderRadius: 8 }, label: { show: true, position: 'right', formatter: '{c}%', color: '#56647b', fontSize: 10 } }],
  }), [data])

  const trendEvents = useMemo(() => [...(data?.events || [])].filter((event) => event.score != null).reverse().slice(-8), [data])
  const trendOption = useMemo(() => ({
    grid: { left: 32, right: 12, top: 18, bottom: 25 }, xAxis: { type: 'category', data: trendEvents.map((event) => event.created_at.slice(5, 16)), axisLine: { lineStyle: { color: '#dce4ef' } }, axisLabel: { color: '#8793a7' } }, yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#edf1f6' } }, axisLabel: { color: '#8793a7' } }, tooltip: { trigger: 'axis' }, series: [{ name: '学习成绩', type: 'line', smooth: true, data: trendEvents.map((event) => Math.round(event.score * 100)), lineStyle: { color: '#2563eb' }, itemStyle: { color: '#2563eb' }, areaStyle: { color: 'rgba(37,99,235,.08)' } }],
  }), [trendEvents])

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentPath) return <PageState empty emptyDescription="当前学生尚无学习画像" />

  const confidence = Math.round(data.profile.confidence * 100)
  const completed = currentPath.nodes.filter((node) => node.status === 'completed').length
  const weakPoints = data.profile.weak_points.map((name) => ({ name, mastery: data.mastery.find((item) => item.name === name)?.mastery || 0 }))

  return (
    <div className="page profile-page">
      <PageHeader title="学习画像" description="画像、掌握度和事件趋势均读取自当前学生数据库记录。" extra={<Tag color="green">学生 ID · {studentId}</Tag>} />
      <Card className="soft-card profile-hero"><div className="profile-hero__identity"><Avatar size={70} icon={<UserOutlined />} /><div><span>当前学习者</span><h2>{currentStudent.name}</h2><p>Python 程序设计</p></div></div><div className="profile-hero__summary"><span>当前目标</span><strong>{data.profile.current_goal}</strong><small><AimOutlined /> {currentStudent.current_goal_id}</small></div><div className="profile-hero__summary"><span>当前路径</span><strong>{data.profile.current_path}</strong><small><CompassOutlined /> 已完成 {completed}/{currentPath.nodes.length}</small></div><div className="profile-hero__confidence"><Progress type="dashboard" percent={confidence} size={82} strokeColor="#2563eb" /><span>学习信心</span></div></Card>
      <div className="metrics-grid profile-metrics"><MetricCard icon={<ClockCircleOutlined />} label="学习速度" value={speedLabels[data.profile.learning_speed]} hint={data.profile.learning_speed} /><MetricCard icon={<CompassOutlined />} label="学习偏好" value={preferenceLabels[data.profile.learning_preference]} hint={data.profile.learning_preference} tone="green" /><MetricCard icon={<RiseOutlined />} label="最近状态" value={stateLabels[data.profile.recent_state] || data.profile.recent_state} hint={`${data.events.length} 条学习事件`} tone="orange" /><MetricCard icon={<ThunderboltOutlined />} label="平均掌握度" value={`${averageMastery}%`} hint={`${data.mastery.length} 个画像知识点`} tone="purple" /></div>
      <Row gutter={16}>
        <Col span={8}><Card className="soft-card" title="能力雷达"><EChart option={radarOption} height={280} /></Card></Col>
        <Col span={8}><Card className="soft-card" title="知识掌握度">{data.mastery.length ? <EChart option={masteryOption} height={280} /> : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无掌握度数据" />}</Card></Col>
        <Col span={8}><Card className="soft-card weak-points-card" title="薄弱知识点">{weakPoints.length ? weakPoints.map((item) => <div className="weak-point" key={item.name}><div><strong>{item.name}</strong><Tag color={item.mastery < .3 ? 'red' : 'orange'}>{Math.round(item.mastery * 100)}%</Tag></div><Progress percent={Math.round(item.mastery * 100)} showInfo={false} strokeColor={item.mastery < .3 ? '#ef5b6c' : '#f59e0b'} size="small" /><small><BulbOutlined /> 建议查看该节点的讲解与练习资源</small></div>) : <div className="insight-box"><span><BulbOutlined /></span><div>当前没有记录明显薄弱点，可以继续学习。</div></div>}</Card></Col>
      </Row>
      <Card className="soft-card profile-trend-card" title="最近学习成绩趋势" extra={<Space><span className="status-dot" />数据来自 learning_events</Space>}>{trendEvents.length ? <EChart option={trendOption} height={220} /> : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无带成绩的学习事件" />}</Card>
    </div>
  )
}

export default ProfilePage
