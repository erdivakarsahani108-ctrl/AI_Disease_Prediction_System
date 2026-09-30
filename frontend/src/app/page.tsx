import Link from "next/link";

const FEATURES = [
  { title: "Disease Prediction", desc: "Hybrid ML + rules · 40+ conditions · confidence scores", icon: "🧬", href: "/predict" },
  { title: "Multilingual Chat", desc: "English · Hindi · Hinglish · Bhojpuri · safety-gated", icon: "💬", href: "/chat" },
  { title: "Nutrition Engine", desc: "BMI · BMR · TDEE · macros · disease-aware tips", icon: "🥗", href: "/nutrition" },
  { title: "Safety Pipeline", desc: "Emergency detection · risk levels · mandatory disclaimers", icon: "🛡️", href: "/predict" },
  { title: "Knowledge RAG", desc: "Cited educational retrieval across medical systems", icon: "📚", href: "/chat" },
  { title: "Voice Scan", desc: "Mic consent · speech-to-text · safety + prediction", icon: "🎤", href: "/voice" },
  { title: "Dashboard", desc: "History · stats · persistent profile after login", icon: "📊", href: "/dashboard" },
];

export default function HomePage() {
  return (
    <div className="space-y-14">
      {/* Hero with 3D/4D rings */}
      <section className="relative min-h-[380px] flex items-center justify-center text-center py-12">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40">
          <div className="ring-4d" />
          <div className="ring-4d-inner" />
        </div>

        <div className="relative z-10 space-y-5 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/15 text-cyan-300 border border-cyan-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            Educational AI · Not clinical diagnosis
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight text-white hero-glow">
            AI Disease Prediction
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-300 to-violet-400 mt-1">
              System
            </span>
          </h2>
          <p className="text-slate-300 text-lg leading-relaxed">
            Symptom intelligence · multilingual medical assistant · nutrition science —
            wrapped in a cinematic 3D interface.
          </p>
          <div className="flex flex-wrap justify-center gap-3 pt-2">
            <Link href="/predict" className="btn-primary">
              Start Prediction
            </Link>
            <Link href="/chat" className="btn-secondary">
              Open Chatbot
            </Link>
          </div>
        </div>
      </section>

      {/* 3D Feature grid */}
      <section className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {FEATURES.map((f) => (
          <Link key={f.title} href={f.href} className="card-3d block group">
            <div className="icon-3d mb-4">{f.icon}</div>
            <h3 className="font-semibold text-white mb-1 group-hover:text-cyan-300 transition-colors">
              {f.title}
            </h3>
            <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
          </Link>
        ))}
      </section>

      {/* Pipeline visual */}
      <section className="card-3d">
        <h3 className="text-xl font-semibold text-white mb-4">Safety pipeline</h3>
        <div className="flex flex-wrap gap-2 text-xs sm:text-sm">
          {[
            "Validate",
            "Emergency",
            "Intent",
            "Language",
            "Retrieve",
            "Safety",
            "Cite",
            "Respond",
          ].map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <span className="px-3 py-1.5 rounded-lg bg-blue-500/20 border border-blue-400/30 text-cyan-200 font-medium">
                {step}
              </span>
              {i < 7 && <span className="text-slate-600">→</span>}
            </div>
          ))}
        </div>
      </section>

      {/* SVG medical illustration */}
      <section className="card-3d flex flex-col sm:flex-row items-center gap-8">
        <svg viewBox="0 0 200 200" className="w-40 h-40 shrink-0" aria-hidden>
          <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          {/* DNA-ish double helix simplified */}
          <ellipse cx="100" cy="100" rx="70" ry="30" fill="none" stroke="url(#g1)" strokeWidth="2" opacity="0.4" transform="rotate(-20 100 100)" />
          <ellipse cx="100" cy="100" rx="70" ry="30" fill="none" stroke="url(#g1)" strokeWidth="2" opacity="0.6" transform="rotate(20 100 100)" />
          <circle cx="100" cy="100" r="28" fill="url(#g1)" filter="url(#glow)" opacity="0.9" />
          <text x="100" y="106" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">AI</text>
          {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => {
            const rad = (a * Math.PI) / 180;
            const x = 100 + Math.cos(rad) * 55;
            const y = 100 + Math.sin(rad) * 55;
            return <circle key={a} cx={x} cy={y} r="4" fill="#06b6d4" opacity="0.8" />;
          })}
        </svg>
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">Built for learning & research</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Persistent auth, prediction history, structured disease knowledge (red flags, specialists),
            train/test ML metrics, and a cinematic interface — without claiming clinical authority.
          </p>
        </div>
      </section>
    </div>
  );
}
