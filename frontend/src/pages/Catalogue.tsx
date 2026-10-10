import { Suspense, lazy } from 'react';
import { Link } from 'react-router-dom';
import { useAnalysisProducts, type AnalysisId } from '../lib/research';
import { Notice } from '../ui';

const ResearchChart = lazy(() => import('../figures/ResearchChart'));

export default function Catalogue({ ids, title = 'Research questions' }: { ids: readonly AnalysisId[]; title?: string }) {
  const state = useAnalysisProducts(ids);
  return <section className="catalogue" aria-label={title}><div className="section-heading"><div><p className="eyebrow">Versioned analyses</p><h2>{title}</h2></div><Link to="/methods">How these analyses were made ↗</Link></div>
    {state.status === 'loading' && <p className="status" role="status">Loading analyses {state.completed} of {state.total}…</p>}
    {state.status === 'error' && <Notice title="Analysis catalogue unavailable" warning><p>{state.message} The room archive and core research records remain available.</p></Notice>}
    {state.products.map(product => <div className="analysis-row" key={product.id}><div className="analysis-index"><span>{product.id}</span><Link to={`/explore?analysis=${product.id}`}>See related data ↗</Link></div><Suspense fallback={<p role="status">Loading chart…</p>}><ResearchChart product={product} /></Suspense></div>)}
  </section>;
}
