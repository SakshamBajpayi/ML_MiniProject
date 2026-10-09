import { motion } from 'framer-motion';

export default function Models() {
  const models = [
    {
      id: 'xgb',
      name: 'XGBoost',
      type: 'Our Extension',
      f1: 0.747, 
      accuracy: 0.747, 
      status: 'active',
      strengths: ['Handles non-linear relationships', 'Gradient boosting efficiency', 'Robust tuning', 'Lower Overfitting'],
      limitations: ['Black-box nature', 'Hyperparameter sensitive']
    },
    {
      id: 'rf',
      name: 'Random Forest',
      type: 'Reference Baseline',
      f1: 0.683,
      accuracy: 0.683,
      status: 'standby',
      strengths: ['Robust to outliers', 'Feature importance extraction', 'No scaling required'],
      limitations: ['Large disk size (~660MB)', 'Slower inference at depth', 'High Overfitting']
    },
    {
      id: 'mlp',
      name: 'Multi-Layer Perceptron',
      type: 'Reference Baseline',
      f1: 0.686,
      accuracy: 0.686,
      status: 'standby',
      strengths: ['High dimensional pattern recognition', 'Non-linear relationships', 'Probabilistic outputs'],
      limitations: ['Opaque decision boundary', 'Compute intensive training']
    },
    {
      id: 'knn',
      name: 'K-Nearest Neighbors',
      type: 'Reference Baseline',
      f1: 0.667,
      accuracy: 0.667,
      status: 'archived',
      strengths: ['Simple conceptual model', 'No strict assumptions'],
      limitations: ['Extremely slow inference (O(N))', 'Curse of dimensionality']
    }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-6xl"
    >
      <header className="mb-12">
        <h1 className="text-3xl font-light tracking-tight text-white mb-2">Model Architecture</h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Comparative analysis of tested machine learning architectures.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        {models.map((model, i) => (
          <motion.div 
            key={model.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className={`p-6 border ${model.status === 'active' ? 'border-[var(--color-brand)] shadow-[0_0_15px_rgba(10,132,255,0.15)] bg-[var(--color-bg-panel)]' : 'border-[var(--color-border-subtle)] bg-transparent'} rounded flex flex-col h-full`}
          >
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className={`text-lg font-medium mb-1 ${model.status === 'active' ? 'text-white' : 'text-[var(--color-text-secondary)]'}`}>
                  {model.name}
                </h3>
                <p className={`text-[10px] font-mono uppercase tracking-widest ${model.id === 'xgb' ? 'text-[var(--color-brand)] font-bold' : 'text-[var(--color-text-tertiary)]'}`}>
                  {model.type}
                </p>
              </div>
              {model.status === 'active' && (
                <span className="px-2 py-1 text-[9px] font-mono bg-[var(--color-brand)] text-white tracking-widest uppercase rounded-sm">
                  Active
                </span>
              )}
            </div>

            <div className="mb-8 space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1 font-mono">
                  <span className="text-[var(--color-text-tertiary)]">MICRO-F1</span>
                  <span className="text-white">{model.f1.toFixed(3)}</span>
                </div>
                <div className="h-1 bg-[var(--color-bg-base)] overflow-hidden">
                  <div 
                    className={`h-full ${model.status === 'active' ? 'bg-[var(--color-brand)]' : 'bg-[var(--color-text-tertiary)]'}`} 
                    style={{ width: `${model.f1 * 100}%` }} 
                  />
                </div>
              </div>
            </div>

            <div className="mt-auto space-y-4">
              <div>
                <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-tertiary)] mb-2">STRENGTHS</p>
                <ul className="text-xs text-[var(--color-text-secondary)] space-y-1">
                  {model.strengths.map(s => <li key={s} className="flex gap-2"><span className="text-white opacity-50">+</span> {s}</li>)}
                </ul>
              </div>
              <div>
                <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-tertiary)] mb-2">LIMITATIONS</p>
                <ul className="text-xs text-[var(--color-text-secondary)] space-y-1">
                  {model.limitations.map(s => <li key={s} className="flex gap-2"><span className="text-white opacity-50">-</span> {s}</li>)}
                </ul>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      <section className="border-t border-[var(--color-border-subtle)] pt-12">
        <h2 className="text-sm font-medium text-white mb-6">XGBoost Decision Flow (Our Extension)</h2>
        <div className="bg-[var(--color-bg-panel)] border border-[var(--color-border-subtle)] p-8 rounded flex items-center justify-center min-h-[200px]">
          <div className="flex items-center gap-4 md:gap-12 font-mono text-[10px] tracking-widest text-[var(--color-text-secondary)]">
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded border border-[var(--color-border-strong)] flex items-center justify-center bg-[var(--color-bg-base)]">38</div>
              <span>INPUTS</span>
            </div>
            <div className="h-[1px] w-8 md:w-16 bg-[var(--color-border-strong)]" />
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded border border-[var(--color-brand)] flex items-center justify-center bg-[var(--color-bg-base)] text-white">400</div>
              <span>TREES</span>
            </div>
            <div className="h-[1px] w-8 md:w-16 bg-[var(--color-border-strong)]" />
            <div className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded border border-white flex items-center justify-center bg-[var(--color-brand)] text-white font-bold">3</div>
              <span>OUTPUTS</span>
            </div>
          </div>
        </div>
      </section>
    </motion.div>
  );
}
