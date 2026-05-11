import { Beaker } from 'lucide-react';

export default function DemoBanner({ message }) {
  return (
    <div className="demo-banner">
      <Beaker size={16} />
      <span>{message || 'Demo Mode — This feature uses sample data. Backend integration coming soon.'}</span>
    </div>
  );
}
