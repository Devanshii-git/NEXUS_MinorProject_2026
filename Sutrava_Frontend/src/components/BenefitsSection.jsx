import { motion } from 'framer-motion';

const benefits = [
  'Work faster with AI',
  'Turn data into insight',
  'Forecast with confidence',
  'Collaborate with your team',
  'Track your files in one place',
];

export default function BenefitsSection() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-16">
        {/* Left side — benefits list */}
        <div className="flex-1">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="heading-lg mb-10"
          >
            Unlock the benefits
          </motion.h2>

          <div className="space-y-0">
            {benefits.map((benefit, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="py-5 list-separator"
              >
                <p className="text-base" style={{ color: 'var(--text-primary)' }}>
                  {benefit}
                </p>
              </motion.div>
            ))}
          </div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="flex gap-4 mt-10"
          >
            <button className="btn-dark">See process</button>
            <button className="btn-outlined">Complete intake form</button>
          </motion.div>
        </div>

        {/* Right side — decorative 3D-like element */}
        <div className="flex-shrink-0 w-64 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="relative"
          >
            {/* Stacked circles to create a spine/helix-like decorative element */}
            <div className="flex flex-col items-center gap-0">
              {[...Array(12)].map((_, i) => (
                <div
                  key={i}
                  className="rounded-full"
                  style={{
                    width: `${30 + Math.sin(i * 0.5) * 15}px`,
                    height: `${30 + Math.sin(i * 0.5) * 15}px`,
                    background: `linear-gradient(${135 + i * 15}deg, 
                      rgba(200, 180, 230, ${0.4 + i * 0.03}), 
                      rgba(230, 200, 210, ${0.5 + i * 0.02}))`,
                    transform: `translateX(${Math.sin(i * 0.6) * 20}px)`,
                    marginTop: i === 0 ? '0' : '-8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  }}
                />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
