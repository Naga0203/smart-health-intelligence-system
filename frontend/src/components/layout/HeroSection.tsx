import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { BlurIn } from '../ui/BlurIn';
import { SplitText } from '../ui/SplitText';

export const HeroSection: React.FC = () => {
  const navigate = useNavigate();

  return (
    <section className="relative w-full h-screen overflow-hidden bg-transparent flex items-center">
      {/* Background Video (Placeholder for HLS) */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0 ml-[200px] scale-125 opacity-60"
        src="https://cdn.pixabay.com/video/2020/03/19/33869-399335193_large.mp4"
        style={{ pointerEvents: 'none' }}
      />

      {/* Subtle Healthcare Gradient Overlay */}
      <div 
        className="absolute inset-0 z-10"
        style={{
          background: 'radial-gradient(circle at 70% 50%, rgba(14, 165, 233, 0.15) 0%, rgba(139, 92, 246, 0.08) 40%, transparent 80%)'
        }}
        aria-hidden="true"
      />

      {/* Main Content Container */}
      <div className="relative z-20 w-full max-w-7xl mx-auto px-6 lg:px-12 flex flex-col justify-center h-full">
        
        {/* Healthcare Context Badge */}
        <BlurIn delay={0.2} duration={0.8} className="mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/20 backdrop-blur-sm bg-white/5">
            <Activity className="w-4 h-4 text-accent-blue" />
            <span className="text-white/80 text-sm font-medium tracking-wide">
              AI-Powered Health Intelligence
            </span>
          </div>
        </BlurIn>

        {/* Main Heading */}
        <div className="flex flex-col gap-2 mb-6">
          <SplitText
            text="Understand Your Health"
            className="text-4xl md:text-5xl lg:text-6xl font-medium leading-tight text-white"
            delay={0.1}
          />
          <SplitText
            text="Before It Becomes a Problem"
            className="text-4xl md:text-5xl lg:text-6xl font-medium leading-tight text-white"
            delay={0.3}
          />
          <SplitText
            text="with AI."
            className="text-4xl md:text-5xl lg:text-6xl font-medium leading-tight bg-gradient-to-r from-accent-blue to-accent-violet bg-clip-text text-transparent"
            delay={0.5}
          />
        </div>

        {/* Subtitle */}
        <BlurIn delay={1} duration={0.8} className="mb-12 max-w-xl">
          <p className="text-white/80 text-lg leading-relaxed">
            SymptoSense analyzes your symptoms and medical reports to assess potential health risks, explain insights clearly, and guide you through multiple treatment perspectives — without replacing professional medical advice.
          </p>
        </BlurIn>

        {/* CTA Buttons */}
        <BlurIn delay={1.2} duration={0.8} className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => navigate('/app/assessment/new')}
            className="group button-gradient px-8 py-3.5 rounded-xl text-base"
          >
            Analyze Symptoms
          </button>
          
          <button
            onClick={() => {
              const el = document.getElementById('features');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
            className="group button-glass px-8 py-3.5 rounded-xl text-base"
          >
            Explore How It Works
          </button>
        </BlurIn>

      </div>
    </section>
  );
};

export default HeroSection;
