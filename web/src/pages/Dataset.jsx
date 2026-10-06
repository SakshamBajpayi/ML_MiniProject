import { motion } from 'framer-motion';

export default function Dataset() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl"
    >
      <header className="mb-12">
        <h1 className="text-3xl font-light tracking-tight text-white mb-2">Dataset Telemetry</h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          2015 Gorkha Earthquake structural damage assessment data.
        </p>
      </header>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
        {[
          { label: 'RECORDS', value: '260,601' },
          { label: 'FEATURES', value: '38' },
          { label: 'MISSING VALUES', value: '0' },
          { label: 'GEO REGIONS', value: '30' }
        ].map((stat) => (
          <div key={stat.label} className="border-t border-[var(--color-border-subtle)] pt-4">
            <p className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase mb-1">{stat.label}</p>
            <p className="text-xl font-medium text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="space-y-12">
        <section>
          <h2 className="text-sm font-medium text-white mb-6">Class Distribution (Imbalanced)</h2>
          <div className="space-y-4 max-w-2xl">
            {[
              { grade: 1, desc: 'Low Damage', pct: 9.6, color: 'bg-[var(--color-status-safe)]' },
              { grade: 2, desc: 'Medium Damage', pct: 56.9, color: 'bg-[var(--color-status-warning)]' },
              { grade: 3, desc: 'Complete Destruction', pct: 33.5, color: 'bg-[var(--color-status-critical)]' }
            ].map((c) => (
              <div key={c.grade}>
                <div className="flex justify-between text-xs font-mono mb-2">
                  <span className="text-[var(--color-text-secondary)]">GRADE 0{c.grade} <span className="text-[var(--color-text-tertiary)] ml-2">{c.desc}</span></span>
                  <span className="text-white">{c.pct}%</span>
                </div>
                <div className="h-1 bg-[var(--color-bg-panel)] overflow-hidden">
                  <div className={`h-full ${c.color}`} style={{ width: `${c.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
          <p className="mt-6 text-xs text-[var(--color-text-secondary)] max-w-2xl leading-relaxed">
            The dataset exhibits significant class imbalance. Grade 2 (Medium Damage) constitutes the majority class. 
            The machine learning models utilize balanced class weights during training to prevent majority-class bias.
          </p>
        </section>

        <section className="border-t border-[var(--color-border-subtle)] pt-12">
          <h2 className="text-sm font-medium text-white mb-6">Feature Taxonomy</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xs font-mono text-[var(--color-text-tertiary)] tracking-widest uppercase mb-4">Categorical / Binary (30)</h3>
              <ul className="text-xs text-[var(--color-text-secondary)] space-y-2 font-mono">
                <li>foundation_type</li>
                <li>roof_type</li>
                <li>ground_floor_type</li>
                <li>other_floor_type</li>
                <li>position</li>
                <li>plan_configuration</li>
                <li>has_superstructure_* (11 binary flags)</li>
                <li>has_secondary_use_* (10 binary flags)</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-mono text-[var(--color-text-tertiary)] tracking-widest uppercase mb-4">Numerical (8)</h3>
              <ul className="text-xs text-[var(--color-text-secondary)] space-y-2 font-mono">
                <li>geo_level_1_id</li>
                <li>geo_level_2_id</li>
                <li>geo_level_3_id</li>
                <li>count_floors_pre_eq</li>
                <li>age</li>
                <li>area_percentage</li>
                <li>height_percentage</li>
                <li>count_families</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </motion.div>
  );
}
