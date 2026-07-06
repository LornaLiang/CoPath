import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { goalApi, pathApi, settingsApi, studentApi } from '../services/copathApi'

const AppDataContext = createContext(null)

export function AppDataProvider({ children }) {
  const [state, setState] = useState({
    currentStudent: null,
    students: [],
    goals: [],
    currentPath: null,
    health: null,
    loading: true,
    error: null,
  })

  const refresh = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }))
    try {
      const currentStudent = await studentApi.getCurrent()
      const [students, goals, currentPath, health] = await Promise.all([
        studentApi.list(),
        goalApi.list(),
        pathApi.getCurrent(currentStudent.student_id),
        settingsApi.health(),
      ])
      setState({ currentStudent, students, goals, currentPath, health, loading: false, error: null })
      return currentStudent
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error }))
      throw error
    }
  }, [])

  useEffect(() => {
    refresh().catch(() => {})
  }, [refresh])

  const switchStudent = useCallback(async (studentId) => {
    await settingsApi.switchStudent(studentId)
    return refresh()
  }, [refresh])

  const value = useMemo(() => ({ ...state, refresh, switchStudent }), [state, refresh, switchStudent])

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>
}

export function useAppData() {
  const context = useContext(AppDataContext)
  if (!context) throw new Error('useAppData must be used inside AppDataProvider')
  return context
}
