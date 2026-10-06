import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldCheck, Target, Hexagon } from 'lucide-react';

const API_URL = 'http://localhost:8000/api/predict';

export default function Predict() {
  const [inputs, setInputs] = useState({
    geo_level_1_id: 10,
    count_floors_pre_eq: 2,
    age: 15,
    area_percentage: 5,
    height_percentage: 5,
    foundation_type: 'r',
    roof_type: 'n',
    has_superstructure_mud_mortar_stone: 1,
    has_superstructure_cement_mortar_brick: 0,
    has_superstructure_rc_engineered: 0,
  });

  const [status, setStatus] = useState('idle'); // idle, processing, complete, error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handlePredict = async () => {
    setStatus('processing');
    setResult(null);
    setErrorMsg('');
    
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });
      
      if (!response.ok) throw new Error('Inference API unavailable or failed.');
      
      const data = await response.json();
      
      // Simulate a brief deliberate delay for the "processing" feel
      setTimeout(() => {
        setResult(data.data);
        setStatus('complete');
      }, 600);
      
    } catch (err) {
      setErrorMsg(err.message);
      setStatus('error');
    }
  };

  const getStatusColor = (grade) => {
    if (grade === 1) return 'text-[var(--color-status-safe)]';
    if (grade === 2) return 'text-[var(--color-status-warning)]';
    if (grade === 3) return 'text-[var(--color-status-critical)]';
    return 'text-white';
  };
  
  const getStatusBg = (grade) => {
    if (grade === 1) return 'bg-[var(--color-status-safe)]';
    if (grade === 2) return 'bg-[var(--color-status-warning)]';
    if (grade === 3) return 'bg-[var(--color-status-critical)]';
    return 'bg-white';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
      
      {/* Input Form Panel */}
      <div className="lg:col-span-5 space-y-8">
        <header className="mb-8">
          <h1 className="text-3xl font-light tracking-tight text-white mb-2">Assess Building</h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Input structural characteristics to run inference.
          </p>
        </header>

        {/* Section: Geography */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-2">
            <Target className="w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
            <h3 className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase">Geography</h3>
          </div>
          <div>
            <label className="flex justify-between text-xs text-[var(--color-text-secondary)] mb-2">
              <span>Geo Level 1 Sector</span>
              <span className="font-mono text-white">{inputs.geo_level_1_id}</span>
            </label>
            <input type="range" min="0" max="30" value={inputs.geo_level_1_id} 
              onChange={(e) => setInputs({...inputs, geo_level_1_id: parseInt(e.target.value)})} 
              className="w-full accent-white" 
            />
          </div>
        </section>

        {/* Section: Dimensions */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-2">
            <Hexagon className="w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
            <h3 className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase">Dimensions</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[var(--color-bg-panel)] p-3 border border-[var(--color-border-subtle)] rounded">
              <label className="block text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] mb-1">FLOORS</label>
              <input type="number" value={inputs.count_floors_pre_eq} 
                onChange={(e) => setInputs({...inputs, count_floors_pre_eq: parseInt(e.target.value) || 0})}
                className="w-full bg-transparent text-white font-mono outline-none" />
            </div>
            <div className="bg-[var(--color-bg-panel)] p-3 border border-[var(--color-border-subtle)] rounded">
              <label className="block text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] mb-1">AGE (YRS)</label>
              <input type="number" value={inputs.age} 
                onChange={(e) => setInputs({...inputs, age: parseInt(e.target.value) || 0})}
                className="w-full bg-transparent text-white font-mono outline-none" />
            </div>
          </div>
        </section>

        {/* Section: Materials */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 border-b border-[var(--color-border-subtle)] pb-2">
            <ShieldCheck className="w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
            <h3 className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase">Composition</h3>
          </div>
          
          <div>
            <label className="block text-xs text-[var(--color-text-secondary)] mb-2">Foundation Array</label>
            <select 
              value={inputs.foundation_type} 
              onChange={(e) => setInputs({...inputs, foundation_type: e.target.value})}
              className="w-full bg-[var(--color-bg-panel)] border border-[var(--color-border-subtle)] text-white text-sm p-2 rounded focus:border-white focus:outline-none"
            >
              <option value="h">H-Type</option>
              <option value="i">I-Type</option>
              <option value="r">R-Type (Standard)</option>
              <option value="u">U-Type</option>
              <option value="w">W-Type</option>
            </select>
          </div>

          <div className="space-y-3 pt-2">
            <label className="block text-xs text-[var(--color-text-secondary)]">Superstructure Material</label>
            {[
              { key: 'has_superstructure_mud_mortar_stone', label: 'Mud Mortar / Stone' },
              { key: 'has_superstructure_cement_mortar_brick', label: 'Cement Mortar / Brick' },
              { key: 'has_superstructure_rc_engineered', label: 'Reinforced Concrete' }
            ].map((mat) => (
              <label key={mat.key} className="flex items-center gap-3 cursor-pointer group">
                <div className={`w-4 h-4 border flex items-center justify-center rounded-sm transition-colors ${inputs[mat.key] ? 'bg-white border-white' : 'border-[var(--color-border-strong)] bg-transparent'}`}>
                  {inputs[mat.key] ? <div className="w-2 h-2 bg-black rounded-sm" /> : null}
                </div>
                <input 
                  type="checkbox" 
                  className="hidden"
                  checked={inputs[mat.key] === 1}
                  onChange={(e) => setInputs({...inputs, [mat.key]: e.target.checked ? 1 : 0})}
                />
                <span className="text-sm text-[var(--color-text-secondary)] group-hover:text-white transition-colors">{mat.label}</span>
              </label>
            ))}
          </div>
        </section>

        <button 
          onClick={handlePredict}
          disabled={status === 'processing'}
          className="w-full py-3 mt-4 bg-white text-black font-medium text-sm transition-all hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
        >
          {status === 'processing' ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
              <Activity className="w-4 h-4" />
            </motion.div>
          ) : "RUN INFERENCE"}
        </button>
        
        {status === 'error' && (
          <div className="text-xs text-[var(--color-status-critical)] font-mono bg-red-950/20 p-3 border border-red-900/50 rounded">
            ERR: {errorMsg}
          </div>
        )}
      </div>

      {/* Output Panel */}
      <div className="lg:col-span-7">
        <div className="h-full min-h-[500px] border border-[var(--color-border-subtle)] bg-[var(--color-bg-panel)] rounded p-8 relative overflow-hidden flex flex-col justify-center">
          
          <AnimatePresence mode="wait">
            {status === 'idle' && (
              <motion.div 
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center"
              >
                <div className="w-12 h-12 border border-[var(--color-border-strong)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <Activity className="w-5 h-5 text-[var(--color-text-tertiary)]" />
                </div>
                <p className="font-mono text-xs text-[var(--color-text-tertiary)] tracking-widest uppercase">
                  Awaiting Pipeline Input
                </p>
              </motion.div>
            )}

            {status === 'processing' && (
              <motion.div 
                key="processing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center space-y-6"
              >
                <div className="flex justify-center gap-2">
                  {[0,1,2].map(i => (
                    <motion.div 
                      key={i}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                      className="w-2 h-2 bg-white rounded-full"
                    />
                  ))}
                </div>
                <div className="font-mono text-[10px] text-[var(--color-text-secondary)] tracking-widest uppercase space-y-2">
                  <p>Initializing Tensor Vector...</p>
                  <p className="text-[var(--color-text-tertiary)]">Scaling parameters</p>
                  <p className="text-[var(--color-text-tertiary)]">Forward pass in progress</p>
                </div>
              </motion.div>
            )}

            {status === 'complete' && result && (
              <motion.div 
                key="complete"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="w-full"
              >
                <div className="mb-10">
                  <p className="font-mono text-[10px] tracking-widest text-[var(--color-text-tertiary)] uppercase mb-3">
                    PREDICTED DAMAGE
                  </p>
                  <div className="flex items-baseline gap-4 mb-2">
                    <h2 className={`text-6xl font-light tracking-tight ${getStatusColor(result.damage_grade)}`}>
                      0{result.damage_grade}
                    </h2>
                    <span className="text-2xl font-light text-white tracking-wide">
                      {result.interpretation.toUpperCase()}
                    </span>
                  </div>
                </div>

                {result.probabilities && (
                  <div className="space-y-6">
                    <p className="font-mono text-[10px] tracking-widest text-[var(--color-text-tertiary)] uppercase border-b border-[var(--color-border-subtle)] pb-2">
                      PROBABILITY DISTRIBUTION
                    </p>
                    
                    <div className="space-y-4">
                      {[1, 2, 3].map(grade => {
                        const probKey = `Grade ${grade}`;
                        const prob = result.probabilities[probKey] || result.probabilities[probKey.toLowerCase()] || result.probabilities[grade.toString()] || 0;
                        const pct = prob * 100;
                        const isMax = grade === result.damage_grade;
                        
                        return (
                          <div key={grade} className="relative">
                            <div className="flex justify-between text-[10px] font-mono tracking-widest mb-1.5 z-10 relative">
                              <span className={isMax ? 'text-white font-medium' : 'text-[var(--color-text-secondary)]'}>GRADE 0{grade}</span>
                              <span className={isMax ? 'text-white' : 'text-[var(--color-text-tertiary)]'}>{pct.toFixed(1)}%</span>
                            </div>
                            <div className="h-1 bg-[var(--color-bg-base)] rounded-full overflow-hidden">
                              <motion.div 
                                initial={{ width: 0 }}
                                animate={{ width: `${pct}%` }}
                                transition={{ duration: 0.8, delay: 0.2 + (grade * 0.1), ease: [0.2, 0.8, 0.2, 1] }}
                                className={`h-full ${isMax ? getStatusBg(grade) : 'bg-[var(--color-border-strong)]'}`}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                
                <div className="mt-10 border-t border-[var(--color-border-subtle)] pt-6 grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase mb-1">ACTIVE MODEL</p>
                    <p className="text-xs text-white">Multi-Layer Perceptron</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-mono tracking-widest text-[var(--color-text-tertiary)] uppercase mb-1">INFERENCE TIME</p>
                    <p className="text-xs text-white">~45ms</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
        </div>
      </div>
    </div>
  );
}
