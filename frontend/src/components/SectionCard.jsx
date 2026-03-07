export default function SectionCard({ title, description, children }) {
  return (
    <section className="section-card">
      <h2>{title}</h2>
      {description ? <p>{description}</p> : null}
      {children}
    </section>
  );
}
