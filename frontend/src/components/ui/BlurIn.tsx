import { motion } from "framer-motion"; // we will create this util

interface BlurInProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  duration?: number;
  as?: any;
}

export function BlurIn({
  children,
  className,
  delay = 0,
  duration = 0.8,
  as: Component = "div",
}: BlurInProps) {
  const MotionComponent = motion(Component as any);
  
  return (
    <MotionComponent
      initial={{ filter: "blur(10px)", opacity: 0 }}
      animate={{ filter: "blur(0px)", opacity: 1 }}
      transition={{ duration, delay, ease: "easeOut" }}
      className={className}
    >
      {children}
    </MotionComponent>
  );
}
