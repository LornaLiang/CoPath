import {
  AimOutlined,
  BulbOutlined,
  ClockCircleOutlined,
  CompassOutlined,
  RiseOutlined,
  ThunderboltOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Avatar, Card, Col, Progress, Row, Space, Tag } from 'antd'
import { useMemo } from 'react'

import EChart from '../components/EChart'
import MetricCard from '../components/MetricCard'
import PageHeader from '../components/PageHeader'
import { mockMastery, mockProfile } from '../services/mockData'

function ProfilePage() {
  const radarOption = useMemo(() => ({
    radar: {
      radius: '67%',
      indicator: [
        { name: '知识掌握', max: 100 },
        { name: '理解深度', max: 100 },
        { name: '逻辑能力', max: 100 },
        { name: '实践能力', max: 100 },
        { name: '学习积极性', max: 100 },
        { name: '学习速度', max: 100 },
      ],
      splitArea: { areaStyle: { color: ['#fbfdff', '#f5f8fc'] } },
      axisName: { color: '#68768d', fontSize: 10 },
      splitLine: { lineStyle: { color: '#dbe3ef' } },
      axisLine: { lineStyle: { color: '#dbe3ef' } },
    },
    series: [{ type: 'radar', data: [{ value: [68, 72, 80, 65, 90, 70], areaStyle: { color: 'rgba(37,99,235,.22)' }, lineStyle: { color: '#2563eb', width: 2 }, itemStyle: { color: '#2563eb' } }] }],
  }), [])

  const masteryOption = useMemo(() => ({
    grid: { left: 75, right: 20, top: 5, bottom: 5 },
    xAxis: { type: 'value', max: 100, show: false },
    yAxis: { type: 'category', inverse: true, data: mockMastery.map((item) => item.name), axisTick: { show: false }, axisLine: { show: false }, axisLabel: { color: '#516079', fontSize: 11 } },
    series: [{ type: 'bar', data: mockMastery.map((item) => Math.round(item.mastery * 100)), barWidth: 8, showBackground: true, backgroundStyle: { color: '#eef2f7', borderRadius: 8 }, itemStyle: { color: (params) => params.value < 40 ? '#f59e0b' : '#2563eb', borderRadius: 8 }, label: { show: true, position: 'right', formatter: '{c}%', color: '#56647b', fontSize: 10 } }],
  }), [])

  const trendOption = useMemo(() => ({
    grid: { left: 32, right: 12, top: 18, bottom: 25 },
    xAxis: { type: 'category', data: ['7/1', '7/2', '7/3', '7/4', '7/5'], axisLine: { lineStyle: { color: '#dce4ef' } }, axisLabel: { color: '#8793a7' } },
    yAxis: { type: 'value', min: 30, max: 90, splitLine: { lineStyle: { color: '#edf1f6' } }, axisLabel: { color: '#8793a7' } },
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0, itemWidth: 10, textStyle: { fontSize: 10 } },
    series: [
      { name: '测验成绩', type: 'line', smooth: true, data: [58, 62, 54, 68, 72], lineStyle: { color: '#2563eb' }, itemStyle: { color: '#2563eb' } },
      { name: '学习信心', type: 'line', smooth: true, data: [50, 55, 52, 58, 62], lineStyle: { color: '#20b979' }, itemStyle: { color: '#20b979' } },
    ],
  }), [])

  return (
    <div className="page profile-page">
      <PageHeader title="学习画像" description="多维展示你的学习特征、能力水平和近期变化。" extra={<Tag color="green">画像更新于今天 20:10</Tag>} />

      <Card className="soft-card profile-hero">
        <div className="profile-hero__identity">
          <Avatar size={70} icon={<UserOutlined />} />
          <div><span>当前学习者</span><h2>Tom</h2><p>Python 基础课程 · 连续学习 5 天</p></div>
        </div>
        <div className="profile-hero__summary"><span>当前目标</span><strong>{mockProfile.current_goal}</strong><small><AimOutlined /> 目标节点 · 递归</small></div>
        <div className="profile-hero__summary"><span>当前路径</span><strong>{mockProfile.current_path}</strong><small><CompassOutlined /> 已完成 60%</small></div>
        <div className="profile-hero__confidence"><Progress type="dashboard" percent={62} size={82} strokeColor="#2563eb" /><span>学习信心</span></div>
      </Card>

      <div className="metrics-grid profile-metrics">
        <MetricCard icon={<ClockCircleOutlined />} label="学习速度" value="中等" hint="平均每节点 42 分钟" />
        <MetricCard icon={<CompassOutlined />} label="学习偏好" value="基础型" hint="喜欢循序渐进" tone="green" />
        <MetricCard icon={<RiseOutlined />} label="最近状态" value="需巩固" hint="调用栈存在困惑" tone="orange" />
        <MetricCard icon={<ThunderboltOutlined />} label="连续学习" value="5 天" hint="本周累计 3.8 小时" tone="purple" />
      </div>

      <Row gutter={16}>
        <Col span={8}><Card className="soft-card" title="能力雷达"><EChart option={radarOption} height={280} /></Card></Col>
        <Col span={8}><Card className="soft-card" title="知识掌握度"><EChart option={masteryOption} height={280} /></Card></Col>
        <Col span={8}>
          <Card className="soft-card weak-points-card" title="薄弱知识点">
            {[{ name: '调用栈', value: 30, tip: '补充可视化讲解' }, { name: '返回值', value: 55, tip: '完成对比练习' }, { name: '递归', value: 18, tip: '先巩固前置知识' }].map((item) => (
              <div className="weak-point" key={item.name}>
                <div><strong>{item.name}</strong><Tag color={item.value < 30 ? 'red' : 'orange'}>{item.value}%</Tag></div>
                <Progress percent={item.value} showInfo={false} strokeColor={item.value < 30 ? '#ef5b6c' : '#f59e0b'} size="small" />
                <small><BulbOutlined /> {item.tip}</small>
              </div>
            ))}
          </Card>
        </Col>
      </Row>

      <Card className="soft-card profile-trend-card" title="最近学习状态趋势" extra={<Space><span className="status-dot" />画像会随学习过程持续更新</Space>}>
        <EChart option={trendOption} height={220} />
      </Card>
    </div>
  )
}

export default ProfilePage
