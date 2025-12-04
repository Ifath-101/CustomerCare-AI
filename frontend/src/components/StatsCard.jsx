export default function StatsCard({ title, value }) {
  return (
    <div className="stats-card">
      <div className="stats-title">{title}</div>
      <div className="stats-value">{value}</div>
    </div>
  );
}
