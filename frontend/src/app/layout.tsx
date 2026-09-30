import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Disease Prediction System",
  description: "Educational AI platform — disease prediction, nutrition, multilingual chatbot with 3D interface.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen scene-3d">
        {/* Ambient orbs */}
        <div className="orb orb-1" aria-hidden />
        <div className="orb orb-2" aria-hidden />
        <div className="orb orb-3" aria-hidden />

        {/* Rising particles */}
        <div className="particles" aria-hidden>
          {Array.from({ length: 20 }).map((_, i) => (
            <span
              key={i}
              className="particle"
              style={{
                left: `${(i * 5 + 3) % 100}%`,
                animationDelay: `${i * 0.7}s`,
                animationDuration: `${12 + (i % 5)}s`,
              }}
            />
          ))}
        </div>

        <header className="nav-glass sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="flex items-center gap-3 group">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-lg"
                style={{
                  background: "linear-gradient(135deg, #2563eb, #06b6d4)",
                  boxShadow: "0 4px 20px rgba(37,99,235,0.5)",
                  transform: "perspective(200px) rotateY(-8deg)",
                }}
              >
                AI
              </div>
              <div>
                <h1 className="font-semibold text-white leading-tight text-sm sm:text-base group-hover:text-cyan-300 transition-colors">
                  Disease Prediction
                </h1>
                <p className="text-xs text-slate-400">v3 · 3D UI · Educational</p>
              </div>
            </a>
            <nav className="flex items-center gap-1 sm:gap-3 text-xs sm:text-sm text-slate-300 flex-wrap justify-end">
              {[
                ["Predict", "/predict"],
                ["Voice", "/voice"],
                ["Chat", "/chat"],
                ["Nutrition", "/nutrition"],
                ["Dashboard", "/dashboard"],
                ["Login", "/login"],
              ].map(([label, href]) => (
                <a
                  key={href}
                  href={href}
                  className="px-2.5 py-1.5 rounded-lg hover:bg-white/5 hover:text-cyan-300 transition-colors"
                >
                  {label}
                </a>
              ))}
            </nav>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 py-8 relative z-10">{children}</main>

        <footer className="border-t border-white/5 mt-16 relative z-10">
          <div className="max-w-6xl mx-auto px-4 py-6 text-center text-sm text-slate-400">
            <p className="font-medium text-amber-400/90 mb-1">⚠️ Medical Disclaimer</p>
            <p>
              Educational use only. Not a diagnosis tool. Always consult a qualified clinician.
              Emergencies → call local emergency services.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
