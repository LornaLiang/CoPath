import { lazy, Suspense } from 'react'
import { Navigate, createBrowserRouter } from 'react-router-dom'

import AppLayout from '../layouts/AppLayout'

const GoalsPage = lazy(() => import('../pages/GoalsPage'))
const GraphPage = lazy(() => import('../pages/GraphPage'))
const LearningPage = lazy(() => import('../pages/LearningPage'))
const PathsPage = lazy(() => import('../pages/PathsPage'))
const ProfilePage = lazy(() => import('../pages/ProfilePage'))
const RecordsPage = lazy(() => import('../pages/RecordsPage'))
const SettingsPage = lazy(() => import('../pages/SettingsPage'))

const renderPage = (PageComponent) => (
  <Suspense fallback={<div className="route-loading">正在加载页面…</div>}>
    <PageComponent />
  </Suspense>
)

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/goals" replace /> },
      { path: 'goals', element: renderPage(GoalsPage) },
      { path: 'paths', element: renderPage(PathsPage) },
      { path: 'learning', element: renderPage(LearningPage) },
      { path: 'graph', element: renderPage(GraphPage) },
      { path: 'profile', element: renderPage(ProfilePage) },
      { path: 'records', element: renderPage(RecordsPage) },
      { path: 'settings', element: renderPage(SettingsPage) },
      { path: '*', element: <Navigate to="/goals" replace /> },
    ],
  },
])

export default router
