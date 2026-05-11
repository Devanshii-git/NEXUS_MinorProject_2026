import { motion } from 'framer-motion';

const steps = [
  { num: 1, title: 'ACCOUNT', subtitle: 'SETUP' },
  { num: 2, title: 'KICKOFF', subtitle: 'CALL' },
  { num: 3, title: 'TRAINING', subtitle: '' },
];

export default function StepsSection() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-4xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="badge mb-8">WHAT'S NEXT?</span>
        </motion.div>

        {/* Step Cards */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
        >
          {steps.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="card-outlined text-center py-10 px-6"
            >
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-5 text-sm font-semibold"
                style={{ border: '1.5px solid var(--border-default)', color: 'var(--text-primary)' }}
              >
                {step.num}
              </div>
              <p className="text-sm font-semibold tracking-wider uppercase" style={{ color: 'var(--text-primary)' }}>
                {step.title}
              </p>
              {step.subtitle && (
                <p className="text-sm font-semibold tracking-wider uppercase" style={{ color: 'var(--text-primary)' }}>
                  {step.subtitle}
                </p>
              )}
            </motion.div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6 }}
          className="mt-10"
        >
          <button className="btn-dark">Get started</button>
        </motion.div>
      </div>
    </section>
  );
}
