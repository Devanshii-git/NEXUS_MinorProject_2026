import { motion } from 'framer-motion';

export default function Footer() {
  return (
    <footer>
      {/* Contact info row */}
      <div className="px-6 py-10 border-t" style={{ borderColor: 'var(--border-light)' }}>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              Tel: 123-456-789
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              Email: hello@sutrava.com
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              Social: @sutrava
            </p>
          </div>
          <div>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              UPES, Bidholi Campus
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              Dehradun, Uttarakhand 248007
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
              India
            </p>
          </div>
          <div>
            <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              We're committed to an accessible onboarding experience for all. Let us know how we can support you.
            </p>
          </div>
        </div>
      </div>

      {/* Innovation Hub — large text bottom section */}
      <div
        className="relative overflow-hidden py-20 px-6"
        style={{
          background: 'linear-gradient(180deg, var(--bg-primary), #fce8d8, #f5d5c8)',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto"
        >
          <h2
            className="font-display font-bold leading-none"
            style={{
              fontSize: 'clamp(4rem, 12vw, 10rem)',
              color: 'var(--text-primary)',
              letterSpacing: '-0.03em',
            }}
          >
            Innovation Hub
          </h2>
        </motion.div>
      </div>
    </footer>
  );
}
