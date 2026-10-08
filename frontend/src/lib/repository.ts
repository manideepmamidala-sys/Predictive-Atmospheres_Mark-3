const repository = 'https://github.com/manideepmamidala-sys/Predictive-Atmospheres_Mark-3';
const revision = import.meta.env.VITE_REPOSITORY_REF || '261008-ymhz-research-platform-rebuild';

export function repositoryFileUrl(relativePath: string): string | null {
  const segments = relativePath.split('/');
  if (!segments.length || segments.some(segment => !segment || segment === '.' || segment === '..' || !/^[A-Za-z0-9_.-]+$/.test(segment))) return null;
  return `${repository}/blob/${encodeURIComponent(revision)}/${segments.map(encodeURIComponent).join('/')}`;
}
