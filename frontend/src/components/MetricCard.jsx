function MetricCard({ icon, label, value, hint, tone = 'blue' }) {
  return (
    <div className="metric-card">
      <div className={`metric-card__icon metric-card__icon--${tone}`}>{icon}</div>
      <div>
        <div className="metric-card__label">{label}</div>
        <div className="metric-card__value">{value}</div>
        {hint ? <div className="metric-card__hint">{hint}</div> : null}
      </div>
    </div>
  )
}

export default MetricCard
