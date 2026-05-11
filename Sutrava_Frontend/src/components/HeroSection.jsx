import { motion } from 'framer-motion';

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden" style={{ minHeight: '85vh' }}>
      {/* Iridescent gradient background */}
      <div className="absolute inset-0 hero-gradient opacity-60" />
      
      {/* Decorative blobs */}
      <div className="absolute top-10 left-1/4 w-64 h-64 iridescent-blob opacity-40 animate-float" />
      <div className="absolute bottom-20 right-1/4 w-48 h-48 iridescent-blob opacity-30" 
           style={{ animationDelay: '2s', animation: 'float 8s ease-in-out infinite' }} />
      <div className="absolute top-1/3 right-1/6 w-32 h-32 iridescent-blob opacity-25"
           style={{ animationDelay: '4s', animation: 'float 7s ease-in-out infinite' }} />

      {/* Wavy iridescent ribbons (CSS-based) */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="relative w-full h-full max-w-3xl">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full"
              style={{
                width: `${200 + i * 60}px`,
                height: `${30 + i * 8}px`,
                top: `${20 + i * 8}%`,
                left: `${10 + i * 10}%`,
                background: `linear-gradient(${90 + i * 30}deg, 
                  rgba(200,180,255,${0.3 - i * 0.04}), 
                  rgba(255,200,180,${0.3 - i * 0.04}), 
                  rgba(180,230,255,${0.3 - i * 0.04}))`,
                transform: `rotate(${-15 + i * 8}deg)`,
                filter: 'blur(1px)',
                animation: `float ${5 + i}s ease-in-out infinite`,
                animationDelay: `${i * 0.5}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-[85vh] px-6">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <span className="badge mb-8">YOUR NEW TOOLKIT</span>
        </motion.div>

        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-center"
        >
          <h1 className="heading-xl max-w-3xl mx-auto">
            All-in-one platform
            <br />
            Intuitive program
            <br />
            Customized to your needs
          </h1>
        </motion.div>
      </div>
    </section>
  );
}
