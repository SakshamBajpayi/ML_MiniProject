import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] p-3 shadow-xl">
        <p className="text-[10px] font-mono text-[var(--color-text-tertiary)] mb-2">AGE: {label} YEARS</p>
        {payload.map((p, i) => (
          <div key={i} className="flex justify-between gap-4 text-xs font-mono mb-1">
            <span style={{ color: p.color }}>GRADE 0{i + 1}</span>
            <span className="text-white">{p.value}%</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function Discover() {
  const ageData = [
    { range: '0-10', grade1: 45, grade2: 40, grade3: 15 },
    { range: '10-20', grade1: 25, grade2: 50, grade3: 25 },
    { range: '20-40', grade1: 15, grade2: 55, grade3: 30 },
    { range: '40-80', grade1: 10, grade2: 50, grade3: 40 },
    { range: '80+', grade1: 5, grade2: 40, grade3: 55 },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-5xl"
    >
      <header className="mb-12">
        <h1 className="text-3xl font-light tracking-tight text-white mb-2">Discover</h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Analytical observations from the earthquake dataset.
        </p>
      </header>

      <div className="space-y-16">
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-medium text-white mb-2">How does building age affect survivability?</h2>
            <p className="text-sm text-[var(--color-text-secondary)] max-w-2xl">
              Analysis reveals a strong correlation between building age and structural failure. Newer buildings (0-10 years) 
              demonstrate significantly higher probability of emerging with only Grade 1 (Low) damage compared to historical structures.
            </p>
          </div>
          
          <div className="h-[300px] bg-[var(--color-bg-panel)] border border-[var(--color-border-subtle)] p-6 rounded">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ageData} layout="vertical" stackOffset="expand">
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="range" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false}
                  tick={{ fill: 'var(--color-text-secondary)', fontSize: 10, fontFamily: 'monospace' }}
                  width={60}
                />
                <Tooltip cursor={{ fill: 'var(--color-bg-elevated)' }} content={<CustomTooltip />} />
                <Bar dataKey="grade1" stackId="a" fill="var(--color-status-safe)" />
                <Bar dataKey="grade2" stackId="a" fill="var(--color-status-warning)" />
                <Bar dataKey="grade3" stackId="a" fill="var(--color-status-critical)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-8 border-t border-[var(--color-border-subtle)] pt-16">
          <div>
            <h2 className="text-xl font-medium text-white mb-4">Structural Vulnerabilities</h2>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              Mud mortar and stone superstructures proved to be the most catastrophic construction type, accounting for the vast majority of Grade 3 total collapse events. Conversely, reinforced concrete (RC) engineered structures survived with predominantly Grade 1 damage.
            </p>
            <div className="space-y-4">
              <div>
                <p className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase mb-1">MUD MORTAR + STONE</p>
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-1 bg-[var(--color-status-critical)]" />
                  <span className="text-xs font-mono text-white">74% GRADE 3</span>
                </div>
              </div>
              <div>
                <p className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase mb-1">RC ENGINEERED</p>
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-1 bg-[var(--color-status-safe)]" />
                  <span className="text-xs font-mono text-white">62% GRADE 1</span>
                </div>
              </div>
            </div>
          </div>
          <div>
            <h2 className="text-xl font-medium text-white mb-4">Feature Importance</h2>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              Geographic location (Geo Level 1) is the single most predictive feature. Proximity to the epicenter overrides almost all structural characteristics. Following geography, building age and footprint area are the strongest secondary indicators.
            </p>
            <ul className="text-xs font-mono space-y-3">
              <li className="flex justify-between border-b border-[var(--color-border-subtle)] pb-1">
                <span className="text-white">1. geo_level_1_id</span>
                <span className="text-[var(--color-text-tertiary)]">PRIMARY</span>
              </li>
              <li className="flex justify-between border-b border-[var(--color-border-subtle)] pb-1">
                <span className="text-white">2. age</span>
                <span className="text-[var(--color-text-tertiary)]">SECONDARY</span>
              </li>
              <li className="flex justify-between border-b border-[var(--color-border-subtle)] pb-1">
                <span className="text-white">3. area_percentage</span>
                <span className="text-[var(--color-text-tertiary)]">SECONDARY</span>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </motion.div>
  );
}
