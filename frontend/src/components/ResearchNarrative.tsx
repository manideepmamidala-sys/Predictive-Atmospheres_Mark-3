import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const ResearchNarrative: React.FC = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="w-full min-h-[50vh] py-24 px-8 border-b border-border flex flex-col md:flex-row gap-12 items-center justify-center">
      <motion.div 
        className="max-w-xl"
        initial={{ opacity: 0, x: -50 }}
        animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -50 }}
        transition={{ duration: 0.8 }}
      >
        <h2 className="text-3xl font-bold mb-4 uppercase tracking-wide">The Static Problem</h2>
        <p className="opacity-80 leading-relaxed mb-6">
          Humans spend 90% of their time indoors, yet architectural spaces are largely designed based on 
          subjective intuition rather than measurable physiological impact. We lack objective metrics for 
          how spatial geometry directly affects human affective states.
        </p>
      </motion.div>

      <motion.div 
        className="max-w-xl"
        initial={{ opacity: 0, x: 50 }}
        animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 50 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <h2 className="text-3xl font-bold mb-4 uppercase tracking-wide">Methodology</h2>
        <p className="opacity-80 leading-relaxed mb-6">
          By mapping Virtual Reality spatial permutations to continuous EEG/ECG biosignal extraction, 
          this platform trains a predictive machine learning model to map geometric parameters into the 
          Circumplex Model of Affect (Valence, Arousal, Dominance).
        </p>
      </motion.div>
    </section>
  );
};

export default ResearchNarrative;
