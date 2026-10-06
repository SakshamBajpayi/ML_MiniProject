import { NavLink } from 'react-router-dom';
import { Activity } from 'lucide-react';

export default function Navigation() {
  const navItems = [
    { label: 'OVERVIEW', path: '/' },
    { label: 'PREDICT', path: '/predict' },
    { label: 'MODELS', path: '/models' },
    { label: 'DISCOVER', path: '/discover' },
    { label: 'DATASET', path: '/dataset' },
  ];

  return (
    <nav className="border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-base)]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-[1440px] mx-auto px-6 h-14 flex items-center justify-between">
        
        {/* Logo / Branding */}
        <div className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-blue-500" />
          <span className="font-mono text-xs tracking-[0.2em] font-semibold text-white">QUAKESENSE</span>
        </div>

        {/* Links */}
        <div className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `text-xs font-mono tracking-widest transition-colors duration-200 ${
                  isActive 
                    ? 'text-white border-b border-white pb-1' 
                    : 'text-[var(--color-text-tertiary)] hover:text-white'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
