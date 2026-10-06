import { motion } from 'framer-motion';

export default function Overview() {
  const metrics = [
    { label: 'DATASET SCALE', value: '260,601', suffix: ' BLDGS' },
    { label: 'FEATURE COUNT', value: '38', suffix: ' VARS' },
    { label: 'DAMAGE CLASSES', value: '3', suffix: ' GRADES' },
    { label: 'BEST MODEL', value: 'MLP', suffix: ' NETWORK' },
    { label: 'PRIMARY METRIC', value: '0.686', suffix: ' μ-F1' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }}
      className="max-w-5xl"
    >
      <header className="mb-16">
        <h1 className="text-4xl md:text-5xl font-light tracking-tight text-white mb-6">
          Earthquake Building Damage Intelligence
        </h1>
        <p className="text-[var(--color-text-secondary)] text-lg max-w-2xl leading-relaxed">
          QuakeSense is a scientific analytical system predicting seismic vulnerability 
          using the 2015 Nepal Earthquake dataset. It evaluates structural characteristics 
          against multiple machine-learning models to determine damage probability.
        </p>
      </header>

      <section className="mb-16">
        <h2 className="font-mono text-[10px] tracking-widest text-[var(--color-text-tertiary)] uppercase mb-6">System Telemetry</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {metrics.map((m, i) => (
            <motion.div 
              key={m.label}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: i * 0.1, ease: "easeOut" }}
              className="border-t border-[var(--color-border-subtle)] pt-4"
            >
              <div className="text-[10px] font-mono tracking-wider text-[var(--color-text-tertiary)] mb-2">
                {m.label}
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-medium text-white">{m.value}</span>
                <span className="text-[10px] font-mono text-[var(--color-text-tertiary)]">{m.suffix}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 border-t border-[var(--color-border-subtle)] pt-12">
        <div>
          <h3 className="text-sm font-medium text-white mb-4">Architecture</h3>
          <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
            The prediction pipeline incorporates categorical encoding, standard scaling, and 
            is currently powered by a tuned Multi-Layer Perceptron (Neural Network) demonstrating 
            superior multi-class performance over Random Forest and KNN baselines.
          </p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-white mb-4">Objective</h3>
          <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
            To provide precise, data-driven structural damage assessments based on geographic location, 
            construction materials, and building geometry, supporting post-earthquake operational intelligence.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
