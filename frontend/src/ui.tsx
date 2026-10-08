import type { ReactNode } from 'react';

export function PageHeading({ eyebrow, title, intro }: { eyebrow: string; title: string; intro: string }) {
  return <header className="page-heading"><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p className="lead">{intro}</p></header>;
}
export function Section({ title, children }: { title: string; children: ReactNode }) {
  return <section aria-label={title}><h2 className="section-title">{title}</h2>{children}</section>;
}
export function Notice({ title, children, warning = false }: { title: string; children: ReactNode; warning?: boolean }) {
  return <div className={`notice${warning ? ' warning' : ''}`} role="status"><strong>{title}</strong><div>{children}</div></div>;
}
export function Figure({ title, caption, children }: { title: string; caption: string; children: ReactNode }) {
  return <figure className="figure"><h3>{title}</h3>{children}<figcaption>{caption}</figcaption></figure>;
}
export function Empty({ subject }: { subject: string }) {
  return <Notice title={`${subject} unavailable`}><p>The current research export has no validated data for this view. Check the export provenance or choose another filter.</p></Notice>;
}
export function Value({ value, unit }: { value: number | null | undefined; unit?: string }) {
  return <>{value == null || !Number.isFinite(value) ? 'Unavailable' : `${new Intl.NumberFormat('en', { maximumFractionDigits: 2 }).format(value)}${unit ? ` ${unit}` : ''}`}</>;
}
export const modelStatusLabel = (status: string) => status === 'not_better_than_baseline' ? 'Not better than baseline' : status.replaceAll('_', ' ');
