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
import { Avatar, Layout, Menu, Progress, Space, Tag, Typography } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

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

function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const pageTitle = pageTitles[location.pathname] || 'CoPath'

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
          <strong>掌握递归</strong>
          <span>Python 基础课程</span>
          <div className="sider-goal-card__progress">
            <span>学习进度</span><b>60%</b>
          </div>
          <Progress percent={60} showInfo={false} size="small" strokeColor="#2563eb" />
          <div className="sider-goal-card__meta"><ClockCircleOutlined /> 预计还需 3 小时</div>
        </div>
      </Sider>

      <Layout>
        <Header className="app-header">
          <div className="app-header__title">
            <HomeOutlined />
            <Typography.Text>{pageTitle}</Typography.Text>
          </div>
          <Space size={10} className="app-header__status">
            <Tag icon={<CheckCircleFilled />} color="success">路径进行中</Tag>
            <Tag color="blue">AI 助手 · Mock</Tag>
            <div className="header-user">
              <Avatar size={32} icon={<UserOutlined />} />
              <span><strong>Tom</strong><small>当前学生</small></span>
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
