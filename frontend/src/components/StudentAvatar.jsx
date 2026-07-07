const avatarProfiles = {
  S001: { initials: 'T', className: 'student-avatar--tom' },
  S002: { initials: 'A', className: 'student-avatar--alice' },
  S003: { initials: 'B', className: 'student-avatar--bob' },
}

function StudentAvatar({ student, size = 38, className = '' }) {
  const profile = avatarProfiles[student?.student_id] || {
    initials: student?.name?.slice(0, 1)?.toUpperCase() || '?',
    className: 'student-avatar--default',
  }

  return (
    <span
      className={`student-avatar ${profile.className} ${className}`.trim()}
      style={{ '--avatar-size': `${size}px` }}
      aria-label={student?.name ? `${student.name} 头像` : '学生头像'}
      role="img"
    >
      <span>{profile.initials}</span>
    </span>
  )
}

export default StudentAvatar
