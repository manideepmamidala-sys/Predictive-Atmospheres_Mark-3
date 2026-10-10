const repository = 'https://github.com/manideepmamidala-sys/Predictive-Atmospheres_Mark-3';
const revision = import.meta.env.VITE_REPOSITORY_REF || '261008-ymhz-research-platform-rebuild';

export function repositoryFileUrl(relativePath: string, sourceRevision = revision): string | null {
  const segments = relativePath.split('/');
  if (!segments.length || segments.some(segment => !segment || segment === '.' || segment === '..' || /[\\?#\u0000-\u001f\u007f]/.test(segment))) return null;
  return `${repository}/blob/${encodeURIComponent(sourceRevision)}/${segments.map(encodeURIComponent).join('/')}`;
}
