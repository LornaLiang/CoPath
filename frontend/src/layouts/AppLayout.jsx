import {
  AimOutlined,
  ApartmentOutlined,
  BookOutlined,
  BulbOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  HistoryOutlined,
  HomeOutlined,
  RadarChartOutlined,
  ReadOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Layout, Menu, Progress, Segmented, Space, Tag, Typography, message } from 'antd'
import { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import StudentAvatar from '../components/StudentAvatar'
import { useAppData } from '../hooks/useAppData'

const { Header, Content, Sider } = Layout

const navigationItems = [
  { key: '/goals', label: '学习目标', icon: <AimOutlined /> },
  { key: '/paths', label: '学习路径', icon: <ApartmentOutlined /> },
  { key: '/learning', label: '我的学习', icon: <ReadOutlined /> },
  { key: '/graph', label: '知识图谱', icon: <RadarChartOutlined /> },
  { key: '/profile', label: '学习画像', icon: <UserOutlined /> },
  { key: '/records', label: '学习记录', icon: <HistoryOutlined /> },
  { key: '/settings', label: '设置', icon: <SettingOutlined /> },
]

const pageTitles = Object.fromEntries(navigationItems.map((item) => [item.key, item.label]))
const demoModeEnabled = import.meta.env.VITE_DEMO_MODE !== 'false'

function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { currentStudent, currentPath, goals, health, error, students, switchStudent } = useAppData()
  const [switchingStudent, setSwitchingStudent] = useState(false)
  const pageTitle = pageTitles[location.pathname] || 'CoPath'
  const currentGoal = goals.find((goal) => goal.goal_id === currentStudent?.current_goal_id)
  const completedNodes = currentPath?.nodes.filter((node) => node.status === 'completed').length || 0
  const totalNodes = currentPath?.nodes.length || 0
  const progress = totalNodes ? Math.round((completedNodes / totalNodes) * 100) : 0
  const currentNode = currentPath?.nodes.find((node) => node.status === 'learning')

  const switchDemoStudent = async (studentId) => {
    if (studentId === currentStudent?.student_id) return
    setSwitchingStudent(true)
    try {
      const student = students.find((item) => item.student_id === studentId)
      await switchStudent(studentId)
      message.success(`Demo 已切换至 ${student?.name || studentId}`)
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSwitchingStudent(false)
    }
  }

  return (
    <Layout className="app-shell">
      <Sider className="app-sider" width={216} theme="light">
        <div className="brand">
          <span className="brand__mark"><BookOutlined /></span>
          <span>
            <strong>CoPath</strong>
            <small>自适应学习系统</small>
          </span>
        </div>
        <Menu
          className="app-menu"
          mode="inline"
          items={navigationItems}
          selectedKeys={[location.pathname]}
          onClick={({ key }) => navigate(key)}
        />
        <div className="sider-goal-card">
          <div className="sider-goal-card__label"><BulbOutlined /> 当前目标</div>
          <strong>{currentGoal?.title || '等待数据库'}</strong>
          <span>Python 基础课程</span>
          <div className="sider-goal-card__progress">
            <span>学习进度</span><b>{progress}%</b>
          </div>
          <Progress percent={progress} showInfo={false} size="small" strokeColor="#2563eb" />
          <div className="sider-goal-card__meta"><ClockCircleOutlined /> 当前节点 · {currentNode?.name || '待加载'}</div>
        </div>
      </Sider>

      <Layout>
        <Header className="app-header">
          <div className="app-header__title">
            <HomeOutlined />
            <Typography.Text>{pageTitle}</Typography.Text>
          </div>
          <Space size={10} className="app-header__status">
            {demoModeEnabled && students.length ? (
              <div className="demo-switcher">
                <Tag color="blue">Demo Mode</Tag>
                <Segmented
                  size="small"
                  disabled={switchingStudent}
                  value={currentStudent?.student_id}
                  options={students.map((student) => ({ label: <span className="demo-switcher__student"><StudentAvatar student={student} size={22} />{student.name}</span>, value: student.student_id }))}
                  onChange={switchDemoStudent}
                />
              </div>
            ) : null}
            <Tag icon={<CheckCircleFilled />} color={error ? 'error' : 'success'}>{error ? 'API 连接异常' : currentPath?.status === 'active' ? '路径进行中' : '路径待开始'}</Tag>
            <Tag color={health?.ai === 'available' ? 'blue' : 'default'}>AI · {health?.ai || '检测中'}</Tag>
            <div className="header-user">
              <StudentAvatar student={currentStudent} size={32} />
              <span><strong>{currentStudent?.name || '加载中'}</strong><small>当前学生</small></span>
            </div>
          </Space>
        </Header>

        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout
